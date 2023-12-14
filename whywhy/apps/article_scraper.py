import pandas as pd

from goose3 import Goose
from malevich.square import processor


@processor()
def get_article_body_with_url(docs):
    g = Goose()
    ids = []
    titles = []
    bodies = []
    urls = []

    for id, row in docs.iterrows():
        print(row['article_url'])
        url = row["article_url"]
        article = g.extract(url)
        ids.append(id)
        titles.append(article.title)
        bodies.append(article.cleaned_text + " ")
        urls.append(url)

    parsed = pd.DataFrame({"id": ids, "title": titles, "body": bodies, "url": urls})

    return parsed
