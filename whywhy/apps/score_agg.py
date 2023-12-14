import pandas as pd

from malevich.square import Context, processor


@processor()
def score_article(context: Context, fo_label, sentiment_label):
    app_cfg = context.app_cfg
    only_facts = bool(app_cfg.get("only_facts", False))
    only_opinions = bool(app_cfg.get("only_opinions", False))
    only_positive = bool(app_cfg.get("only_positive", False))
    only_negative = bool(app_cfg.get("only_negative", False))
    sentense_count = app_cfg.get("sentense_count", 5)
    assert sentense_count > 0, "sentense_count should be positive"

    ids = []
    texts = []

    for article_id in fo_label["article_id"].unique():
        sentence_ids = set(
            fo_label.loc[fo_label["article_id"] == article_id, "sentence_uuid"])
        if only_facts:
            filtered_ids = set(
                fo_label.loc[fo_label["label"] == "fact", "sentence_uuid"])
            sentence_ids = sentence_ids.intersection(filtered_ids)
        if only_opinions:
            filtered_ids = set(
                fo_label.loc[fo_label["label"] == "opinion", "sentence_uuid"])
            sentence_ids = sentence_ids.intersection(filtered_ids)
        if only_positive:
            filtered_ids = set(
                sentiment_label.loc[sentiment_label["label"] == "positive", "sentence_uuid"])
            sentence_ids = sentence_ids.intersection(filtered_ids)
        if only_negative:
            filtered_ids = set(
                sentiment_label.loc[sentiment_label["label"] == "negative", "sentence_uuid"])
            sentence_ids = sentence_ids.intersection(filtered_ids)

        article_text = " ".join(list(fo_label.loc[fo_label["sentence_uuid"].isin(
            sentence_ids), "sentence_text"])[:sentense_count])
        ids.append(article_id)
        texts.append(article_text)

    return pd.DataFrame({"article_id": ids, "text": texts})
