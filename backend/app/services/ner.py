import re

ANIMAL_KEYWORDS = [
    "корова", "коза", "овца", "свинья", "курица", "бык",
    "телёнок", "козлёнок", "поросёнок", "утка", "гусь",
]

SYMPTOM_KEYWORDS = [
    "диарея", "температура", "кашель", "хромота", "отказ от еды",
    "рвота", "слабость", "судороги", "отёк", "выделения",
]


class VetNERService:
    def __init__(self):
        from natasha import (
            Segmenter, MorphVocab, NewsEmbedding,
            NewsMorphTagger, NewsSyntaxParser,
            NewsNERTagger,
        )
        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()
        self.emb = NewsEmbedding()
        self.morph_tagger = NewsMorphTagger(self.emb)
        self.syntax_parser = NewsSyntaxParser(self.emb)
        self.ner_tagger = NewsNERTagger(self.emb)

    def extract(self, text: str) -> dict:
        from natasha import Doc
        doc = Doc(text)
        doc.segment(self.segmenter)
        doc.tag_morph(self.morph_tagger)
        doc.parse_syntax(self.syntax_parser)
        doc.tag_ner(self.ner_tagger)

        named_entities = [
            {"text": span.text, "type": span.type}
            for span in doc.spans
            if span.type in {"ORG", "PER", "LOC"}
        ]

        # Keywords are in the nominative case, so "у коровы" is matched through the lemma "корова"
        for token in doc.tokens:
            token.lemmatize(self.morph_vocab)
        lemmas = {_normalize(token.lemma) for token in doc.tokens}
        text_lower = _normalize(text.lower())

        animals = [a for a in ANIMAL_KEYWORDS if _normalize(a) in lemmas or _normalize(a) in text_lower]
        symptoms = [s for s in SYMPTOM_KEYWORDS if _normalize(s) in lemmas or _normalize(s) in text_lower]

        duration = None
        duration_match = re.search(r"(\d+)\s*(день|дня|дней|час|часа|часов|неделю|недели)", text_lower)
        if duration_match:
            duration = duration_match.group(0)

        return {
            "animals": animals,
            "symptoms": symptoms,
            "duration": duration,
            "named_entities": named_entities,
        }


def _normalize(word: str) -> str:
    return word.lower().replace("ё", "е")
