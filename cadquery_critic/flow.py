import os

from malevich.utility import merge, locs, get_links_to_files
from malevich.openai import prompt_completion, completion_with_vision
from malevich.cadquery import execute_python_with_cq
from malevich import flow, collection, config, table


PROMPT = """
    @@ Task
    Write python code that uses cadquery to generate {user_query}. Please assign the final object to variable named Result. Please don't do show_object() command and DON'T INSTALL ANY LIBRARIES.
    @@ Your previous code:
    {previous_code}
    @@ Feedback from the previously generated image:
    {feedback}
    @@ Error (if there was any):
    {error_code}
    @@ Response (add @@@ and @@@ at the start and finish of your code):
"""


CRITIC_PROMPT = """
    I am building cadquery-based shape generation script and the following attached image represents image of shape that was supposed to be {user_query}.
    Please output some actionable items I could do to make it look more like {user_query}.
    This is the old code for the reference:
    {code}

    This is the error (if there is any):
    {error_code}
"""

@flow(reverse_id='cadquery_critic.round')
def cadquery_critic():
    user_query = collection(

        "CAD User Queries", alias='user_query',        df=table(
                    [ ['sofa', '', '', '']], 
                    columns=['user_query', 'previous_code', 'feedback', 'error_code']
                ),
    )
    
    
    code = prompt_completion(
        user_query,
        config=config(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            user_prompt=PROMPT,
            model='gpt-4'
        )
    )
    
    execution_result = execute_python_with_cq(code)
    execution_with_links = get_links_to_files(execution_result)
    
    critic = completion_with_vision(
        merge(locs(user_query, {'column': 'user_query'}), execution_with_links),
        config=config(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            user_prompt=CRITIC_PROMPT,
            image_column='image'
        )
    )
    
    
    return critic, execution_with_links


if __name__ == '__main__':
    
    from malevich import CoreInterpreter
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--rounds', '-n', type=int)
    parser.add_argument('--results-directory', '-d', type=str)
    parser.add_argument('--query', '-q', type=str)

    args = parser.parse_args()
    
    query = [args.query, '', '', '']
    os.makedirs(args.results_directory, exist_ok=True)
    task = cadquery_critic()
    # task.interpret(CoreInterpreter(core_auth=('example', "Welcome to Malevich!")))
    task.interpret()
    # task.prepare()
    # for i in range(args.rounds):
    #     task.run(
    #         run_id=str(i),
    #         override={
    #             'user_query': table(
    #                 [query], 
    #                 columns=['user_query', 'previous_code', 'feedback', 'error_code']
    #             )
    #         },
    #         with_logs=True,
    #         profile_mode='all'
    #     )
    
    #     critic_response, exec_result = task.results(
    #         run_id=str(i)
    #     )
        
    #     feedback = str(critic_response.get_df().iloc[0, 0])
    #     error_code = str(exec_result.get_df().error_code.iloc[0])
    #     previous_code = str(exec_result.get_df().code.iloc[0])
    #     exec_result.get_df().to_csv(os.path.join(args.results_directory, f'output_{i}.csv'))
        
    #     query = [args.query, previous_code, feedback, error_code]
        
        