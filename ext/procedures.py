import base64
import json
import os
import random
import unicodedata
from typing import Any, Callable, Iterable

from iso639 import languages

__all__ = ["code_to_lang", "join_iter", "code_block", "normalize", "human_status", "bool_to_emoji", "convert_to_bool", "convert_to_int", "linkvertise"]

lang_codes = {'da': 'Danish, Denmark', 'de': 'German, Germany', 'en-GB': 'English, United Kingdom', 'en-US': 'English, United States', 'es-ES': 'Spanish, Spain', 'fr': 'French, France', 'hr': 'Croatian, Croatia', 'lt': 'Lithuanian, Lithuania', 'hu': 'Hungarian, Hungary', 'nl': 'Dutch, Netherlands', 'no': 'Norwegian, Norway', 'pl': 'Polish, Poland', 'pt-BR': 'Portuguese, Brazilian, Brazil', 'ro': 'Romanian, Romania', 'fi': 'Finnish, Finland', 'sv-SE': 'Swedish, Sweden', 'vi': 'Vietnamese, Vietnam', 'tr': 'Turkish, Turkey', 'cs': 'Czech, Czechia, Czech Republic', 'el': 'Greek, Greece', 'bg': 'Bulgarian, Bulgaria', 'ru': 'Russian, Russia', 'uk': 'Ukranian, Ukraine', 'th': 'Thai, Thailand', 'zh-CN': 'Chinese, China', 'ja': 'Japanese', 'zh-TW': 'Chinese, Taiwan', 'ko': 'Korean, Korea'}

code_to_lang: Callable[[str], str] = lambda code: lang_codes.get(code, "Unknown")
join_iter: Callable[[Iterable, str, str], str] = lambda iter, joiner, ends: str(ends + joiner.join(iter) + ends)
code_block: Callable[[str, str], str] = lambda s, lang = None: ('```' if not lang else '```{0}'.format(lang)) + str(s) + '```'
normalize: Callable[[str], str] = lambda s: unicodedata.normalize(u"NFKD", s).encode("ascii", "ignore").decode("utf8")
human_status: Callable[[str], str] = lambda status: {"dnd": "Do Not Disturb.", "online": "Online.", "idle": "Idle.", "offline": "Offline."}.get(status, 'Error.')
bool_to_emoji: Callable[[bool], str] = lambda boolean: '✅' if boolean is True else '❌'
convert_to_bool: Callable[[int], bool] = lambda int: False if int == 0 else True
convert_to_int: Callable[[bool], int] = lambda bool: 0 if bool == False else 1
linkvertise: Callable[[str], str] = lambda redirect: "https://link-to.net/327045/{0}/dynamic?r={1}".format(random.randint(1, 9000), base64.encodebytes(redirect.encode('utf-8')).decode('utf-8'))