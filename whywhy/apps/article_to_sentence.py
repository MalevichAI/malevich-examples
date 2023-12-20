import sys
import uuid
import subprocess

import spacy
import pandas as pd

from malevich.square import processor


@processor()
def split_article_to_sentence(docs):
    """
    Split article content into sentences with spaCy
    """
    nlp = spacy.load("en_core_web_sm")
    out = []
    for _, row in docs.iterrows():
        article_doc = nlp(row["body"])
        for sentence in article_doc.sents:
            out.append(
                {
                    "sentence_uuid": str(uuid.uuid1()),
                    "sentence_text": sentence.text,
                    "article_id": row["id"]
                }
            )
    return pd.DataFrame(out)
