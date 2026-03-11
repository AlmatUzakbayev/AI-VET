COMMON_SYMPTOMS = {
    "отказ от еды": ["вирусная инфекция", "отравление", "стресс", "зубная боль"],
    "диарея": ["паразиты", "смена корма", "инфекция ЖКТ", "отравление"],
    "кашель": ["бронхит", "пневмония", "сердечная недостаточность", "паразиты лёгких"],
    "хромота": ["травма", "артрит", "копытная гниль", "некробактериоз"],
    "снижение удоя": ["мастит", "стресс", "смена рациона", "инфекция"],
}

ANIMAL_SPECIES = [
    "крупный рогатый скот",
    "мелкий рогатый скот",
    "свиньи",
    "птица",
    "пушные",
]


class VetKnowledge:
    def __init__(self):
        self.symptoms = COMMON_SYMPTOMS
        self.species = ANIMAL_SPECIES

    def get_possible_diagnoses(self, symptom: str) -> list[str]:
        symptom_lower = symptom.lower()
        for key, diagnoses in self.symptoms.items():
            if key in symptom_lower:
                return diagnoses
        return []

    def is_known_species(self, species: str) -> bool:
        return any(s in species.lower() for s in self.species)
