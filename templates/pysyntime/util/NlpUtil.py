import spacy
from ..model import TaggedToken

class NlpUtil(object):
    """
    NLP util to do POS-tagging for the input.txt text. NLP is powered by spaCy.
    """

    def __init__(self):
        # self.nlp = spacy.load('ro_core_news_sm')
        self.nlp = spacy.load('en_core_web_sm')
        # doc = self.nlp("Iulia Popescu, cea din Constanta, ieri, s-a dus la Lidl să cumpere pâine pe la ora doisprezece.\n Pe drum și-a dat seama că are nevoie de 50 de lei așa că a trecut și pe la bancomat înainte.")
        # for ent in doc.ents:
        #     print(ent.text, ent.label_)

    def tagging(self, text):
        if not text:
            return None
        doc = self.nlp(text)
        taggedTokenList = []
        offset = 0
        for token in doc:
            offset = text.find(token.text, offset)
            taggedToken = TaggedToken()
            taggedToken.token = token.text
            taggedToken.lemma = token.lemma_
            taggedToken.tag = token.tag_
            taggedToken.tokenPosition = token.i
            taggedToken.beginCharPosition = offset
            taggedToken.endCharPosition = offset + len(token)
            offset += len(token)
            taggedTokenList.append(taggedToken)

        return taggedTokenList
