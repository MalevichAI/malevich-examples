import os

from malevich import flow, collection
from malevich.interpreter.core import CoreInterpreter
from malevich.whywhy import *

@flow()
def facts_newsletter(sources: str, recipients: str):
    sources = collection(file=sources, name="whywhy.sources")
    recipients = collection(file=recipients, name="whywhy.recipients")
    
    article_urls = get_article_url_from_rss(sources)
    article_body = get_article_body_with_url(article_urls)

    sentences = split_article_to_sentence(article_body)
    
    fact_labels = sentence_classifier(sentences, config={"model": "fo", "subjectivity_threshold": 0.5})
    sentiment_lables = sentence_classifier(sentences, config={"model": "sentiment", "sentiment_threshold": 0.5})
    
    summary = score_article(fact_labels, sentiment_lables)

    parsed_recipients = parse_recipeints(recipients)

    return send_newsletter(parsed_recipients, summary, config={"login": os.getenv("EMAIL_LOGIN"), "password": os.getenv("EMAIL_PASSWORD")})


if __name__ == "__main__":
    task = facts_newsletter(
        "./data/rss_feed_sample.csv", "./data/email_workshop_test.csv"
    )
    task.interpret(...)
    print(task())