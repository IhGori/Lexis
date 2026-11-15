# Copyright: Anki Software, LLC and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from typing import Any

import pytest

from aqt.stylesheets import _theme_qcolor, blend


class FakeTheme:
    "Just enough of ThemeManager for the color helpers."

    def var(self, color: dict[str, str]) -> str:
        return color["light"]

    def qcolor(self, color: dict[str, str]) -> Any:
        raise AssertionError("should not be needed")


@pytest.mark.parametrize(
    "css, rgb",
    [
        ("white", (255, 255, 255)),
        ("#3b82f6", (59, 130, 246)),
        ("rgb(18.7843137255%, 41.8823529412%, 92.5490196078%)", (48, 107, 236)),
        ("rgb(10, 20, 30)", (10, 20, 30)),
        ("rgba(10, 20, 30, 0.5)", (10, 20, 30)),
    ],
)
def test_theme_qcolor_understands_every_notation(
    css: str, rgb: tuple[int, int, int]
) -> None:
    c = _theme_qcolor(FakeTheme(), {"light": css, "dark": css})  # type: ignore[arg-type]
    assert (c.red(), c.green(), c.blue()) == rgb


def test_blend_mixes_in_the_given_ratio() -> None:
    tm: Any = FakeTheme()
    black, white = {"light": "#000000"}, {"light": "#ffffff"}
    assert blend(tm, black, white, 0) == "#ffffff"
    assert blend(tm, black, white, 1) == "#000000"
    assert blend(tm, black, white, 0.5) == "#808080"
