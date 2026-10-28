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
            Segmenter, NewsEmbedding,
            NewsMorphTagger, NewsSyntaxParser,
            NewsNERTagger,
        )
        self.segmenter = Segmenter()
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

        text_lower = text.lower()
        animals = [a for a in ANIMAL_KEYWORDS if a in text_lower]
        symptoms = [s for s in SYMPTOM_KEYWORDS if s in text_lower]

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