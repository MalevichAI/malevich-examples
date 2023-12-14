from malevich.square import scheme
from pydantic import BaseModel


@scheme()
class Source(BaseModel):
    source_name: str
    rss_feed_url: str


@scheme()
class ArticleUrl(Source):
    article_url: str
    
@scheme()
class ArticleBody(BaseModel):
    id: str
    title: str
    body: str
    url: str


@scheme()
class Sentence(BaseModel):
    sentence_uuid: str
    sentence_text: str
    article_id: str


@scheme()
class LabeledSentence(Sentence):
    label: str


@scheme()
class ArticleSummary(BaseModel):
    article_id: str
    article_text: str


@scheme()
class Recipient(BaseModel):
    title: str
    recipient: str


@scheme()
class RecipientStatus(BaseModel):
    recipient: str
    status: str
