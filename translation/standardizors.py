__author__ = 'Huang Kaibo <kamp_kbh@hotmail.com>'
# The following code, derived from the bulbs project, carries this
# license:
"""
Copyright (c) 2017 Huang Kaibo (kamp_kbh@hotmail.com)
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. The name of the author may not be used to endorse or promote products
   derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


import constant as C, log, logging as l, os, re
from typing import Any, AnyStr, List, Dict
from itertools import chain
from pathlib import Path
from datetime import datetime
from copy import deepcopy
from container.term import Terminology


class Standardizor(object):
    r"""Standardize the downloaded html file.

    parameters
    ----------
    std_path: Path
        saved path of standardized files.

    attributes
    ----------
    log: Logger.

    std_path: Path. saved path of standardized files.

    term: Terminology. The Terminology object instance.

    term_pair: Dict. The pair structure of Terminology, which is 
        {
            'key': # The key is constructd by '-'.join(cols)
                   # The cols is constructd by [from_languages, to_language]
            [
                from_languages, to_language, df[from_languages, to_language]
            ]
        }
    """

    def __init__(self, std_path:Path, term:Terminology=None):
        self.log = l.getLogger(__name__)
        self.std_path:Path = std_path
        self.term: Terminology = term
        self.term_pair = dict()
        if self.term is None:
            return
        

    def __construct_term_pair(self, term:Terminology, from_lang:str, to_lang:str) -> List[List, AnyStr, pd.DataFrame]:
        r"""Construct Terminology pair. The structure is 
        {
            'key': # The key is constructd by '-'.join(cols)
                   # The cols is constructd by [from_languages, to_language]
            [
                from_languages, to_language, {from_lang_value: [complied_RE, [translation values]]}
            ]
        }

        parameters
        ----------
        term: Terminology. 
            The Terminology object instance.
        from_lang: str
            from language, like, 'en'.
        to_lang: str
            to language, like, 'cn_zh'

        returns
        -------
        return a Dict.
        """
        to_langs = []
        for col in term.COL_NAME:
            if col.startswith(to_lang):
                to_langs.append(col)
        if len(to_langs) < 1:
            raise ValueError(f'Value of to_lang, "{to_lang}", is not supported. Supported "{term.COL_NAME}"')
        from_langs = []
        for col in term.COL_NAME:
            if col.startswith(from_lang):
                from_langs.append(col)
        if len(from_langs) < 1:
            raise ValueError(f'Value of from_lang, "{from_lang}", is not supported. Supported "{term.COL_NAME}"')
        cols = deepcopy(from_langs).extend(to_langs)
        key = '-'.join(cols)
        df: pd.DataFrame = term.term[cols]
        search = dict() # search pair. key is one of the from languagues, values are compose by
                        # [compiled re,  [translation list]]
        for index, row in enumerate(df.itertuples(index=True)):
            for frm_lang in from_langs:
                frm_keys = row[frm_lang]
                # search key type could be single value, which is string; or List, whichs is list of string.
                if isinstance(frm_keys, str):
                    p = re.compile(r"[^\+\=\-\</\w]{1}" + frm_keys + r"[^\+\>\-\=\w]{1}", flags=re.IGNORECASE)
                    search[frm_keys] = [p, row[to_lang]]
                elif isinstance(frm_keys, list):
                    for k in frm_keys:
                        p = re.compile(r"[^\+\=\-\</\w]{1}" + k + r"[^\+\>\-\=\w]{1}", flags=re.IGNORECASE)
                        search[k] = [p, chain.from_iterable(row[to_langs])]
        self.term_pair[key] = [from_langs, to_langs, search]
        return self.term_pair[key]


    def parse_one(self, downloaded:Path, from_lang:str='en', to_lang:str='cn_zh', term:Terminology=None, encoding='utf-8') -> Path:
        r"""Parse one downloaded file and returns standardized file full path.

        parameters
        ----------
        downloaded: Path
            The full path of downloaded file.
        from_lang: str
            from language, like, 'en'.
        to_lang: str
            to language, like, 'cn_zh'
        term: Terminology
            terminology arguement.

        returns
        -------
        Path. return the standardized file full path.
        """
        before = datetime.now()
        content: str = None
        term = term if term is None else self.term
        if term is None:
            raise ValueError('The term arguement has to be set, either set by parse_one or constructor')
        with open(downloaded, "r", encoding=encoding) as f:
            content = f.read()
        std_name: Path = None
        after = datetime.now()
        self.log.info(f"Standardized with [{after-before}]‘{std_name}’")
        return std_name


    def parse_single(self, download:Path, word_pair:dict, ext_properties:dict) -> Path:
        before = datetime.now()
        terms = dict()
        content: str = None
        with open(download, "r", encoding="utf-8") as f:
            content = f.read()
        for index, std_dict in word_pair.items():
            ext_int = 0
            if index in ext_properties:
                ext_int = re.IGNORECASE if ext_properties[int(index)] == "IGNORECASE" else 0
            for std_k, std_v in std_dict.items():
                p = re.compile(r"[^\+\=\-\</\w]{1}" + std_k + r"[^\+\>\-\=\w]{1}", flags=ext_int)
                for m in p.finditer(content):
                    k_index = m.start() + 1
                    if k_index not in terms:
                        terms[k_index] = [std_k, std_v]
        ordered_key = sorted(terms.keys())
        std_f_name = self.std_path.joinpath(download.name)
        with open(std_f_name, "w+", encoding="utf-8") as s_f:
            start_i = 0
            key_index = 0
            key_len = len(ordered_key)
            while key_index < key_len:
                order_index = ordered_key[key_index]
                std_k = terms[order_index]
                k_len = len(std_k[0])
                same_len_as_before = order_index + k_len
                if start_i == same_len_as_before:
                    key_index += 1
                    continue
                s_f.write(content[start_i:order_index + k_len])
                s_f.write("[翻译：{}]".format(",".join(std_k[1]) if isinstance(std_k[1], list) else std_k[1]))
                start_i = order_index + k_len
                key_index += 1
            s_f.flush()
        after = datetime.now()
        self.log.info(f"Standardized with [{after-before}]‘{std_f_name}’")
        return std_f_name


    def parse(self, files:dict, term:Terminology):
        replace = dict()
        for k, v in files.items():
            if C.REQ_STANDARDIZED in v and len(v[C.REQ_STANDARDIZED]) > 0:
                self.log.info(f"**omitted. uri:'{k}' is standardized, '{v[C.REQ_STANDARDIZED]}'")
                continue
            if C.REQ_DOWNLOAD in v and len(v[C.REQ_DOWNLOAD]) > 0:
                word_pair = term.get_word_pair(v[C.REQ_LANG_SRC], v[C.REQ_LANG_DST])
                std_f_name = self.parse_single(v[C.REQ_DOWNLOAD], word_pair, term.ext_property)
                v[C.REQ_STANDARDIZED] = std_f_name
