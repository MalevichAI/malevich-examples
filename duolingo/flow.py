import os

import pandas as pd
import argparse

from malevich import collection, config, flow
from malevich.drives import download_from_google_drive
from malevich.openai import prompt_completion
from malevich.translate import translate_texts
from malevich.tts import text_to_speech
from malevich.ultralytics import detect
from malevich.utility import add_column, locs, merge_two, rename, squash


@flow(reverse_id='examples.duolingo', name='Duoling: Tell a story about what I see')
def duolingo(
    file: str,
    classes: dict,
    prompt: str,
    target_language: str,
):
    """Takes an image and describes it in a target language."""

    # Create a collection
    # for the images stored on drive
    files = collection(
        name='Duolingo Images',
        # Only one file is stored
        df=pd.DataFrame({
            'link': [file],
        })
    )

    # Download files from Google Drive storage
    # and store them in the local filesystem
    paths = download_from_google_drive(files)

    # Create a collection
    # that stores a code
    # for the target language
    language = rename(collection(
        name='Duolingo Language',
        df=pd.DataFrame({
            'to_language': [target_language],
        })
    ))

    # Detect objects on the images
    objects = rename(  # Rename the column to match prompt variable
        locs(  # Select class names
            # Detection with YOLOv8
            detect(paths, config(classes=classes)),
            config={'column': 'cls_name'}
        ), config={'cls_name': 'objects'}
    )

    # Send to OpenAI API
    descriptions = prompt_completion(
        squash(objects),
        config(
            user_prompt=prompt,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
    )

    descriptions = rename(
        locs(descriptions, config(column='content')),
        config(content='text')
    )
    # Merge the outputs of langchain and column
    # with `target_language` to match the expected
    # format of the input to the translation app
    for_translation = merge_two(  # Merge 2 DFs
        add_column(  # Add a column to the first DF
            descriptions,
            config={'column': 'from_language', 'value': 'en', 'position': -1}
        ),
        language, config={'how': 'cross'}
    )

    # Translate texts
    translated = merge_two(
        locs(  # Select the column with texts
            translate_texts(for_translation),
            config={'column': 'translation'},
        ),
        language,
        config={'how': 'cross'}
    )

    # Convert texts to speech
    speech = text_to_speech(
        translated
    )

    return speech


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('link', type=str)
    parser.add_argument('target_language', type=str)
    args = parser.parse_args()

    classes = open(
        os.path.join(
            os.path.dirname(__file__),
            'misc'
            'classes.txt'
        )
    ).read().split('\n')
    classes = {str(i): cls for i, cls in enumerate(classes)}

    prompt = open(
        os.path.join(
            os.path.dirname(__file__),
            'misc',
            'prompt.txt'
        )
    ).read()

    task = duolingo(
        file=args.link,
        target_language=args.target_language,
        classes=classes,
        prompt=prompt,
    )

    task.interpret()

    task.prepare()
    task.run()
    task.stop()
    print(task.results())
