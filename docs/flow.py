import argparse
import ast
import os
import time

import pandas as pd
from malevich import collection, flow
from malevich.models.results.core.result import CoreResult
from malevich.openai_api import prompt_completion
from malevich.runners.async_core import AsyncCoreRunner

parser = argparse.ArgumentParser(description='Automatic docs generator')
parser.add_argument(
    '--path', type=str, default='.',
    help='Path to the project'
)


@flow(
    reverse_id='malevich.docs.generate',
    name="Generate library documentation",
)
def generate_docs():
    """Generates documentation for library functions using GPT-4"""
    data = collection('FunctionData')

    return prompt_completion(
        data,
        config={
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'user_prompt': "{code}\nDocumentation: ```markdown",
            'system_prompt': open(
                os.path.join(os.path.dirname(__file__), 'docs.prompt.txt')
            ).read(),
            'temperature': 0.333,
            'max_tokens': 1024,
            'model': 'gpt-4-1106-preview'
        }
    )


def process_output(outputs: list[CoreResult], app: str, func: str):
    print(f"Processing output for {app}")
    output = outputs[0].get()  # Taking the first result of flow (there is only one)
    # The app returns a single dataframe, so we take the first one
    # and access its data
    output_df = output[0].data
    with open(
        # Collecting processors in README.md
        os.path.join(args.path, app, 'README.md'), 'a+'
    ) as f:
        # 0 - first row
        f.write(output_df['content'][0] + '\n\n')
        print(f"Writing to {os.path.join(args.path, app, 'README.md')}")
    # Creating docs folder (if it is first processor in app)
    os.makedirs(os.path.join(args.path, app, 'docs'), exist_ok=True)
    with open(os.path.join(args.path, app, 'docs', f'{func}.md'), 'w+') as f:
        print(
            f"Writing to {os.path.join(args.path, app, 'docs', f'{func}.md')}"
        )
        # 0 - first row
        f.write(output_df['content'][0])
    print(f"Done processing output for {app}")


if __name__ == '__main__':
    data = []
    args = parser.parse_args()
    # Iterating over library files
    for root, dirs, files in os.walk(args.path):
        for file in files:
            # Parsing python files
            if file.endswith('.py'):
                with open(os.path.join(root, file)) as f:
                    # Parsing AST
                    tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        # Looking for functions with @processor decorator
                        if isinstance(node, ast.FunctionDef):
                            function_name = node.name
                            decorators = [
                                # id may be absent?
                                d.func.id for d in node.decorator_list
                                if isinstance(d, ast.Call)
                            ]
                            if 'processor' in decorators:
                                data.append(
                                    {
                                        'name': function_name,
                                        'code': ast.unparse(node),
                                        'docstring': ast.get_docstring(node),
                                        'path': f'{root}/{file}',
                                        'app': root.split(args.path)[1].strip('/').split('/')[0]  # noqa: E501
                                    }
                                )

    runner = AsyncCoreRunner(task=generate_docs, core_auth=('leo', 'pak'))
    try:
        for i, d in enumerate(data):
            if len(d['code']) > 6000:
                print(f"Skipping {d['name']} due to code length")
                continue

        
            def get_callback(index):
                """The function is needed to capture the index variable"""
                def _f(outputs: list[pd.DataFrame]) -> None:
                    return process_output(
                        outputs, 
                        data[index]['app'], 
                        data[index]['name']
                    )
                # Returning the function object
                # with index of the current function
                # captured in its closure
                return _f

            runner.run(
                # FunctionData is a collection
                # within the flow
                FunctionData=pd.DataFrame([d]),
                # Callback is function that will be called
                # after the flow is finished
                # We are using a callback library
                # to capture the index of the current processor
                # to be described
                callback=get_callback(i),
            )
            # This is needed to avoid overloading the Open AI API
            # with too many requests
            time.sleep(0.5)

        runner.wait()
    except KeyboardInterrupt:
        runner.stop()
