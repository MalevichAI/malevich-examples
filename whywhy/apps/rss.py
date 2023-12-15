import feedparser
import pandas as pd

from malevich.square import Context, processor


@processor()
def get_article_url_from_rss(docs, context: Context):
    """
    Parse RSS feed and retrieve a list of article links
    """
    app_cfg = context.app_cfg
    article_limit = app_cfg.get("article_count_limit", 10)
    urls = []
    titles = []
    source_names = []
    feed_urls = []

    for _, row in docs.iterrows():
        feed_url = row["rss_feed_url"]

        news_feed = feedparser.parse(feed_url)
        for i in range(min(article_limit, len(news_feed.entries))):
            titles.append(news_feed.entries[i]["title"])
            urls.append(news_feed.entries[i]["link"])
            source_names.append(row["source_name"])
            feed_urls.append(row["rss_feed_url"])

    articles = pd.DataFrame(
        {"article_url": urls}
    )

    return articles
