import os

from malevich import flow, collection, run, SpaceInterpreter, CoreInterpreter
from malevich.whywhy import *

sources_ =  "./data/rss_feed_sample.csv"
recipients_ = "./data/email_workshop_test.csv"


@flow(reverse_id="whywhy.feed.preload", name="Feed preloader")
def feed_preloader(sources):
    article_urls = run(get_article_url_from_rss(sources), alias="urls")
    article_body = run(get_article_body_with_url(article_urls), alias="body")
    return article_body


@flow(reverse_id='whywhy.newsletter.facts', name="Facts Newsletter")
def facts_newsletter():
    sources = collection(file=sources_, name="whywhy.sources")
    recipients = collection(file=recipients_, name="whywhy.recipients")

    article_body = feed_preloader(sources)

    sentences = run(
        split_article_to_sentence(article_body),
        alias="split"
    )
    
    fact_labels = run(
        sentence_classifier(
            sentences, config={"model": "fo", "subjectivity_threshold": 0.5}
        ), alias="fo"
    )
    sentiment_lables = run(
        sentence_classifier(
            sentences,
            config={"model": "sentiment", "sentiment_threshold": 0.5}
        ), alias="sentiment"
    )
    
    summary = run(
        score_article(fact_labels, sentiment_lables),
        alias="score"
    )

    parsed_recipients = run(parse_recipeints(recipients), alias="recep")

    return run(
        send_newsletter(
            parsed_recipients, summary, 
            config={"login": os.getenv("EMAIL_LOGIN"),
                    "password": os.getenv("EMAIL_PASSWORD")}
        ),
        alias="send"
    )


if __name__ == "__main__":
    task = facts_newsletter()
    interpreter = SpaceInterpreter()
    interpreter.supports_subtrees = False
    task.interpret(interpreter)