# Copyright: Anki Software, LLC and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Maps a deck name such as "Espanhol", "Spanish" or "Español" to a flag.

A language is not a country, so each language has one default flag (Portuguese
is Brazil, English is the US, Spanish is Spain...). The flag files live in
data/web/imgs/flags/<code>.svg (flag-icons, MIT).
"""

from __future__ import annotations

import colorsys
import re
import unicodedata

# flag code -> names of the language in Portuguese, English and the language itself
_LANGUAGES: dict[str, tuple[str, ...]] = {
    "br": ("português", "portuguese", "portugues"),
    "us": ("inglês", "english", "inglés"),
    "es": ("espanhol", "spanish", "español", "castelhano", "castellano"),
    "fr": ("francês", "french", "français"),
    "de": ("alemão", "german", "deutsch"),
    "it": ("italiano", "italian"),
    "jp": ("japonês", "japanese", "日本語", "にほんご", "nihongo"),
    "cn": ("chinês", "chinese", "mandarim", "mandarin", "中文", "普通话", "zhongwen"),
    "hk": ("cantonês", "cantonese", "广东话", "粵語"),
    "kr": ("coreano", "korean", "한국어", "hangul"),
    "ru": ("russo", "russian", "русский"),
    "sa": ("árabe", "arabic", "العربية"),
    "in": (
        "hindi",
        "हिन्दी",
        "tâmil",
        "tamil",
        "telugo",
        "telugu",
        "punjabi",
        "marati",
        "marathi",
        "gujarati",
    ),
    "tr": ("turco", "turkish", "türkçe"),
    "nl": ("holandês", "dutch", "nederlands", "neerlandês"),
    "se": ("sueco", "swedish", "svenska"),
    "no": ("norueguês", "norwegian", "norsk"),
    "dk": ("dinamarquês", "danish", "dansk"),
    "fi": ("finlandês", "finnish", "suomi"),
    "pl": ("polonês", "polish", "polski"),
    "gr": ("grego", "greek", "ελληνικά"),
    "il": ("hebraico", "hebrew", "עברית"),
    "th": ("tailandês", "thai", "ภาษาไทย"),
    "vn": ("vietnamita", "vietnamese", "tiếng việt"),
    "id": ("indonésio", "indonesian", "bahasa"),
    "ua": ("ucraniano", "ukrainian", "українська"),
    "cz": ("tcheco", "czech", "čeština"),
    "hu": ("húngaro", "hungarian", "magyar"),
    "ro": ("romeno", "romanian", "română"),
    "bg": ("búlgaro", "bulgarian"),
    "rs": ("sérvio", "serbian"),
    "hr": ("croata", "croatian", "hrvatski"),
    "sk": ("eslovaco", "slovak"),
    "ir": ("persa", "persian", "farsi", "فارسی"),
    "ke": ("suaíli", "swahili", "kiswahili"),
    "ph": ("tagalog", "filipino"),
    "pk": ("urdu", "اردو"),
    "bd": ("bengali", "bangla"),
    "ie": ("irlandês", "irish", "gaeilge"),
    "es-ct": ("catalão", "catalan", "català"),
    "es-pv": ("basco", "basque", "euskara"),
    "es-ga": ("galego", "galician"),
    "gb-wls": ("galês", "welsh", "cymraeg"),
    "va": ("latim", "latin"),
    "nz": ("maori", "māori"),
    "my": ("malaio", "malay", "melayu"),
    "lt": ("lituano", "lithuanian", "lietuvių"),
    "lv": ("letão", "latvian", "latviešu"),
    "ee": ("estoniano", "estonian", "eesti"),
    "si": ("esloveno", "slovenian", "slovene"),
    "al": ("albanês", "albanian", "shqip"),
    "mk": ("macedônio", "macedonian"),
    "ba": ("bósnio", "bosnian"),
    "is": ("islandês", "icelandic", "íslenska"),
    "za": ("africâner", "afrikaans", "zulu", "xhosa"),
    "et": ("amárico", "amharic"),
    "ng": ("iorubá", "yoruba", "igbo", "hausa"),
    "so": ("somali",),
    "mt": ("maltês", "maltese"),
    "lu": ("luxemburguês", "luxembourgish"),
    "ge": ("georgiano", "georgian"),
    "am": ("armênio", "armenian"),
    "az": ("azeri", "azerbaijani", "azerbaijano"),
    "kz": ("cazaque", "kazakh"),
    "uz": ("uzbeque", "uzbek"),
    "mn": ("mongol", "mongolian"),
    "np": ("nepalês", "nepali"),
    "lk": ("cingalês", "sinhala", "sinhalese"),
    "kh": ("khmer", "cambojano"),
    "la": ("laosiano", "lao"),
    "mm": ("birmanês", "burmese"),
    "by": ("bielorrusso", "belarusian"),
    "ht": ("haitiano", "haitian"),
}


# main colors of each flag, in stripe order (used for the hover effect of the cards)
_FLAG_COLORS: dict[str, tuple[str, ...]] = {
    "br": ("#009C3B", "#FFDF00", "#002776"),
    "us": ("#B22234", "#FFFFFF", "#3C3B6E"),
    "es": ("#AA151B", "#F1BF00", "#AA151B"),
    "fr": ("#0055A4", "#FFFFFF", "#EF4135"),
    "de": ("#000000", "#DD0000", "#FFCE00"),
    "it": ("#009246", "#FFFFFF", "#CE2B37"),
    "jp": ("#FFFFFF", "#BC002D", "#FFFFFF"),
    "cn": ("#DE2910", "#FFDE00"),
    "hk": ("#DE2910", "#FFFFFF"),
    "kr": ("#FFFFFF", "#CD2E3A", "#0047A0"),
    "ru": ("#FFFFFF", "#0039A6", "#D52B1E"),
    "sa": ("#006C35", "#FFFFFF"),
    "in": ("#FF9933", "#FFFFFF", "#138808"),
    "tr": ("#E30A17", "#FFFFFF"),
    "nl": ("#AE1C28", "#FFFFFF", "#21468B"),
    "se": ("#006AA7", "#FECC00"),
    "no": ("#BA0C2F", "#FFFFFF", "#00205B"),
    "dk": ("#C8102E", "#FFFFFF"),
    "fi": ("#FFFFFF", "#003580"),
    "pl": ("#FFFFFF", "#DC143C"),
    "gr": ("#0D5EAF", "#FFFFFF"),
    "il": ("#FFFFFF", "#0038B8"),
    "th": ("#A51931", "#F4F5F8", "#2D2A4A"),
    "vn": ("#DA251D", "#FFFF00"),
    "id": ("#FF0000", "#FFFFFF"),
    "ua": ("#0057B7", "#FFD700"),
    "cz": ("#FFFFFF", "#D7141A", "#11457E"),
    "hu": ("#CE2939", "#FFFFFF", "#477050"),
    "ro": ("#002B7F", "#FCD116", "#CE1126"),
    "bg": ("#FFFFFF", "#00966E", "#D62612"),
    "rs": ("#C6363C", "#0C4076", "#FFFFFF"),
    "hr": ("#FF0000", "#FFFFFF", "#171796"),
    "sk": ("#FFFFFF", "#0B4EA2", "#EE1C25"),
    "ir": ("#239F40", "#FFFFFF", "#DA0000"),
    "ke": ("#000000", "#BB0000", "#006600"),
    "ph": ("#0038A8", "#CE1126", "#FCD116"),
    "pk": ("#01411C", "#FFFFFF"),
    "bd": ("#006A4E", "#F42A41"),
    "ie": ("#169B62", "#FFFFFF", "#FF883E"),
    "es-ct": ("#FCDD09", "#DA121A"),
    "es-pv": ("#D52B1E", "#009B48", "#FFFFFF"),
    "es-ga": ("#FFFFFF", "#0A5FAA"),
    "gb-wls": ("#FFFFFF", "#00AB39", "#D30731"),
    "va": ("#FFE000", "#FFFFFF"),
    "nz": ("#00247D", "#FFFFFF", "#CC142B"),
    "my": ("#CC0001", "#FFFFFF", "#010066", "#FFCC00"),
    "lt": ("#FDB913", "#006A44", "#C1272D"),
    "lv": ("#9E3039", "#FFFFFF", "#9E3039"),
    "ee": ("#0072CE", "#000000", "#FFFFFF"),
    "si": ("#FFFFFF", "#005DA4", "#ED1C24"),
    "al": ("#E41E20", "#000000"),
    "mk": ("#D20000", "#FFE600"),
    "ba": ("#002395", "#FECB00", "#FFFFFF"),
    "is": ("#02529C", "#FFFFFF", "#DC1E35"),
    "za": ("#E03C31", "#FFFFFF", "#007749", "#001489", "#FFB81C"),
    "et": ("#078930", "#FCDD09", "#DA121A"),
    "ng": ("#008751", "#FFFFFF", "#008751"),
    "so": ("#4189DD", "#FFFFFF"),
    "mt": ("#FFFFFF", "#CF142B"),
    "lu": ("#EF3340", "#FFFFFF", "#00A3E0"),
    "ge": ("#FFFFFF", "#FF0000"),
    "am": ("#D90012", "#0033A0", "#F2A800"),
    "az": ("#00B5E2", "#EF3340", "#509E2F"),
    "kz": ("#00AFCA", "#FEC50C"),
    "uz": ("#1EB53A", "#FFFFFF", "#0099B5"),
    "mn": ("#C4272F", "#015197", "#C4272F"),
    "np": ("#DC143C", "#003893"),
    "lk": ("#8D153A", "#EB7400", "#00534E", "#FFBE29"),
    "kh": ("#032EA1", "#E00025", "#FFFFFF"),
    "la": ("#CE1126", "#002868", "#CE1126"),
    "mm": ("#FECB00", "#34B233", "#EA2839"),
    "by": ("#C8313E", "#4AA657"),
    "ht": ("#00209F", "#D21034"),
}


def _rgb(color: str) -> tuple[float, float, float]:
    return tuple(int(color[i : i + 2], 16) / 255 for i in (1, 3, 5))  # type: ignore[return-value]


def _luminance(color: str) -> float:
    """Relative luminance as defined by WCAG."""

    def linear(channel: float) -> float:
        if channel <= 0.03928:
            return channel / 12.92
        return ((channel + 0.055) / 1.055) ** 2.4

    r, g, b = (linear(c) for c in _rgb(color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def flag_accent(code: str) -> str | None:
    """The color of the flag that reads best on both the dark and the light theme.

    Only vivid colors are candidates (white and black are not), and among those
    the one with the best contrast against both a dark canvas and white wins.
    So Brazil is green rather than yellow, which would vanish on a light theme."""
    colors = _FLAG_COLORS.get(code)
    if not colors:
        return None

    def score(color: str) -> float:
        _, saturation, _ = colorsys.rgb_to_hsv(*_rgb(color))
        if saturation < 0.4:
            return 0
        luminance = _luminance(color)
        return min((luminance + 0.05) / 0.06, 1.05 / (luminance + 0.05))

    return max(colors, key=score)


# The accent is drawn as a 1px border and a glow, which needs about 3:1 contrast
# against the card: a dark card (luminance ~0.02) needs luminance >= 0.16 and a
# white card needs luminance <= 0.30.
_MIN_LUMINANCE_ON_DARK = 0.16
_MAX_LUMINANCE_ON_LIGHT = 0.30


def flag_accent_for_theme(code: str, dark: bool) -> str | None:
    """The flag's accent, made lighter (dark theme) or darker (light theme) just
    enough to stay visible. Only the lightness changes, so the hue and the
    saturation stay those of the country (red stays red, not pink)."""
    accent = flag_accent(code)
    if accent is None:
        return None
    hue, lightness, saturation = colorsys.rgb_to_hls(*_rgb(accent))
    direction = 0.01 if dark else -0.01
    candidate = accent
    for _ in range(100):
        luminance = _luminance(candidate)
        if dark and luminance >= _MIN_LUMINANCE_ON_DARK:
            break
        if not dark and luminance <= _MAX_LUMINANCE_ON_LIGHT:
            break
        lightness = min(max(lightness + direction, 0.0), 1.0)
        r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
        candidate = f"#{round(r * 255):02X}{round(g * 255):02X}{round(b * 255):02X}"
    return candidate


def flag_stripes(code: str) -> str | None:
    """CSS gradient with hard stops that looks like the flag's stripes."""
    colors = _FLAG_COLORS.get(code)
    if not colors:
        return None
    n = len(colors)
    stops = ", ".join(
        f"{color} {100 * i / n:.1f}% {100 * (i + 1) / n:.1f}%"
        for i, color in enumerate(colors)
    )
    return f"linear-gradient(90deg, {stops})"


def _normalize(text: str) -> str:
    """Lowercase and strip accents, so 'Alemão' and 'alemao' compare equal."""
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


# aliases made only of letters and digits are matched as whole words, so that
# "Espanhol - Viagem" matches but "Cantoneses" would not match "cantones"
_WORD_ALIASES: dict[str, str] = {}
# aliases in other scripts (kanji, hangul...) have no word boundaries, so they
# are matched anywhere in the name
_SUBSTRING_ALIASES: dict[str, str] = {}

for _code, _names in _LANGUAGES.items():
    for _name in _names:
        _alias = _normalize(_name)
        if _alias.isascii():
            _WORD_ALIASES.setdefault(_alias, _code)
        else:
            _SUBSTRING_ALIASES.setdefault(_alias, _code)


def flag_for_deck_name(name: str) -> str | None:
    """Return the flag code for a deck name, or None if no language is found."""
    normalized = _normalize(name)
    for word in re.split(r"[\W_]+", normalized):
        code = _WORD_ALIASES.get(word)
        if code:
            return code
    for alias, code in _SUBSTRING_ALIASES.items():
        if alias in normalized:
            return code
    return None


def all_flag_codes() -> set[str]:
    return set(_LANGUAGES)
