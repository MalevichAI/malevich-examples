import os
import pandas as pd
from malevich.scrape import scrape_web
from malevich.openai import prompt_completion, structured_prompt_completion
from malevich.utility import rename, merge_two, merge_three
from malevich import flow, collection, config
from malevich.interpreter.space import SpaceInterpreter
from malevich.interpreter.core import CoreInterpreter

@flow(
    reverse_id='rival-get-queries',
    name="Get Queries",
)
def get_queries(
    goals_collection,
    goal_prompt: str
):
    """Gets queries for LLM"""
    

    return structured_prompt_completion(
        rename(goals_collection, config(goal="goal")),
        config(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            user_prompt=goal_prompt,
            model='gpt-4',
            fields=[
                {
                    'name': 'query',
                    'description': 'A search engine query that will make me achieve the goal',
                    'type': 'list[str]'
                }
            ]
        )
    )

@flow(
    reverse_id='rival-llm-analysis-v2', 
    name="LLM Demand Analysis",
)
def rival(
    queries: pd.DataFrame = pd.read_csv('./datasets/queries.csv'),
    company: pd.DataFrame =  pd.read_csv('./datasets/company.csv'),
    clear_prompt: str = open('prompts/explain.txt').read(),
    decide_prompt: str = open('prompts/decide.txt').read(),
):
    """Analyzes demands using a power of LLM models"""
    
    queries_collection = collection(
        df=queries,
        name="Google Engine Search Queries v2"
    )
    
    links = scrape_web(
        queries_collection,
        config(
            max_results=10,
            max_depth=1,
            timeout=50,
            spider='google',
            spider_cfg=config(
                scrape_api_key="00ca37449592cc3e41cb5c1e4094ff83",
            )
        )
    
    )
    
    scraped = scrape_web(
        links,
        config(
            links_are_independent=True,
            spider_cfg=config(
                min_text_length=10,
                max_text_length=500
            ),
            max_results=10,
            max_depth=5,
            timeout=5
        )
    )
    
    company = rename(collection(
        df=company,
        name="My Company Information v2"
    ))
    
    scraped_with_company = merge_two(
        scraped,
        company,
        config(how='cross')
    )
    
    cleaned = prompt_completion(
        rename(scraped_with_company, config(result="partner_info")),
        config(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            user_prompt=clear_prompt,
            model='gpt-3.5-turbo',
            max_tokens=128,
        )
    )
        
    cleaned_with_company = merge_two(
        cleaned,
        company,
        config(how='cross')
    )
    
    
    results = structured_prompt_completion(
        rename(cleaned_with_company, config(content="lead_description")),
        config(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            user_prompt=decide_prompt,
            model='gpt-3.5-turbo',
            fields=[
                {'name': 'decision', 'description': 'Desicion about the company. One of "valuable", "neutral", "not valuable", "impossible to decide"', 'type': 'str'},
            ],
            max_tokens=256,
        )
    )
    
    return merge_three(
        cleaned,
        results,
        links,
        config(both_on='index', how='inner')
    )
    

if __name__ == '__main__':
    interpreter = SpaceInterpreter()
    

    f = rival(
        pd.read_csv('./datasets/queries.csv'),
        pd.read_csv('./datasets/company.csv'),
        open('prompts/explain.txt').read(),
        open('prompts/decide.txt').read(),
    )
    
    f.interpret(interpreter)
    print("\n\nFlow is updated!!")
    f.prepare()
    f.run(with_logs=True, profile_mode='all')
    f.stop()
    results = f.results()
    if isinstance(results, pd.DataFrame):
        results.to_csv('results.csv')
    else:
        for i, r in enumerate(results):
            r.to_csv(f'results_{i}.csv')
