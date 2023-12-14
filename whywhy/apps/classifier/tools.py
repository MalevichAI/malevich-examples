from typing import List
from random import randint
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob


class SentenceClassifier:
    def __init__(self, name, subjectivity_threshold: float = 0.5, sentiment_threshold: float = 0, device='cpu'):
        self.mode = name
        self.device = device
        self.nlp = spacy.load('en_core_web_sm')
        self.nlp.add_pipe('spacytextblob')

        self.subjectivity_threshold = subjectivity_threshold
        self.sentiment_threshold = sentiment_threshold

    def batch(self, sents: List[str]) -> List[str]:
        """
        :param sent:
        :return:
        """
        out = []
        for sent in sents:
            doc = self.nlp(sent)
            if self.mode == "fo":
                score = doc._.blob.subjectivity
                if score > self.subjectivity_threshold:
                    out.append("opinion")
                else:
                    out.append("fact")
            elif self.mode == "sentiment":
                score = doc._.blob.polarity
                if score > self.sentiment_threshold:
                    out.append("positive")
                else:
                    out.append("negative")
        return out
        
    
class BestSentenceClassifier:
    def __init__(self, name, device='cpu'):
        self.path = name
        self.device = device

    def predict(self, _):
        return randint(0,1)
