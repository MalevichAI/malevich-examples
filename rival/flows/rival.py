import os
import pandas as pd
from malevich.scrape import scrape_web
from malevich.openai import prompt_completion, structured_prompt_completion
from malevich.utility import rename, merge_three, locs
from malevich import flow, collection, config
from malevich.interpreter.core import CoreInterpreter
from malevich.interpreter.space import SpaceInterpreter


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
    data: pd.DataFrame,
    clear_prompt: str,
    decide_prompt: str,
    goal_prompt: str
):
    """Analyzes demands using a power of LLM models"""
    
    queries_collection = collection(
        df=data,
        name="Search Queries"
    )
    
    links = scrape_web(
        queries_collection,
        config(
            max_results=10,
            max_depth=2,
            timeout=5,
            spider='google',
            spider_cfg=config(
                scrape_api_key=...,
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
    
    cleaned = prompt_completion(
        rename(scraped, config(result="company_info")),
        config(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            user_prompt=clear_prompt,
            model='gpt-4'
        )
    )
        
    
    results = prompt_completion(
        rename(cleaned, config(content="lead_description")),
        config(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            user_prompt=decide_prompt,
            model='gpt-4'
        )
    )
    
    return results

if __name__ == '__main__':
    interpreter = SpaceInterpreter()
    interpreter.supports_subtrees = False
    f = rival(
        pd.read_csv('./datasets/goals.csv'),
        open('prompts/explain.txt').read(),
        open('prompts/decide.txt').read(),
        open('prompts/goal.txt').read()
    )
    
    f.interpret(interpreter)
    print("\n\nFlow is updated!!")