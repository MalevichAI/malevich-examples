import sys
import subprocess

import spacy

from malevich.square import Context, processor, init

from .tools import SentenceClassifier, BestSentenceClassifier


@init()
def ensure_spacy(ctx: Context):
    """Ensure spaCy asset is loaded"""
    spacy.cli.download("en_core_web_sm")


@processor()
def sentence_classifier(docs, context: Context):
    """
    Demo sentence classifier using spaCy package
    """
    app_cfg = context.app_cfg
    model = app_cfg["model"]
    if model in ["fo", "sentiment"]:
        sentence_classifier = SentenceClassifier(
            model,
            subjectivity_threshold=app_cfg.get("subjectivity_threshold"),
            sentiment_threshold=app_cfg.get("sentiment_threshold")
        )
    else:
        sentence_classifier = BestSentenceClassifier(model)

    sents = docs["sentence_text"].tolist()
    docs["label"] = sentence_classifier.batch(sents)

    return docs
