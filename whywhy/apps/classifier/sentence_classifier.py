import sys
import subprocess

from malevich.square import Context, processor

from .tools import SentenceClassifier, BestSentenceClassifier


@processor()
def sentence_classifier(docs, context: Context):
    app_cfg = context.app_cfg
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
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
