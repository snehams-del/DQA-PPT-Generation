import pytest
from presentation_agent.shared_libraries.models import CoverSpec, DeckSpec, SlideSpec
from pydantic import ValidationError


def test_cover_spec():
    cover = CoverSpec(title="Test Cover")
    assert cover.title == "Test Cover"
    assert cover.subhead is None


def test_slide_spec_valid():
    slide = SlideSpec(title="Slide 1", bullets=["Point 1", "Point 2"])
    assert slide.title == "Slide 1"
    assert len(slide.bullets) == 2
    assert slide.layout_name == "Title and Content"  # default


def test_slide_spec_invalid():
    with pytest.raises(ValidationError):
        SlideSpec(bullets=["No title"])  # title is missing


def test_deck_spec():
    deck = DeckSpec(
        cover={"title": "My Deck"},
        slides=[{"title": "Slide 1", "layout_name": "Title Only"}],
        closing_title="Thank You",
    )
    assert deck.cover.title == "My Deck"
    assert deck.slides[0].title == "Slide 1"
    assert deck.closing_title == "Thank You"
