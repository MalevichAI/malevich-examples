import os
from malevich.scrape import scrape_web
from malevich import flow, collection, config
from malevich.interpreter.core import CoreInterpreter
from malevich.utility import merge_two, merge_three, rename
from malevich.openai import prompt_completion, completion_with_vision, text_to_image
import pandas as pd

def _collection(df: pd.DataFrame | str, name: str):
    if isinstance(df, pd.DataFrame):
        return rename(collection(
            df=df,
            name=name
        ))
    elif isinstance(df, str):
        return rename(collection(
            file=df,
            name=name
        ))
    else:
        return df

# @flow(reverse_id='economist.get_text')
def get_econ_text(links: pd.DataFrame | str):
    links = _collection(links, 'Economist Links')
    
    text = scrape_web(
        links,
        config(
            spider='xpath',
            links_are_independent=True,
            # max_results=0,
            spider_cfg={
                'components': [{
                    'key': 'image',
                    'xpath': "//p[@data-component='paragraph']//text()",
                    'include_keys': False,
                }],
                'output_type': 'text'
            }
        )
    )
    
    images = scrape_web(
        links,
        config(
            spider='xpath',
            links_are_independent=True,
            max_results=1,
            spider_cfg={
                'components': [{
                    'key': 'paragraph',
                    'xpath': "(//img[@data-nimg='1']/@src)[1]",
                }],
                'output_type': 'text'
            }
        )
    )
    
    return text, images
    
    
# @flow(reverse_id='economist.analyze_text')
def analyze_text(text: pd.DataFrame | str):
    text = _collection(text, 'Economist Text') 

        
    analyzed = prompt_completion(
        rename(text, config(result='text')),
        config(
            user_prompt=open('prompts/ethics.txt').read(),
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            model='gpt-4' 
        )
    )
    
    return rename(analyzed, config(content='text_report'))


# @flow(reverse_id='economist.analyze_image')
def analyze_image(images: pd.DataFrame | str):
    images = _collection(images, 'Economist Images')
        
    analyzed = completion_with_vision(
        images,
        config(
            user_prompt='What is the image about?',
            openai_api_key=os.getenv('OPENAI_API_KEY'), 
            image_column='result'
        )
    )
    
    return rename(analyzed, config(content='image_report'))

# @flow(reverse_id='economist.new_image')
def new_image(text: pd.DataFrame | str, text_report: pd.DataFrame | str, image_report: pd.DataFrame | str):
    text = _collection(text, 'Economist Text')
    text_report = _collection(text_report, 'Economist Text Report')
    image_report = _collection(image_report, 'Economist Image Report')
    
    variables = merge_three(
        rename(text, config(result='raw_text')),
        text_report,
        image_report
    )

    images = text_to_image(
        variables,
        config(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            user_prompt=open('prompts/new_image.txt').read(),
            model='dall-e-3'
        )
    )
    
    return images

@flow(reverse_id='economist.editorial')
def editorial(links):
    links = _collection(links, 'Economist Links')
    
    text, images = get_econ_text(links)
    text_report = analyze_text(text)
    image_report = analyze_image(images)
    new_images = new_image(text, text_report, image_report)
    
    return merge_three(
        text,
        images,
        new_images,
        config(both_on='index', how='inner')
    )
   

task = editorial(
    pd.DataFrame({
        'link': ['https://www.economist.com/briefing/2023/12/14/brexit-hah-lockdowns-shrug-can-nothing-stop-london']
    })
)

task.interpret()
task.prepare(with_logs=True)
task.run(with_logs=True, profile_mode='all')
task.stop()
results = task.results()[0]

if isinstance(results, pd.DataFrame):
    results.to_csv('economist.csv')
else:
    for i, result in enumerate(results):
        result.to_csv(f'economist_{i}.csv')
        
        