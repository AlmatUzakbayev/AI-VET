import pytest

from backend.app.services.ner import VetNERService


@pytest.fixture(scope="module")
def ner():
    return VetNERService()


@pytest.mark.parametrize("text, animal", [
    ("Корова не ест", "корова"),
    ("У коровы диарея", "корова"),
    ("Купил козу, у неё кашель", "коза"),
    ("У телёнка рвота", "телёнок"),
    ("У теленка рвота", "телёнок"),
])
def test_animal_is_found_in_any_case_form(ner, text, animal):
    assert animal in ner.extract(text)["animals"]


def test_symptoms_are_found(ner):
    result = ner.extract("У овцы слабость, судороги и отказ от еды")

    assert set(result["symptoms"]) == {"слабость", "судороги", "отказ от еды"}


@pytest.mark.parametrize("text, duration", [
    ("Свинья хромает 3 дня", "3 дня"),
    ("Кашель уже 2 недели", "2 недели"),
    ("Кашель без причины", None),
])
def test_duration(ner, text, duration):
    assert ner.extract(text)["duration"] == duration


def test_text_without_entities(ner):
    result = ner.extract("Добрый день")

    assert result["animals"] == []
    assert result["symptoms"] == []
