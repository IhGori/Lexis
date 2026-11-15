# Copyright: Anki Software, LLC and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from pathlib import Path

import pytest

import anki.lang
import aqt
from aqt.language_flags import (
    all_flag_codes,
    flag_accent,
    flag_accent_for_theme,
    flag_for_deck_name,
    flag_stripes,
)


@pytest.mark.parametrize(
    "name, code",
    [
        ("Português", "br"),
        ("English", "us"),
        ("Inglês", "us"),
        ("Espanhol", "es"),
        ("Spanish", "es"),
        ("Español", "es"),
        ("Alemão", "de"),
        ("alemao", "de"),
        ("日本語", "jp"),
        ("Japonês N5", "jp"),
        ("한국어", "kr"),
        ("Espanhol - Viagem", "es"),
        ("Estudo de inglês", "us"),
        ("Catalão", "es-ct"),
    ],
)
def test_flag_for_deck_name(name: str, code: str) -> None:
    assert flag_for_deck_name(name) == code


@pytest.mark.parametrize("name", ["Default", "Padrão", "Matemática", "", "Cantoneses"])
def test_no_flag_for_unknown_names(name: str) -> None:
    assert flag_for_deck_name(name) is None


def test_every_flag_code_has_an_image() -> None:
    flags_dir = Path(aqt.__file__).parent / "data" / "web" / "imgs" / "flags"
    missing = sorted(
        c for c in all_flag_codes() if not (flags_dir / f"{c}.svg").exists()
    )
    assert missing == []


@pytest.mark.parametrize(
    "query, ok",
    [("a", False), ("", False), ("ab", True), ("水", True), ("한", True), ("é", False)],
)
def test_one_character_is_enough_only_without_spaces(query: str, ok: bool) -> None:
    # importing the deck browser translates some strings at import time
    anki.lang.set_lang("en")
    from aqt.deckbrowser import DeckBrowser

    assert DeckBrowser._worth_searching(query) is ok


def test_every_flag_has_colors() -> None:
    import re

    for code in all_flag_codes():
        accent = flag_accent(code)
        stripes = flag_stripes(code)
        assert accent and re.fullmatch(r"#[0-9A-F]{6}", accent), code
        assert stripes and stripes.startswith("linear-gradient(90deg, #"), code


@pytest.mark.parametrize(
    "code, accent",
    [
        ("jp", "#BC002D"),  # the white would be faint
        ("de", "#DD0000"),  # black vanishes on dark, gold on light
        ("br", "#009C3B"),  # yellow would vanish on a light theme
        ("es", "#AA151B"),
        ("nope", None),
    ],
)
def test_flag_accent_is_a_vivid_color(code: str, accent: str | None) -> None:
    assert flag_accent(code) == accent


def test_stripes_have_hard_stops() -> None:
    assert flag_stripes("cn") == (
        "linear-gradient(90deg, #DE2910 0.0% 50.0%, #FFDE00 50.0% 100.0%)"
    )


def test_accent_is_visible_on_both_themes_for_every_flag() -> None:
    """3:1 against a dark card needs luminance >= 0.16, against white <= 0.30."""
    from aqt.language_flags import _luminance

    for code in all_flag_codes():
        dark = flag_accent_for_theme(code, dark=True)
        light = flag_accent_for_theme(code, dark=False)
        assert dark and _luminance(dark) >= 0.155, (code, dark)
        assert light and _luminance(light) <= 0.305, (code, light)


def test_theme_adjustment_keeps_a_good_color_untouched() -> None:
    # Brazil's green already reads well on both themes
    assert flag_accent_for_theme("br", dark=True) == "#009C3B"
    assert flag_accent_for_theme("br", dark=False) == "#009C3B"
    # the dark blue of Finland is made lighter on a dark card, not on a light one
    assert flag_accent_for_theme("fi", dark=False) == "#003580"
    assert flag_accent_for_theme("fi", dark=True) != "#003580"


def test_overview_header_for_a_subdeck_and_for_a_deck_without_flag() -> None:
    anki.lang.set_lang("en")
    from aqt.overview import Overview

    sub = Overview._header("Espanhol::Verbos")
    assert "flags/es.svg" in sub["flag"]
    assert "has-flag" in sub["klass"]
    assert "--flag-accent-dark" in sub["style"]
    assert sub["name"] == "Verbos"
    assert "Espanhol" in sub["path"]

    plain = Overview._header("Geral")
    assert plain["flag"] == "" and plain["style"] == "" and plain["path"] == ""
    assert plain["klass"] == "ov"


def test_overview_header_escapes_html() -> None:
    anki.lang.set_lang("en")
    from aqt.overview import Overview

    header = Overview._header("<b>x</b>::<i>y</i>")
    assert header["name"] == "&lt;i&gt;y&lt;/i&gt;"
    assert "&lt;b&gt;x&lt;/b&gt;" in header["path"]
