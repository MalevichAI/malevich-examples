import os

from malevich import flow, collection
from malevich.interpreter.core import CoreInterpreter
from malevich.whywhy import *

sources_ =  "./data/rss_feed_sample.csv"
recipients_ = "./data/email_workshop_test.csv"
@flow(reverse_id='whywhy.newsletter.facts', name="Facts Newsletter")
def facts_newsletter():
    sources = collection(file=sources_, name="whywhy.sources")
    recipients = collection(file=recipients_, name="whywhy.recipients")
    
    article_urls = get_article_url_from_rss(sources)
    article_body = get_article_body_with_url(article_urls)

    sentences = split_article_to_sentence(article_body)
    
    fact_labels = sentence_classifier(sentences, config={"model": "fo", "subjectivity_threshold": 0.5})
    sentiment_lables = sentence_classifier(sentences, config={"model": "sentiment", "sentiment_threshold": 0.5})
    
    summary = score_article(fact_labels, sentiment_lables)

    parsed_recipients = parse_recipeints(recipients)

    return send_newsletter(parsed_recipients, summary, config={"login": os.getenv("EMAIL_LOGIN"), "password": os.getenv("EMAIL_PASSWORD")})


if __name__ == "__main__":
    task = facts_newsletter()
    task.interpret()
