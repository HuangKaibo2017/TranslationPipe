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
from typing import Any, AnyStr, List, Dict, Set
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
        

    def __construct_term_pair(self, term:Terminology, from_lang:str, to_lang:str) -> List[Any]:
        r"""Construct Terminology pair. The structure is 
        {
            'key': # The key is constructd by '-'.join(cols)
                   # The cols is constructd by [from_languages, to_language]
            [
                from_languages, to_languages, {from_lang_value: [complied_RE, [translation values]]}
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
        return a List of pair info. Which is: [[from_languages], [to_languages], search]
            search is Dict, as {val_of_lang: [compiled_re, [translation_val]]}
        """
        to_langs = []
        for col in term.COL_NAME:
            if col.startswith(to_lang):
                to_langs.append(col)
        if len(to_langs) < 1:
            raise ValueError(f'Value of to_lang, "{to_lang}", is not supported. Supported "{term.COL_NAME}"')
        from_langs = []
        for col in term.term.columns:
            if col.startswith(from_lang):
                from_langs.append(col)
        if len(from_langs) < 1:
            raise ValueError(f'Value of from_lang, "{from_lang}", is not supported. Supported "{term.COL_NAME}"')

        def flat_list(val:Any, ret:Set) -> None:
            if isinstance(val, list):
                for i in val:
                    flat_list(i, ret)
            else:
                ret.add(val)

        cols = from_langs + to_langs
        key = '-'.join(cols)
        if key in self.term_pair:
            return self.term_pair[key]
        df: pd.DataFrame = term.term[cols]
        search = dict() # search pair. key is one of the from languagues, values are compose by
                        # [compiled re,  [translation list]]

        for row in df.itertuples(index=True):
            for frm_lang in from_langs:
                frm_keys = row[term.TERM_INDEX[frm_lang]] # TERM_INDEX is column index. frm_lang is one of from_langs
                # search key type could be single value, which is string; or List, whichs is list of string.
                val = set()
                flat_list([row[term.TERM_INDEX[i]] for i in to_langs], val) # to_lang may has multi-columns
                if isinstance(frm_keys, str):
                    if len(frm_keys) < 1: continue
                    p = re.compile(r"[^\+\=\-\</\w]{1}" + frm_keys + r"[^\+\>\-\=\w]{1}", flags=re.IGNORECASE)
                    search[frm_keys] = [p, val]
                elif isinstance(frm_keys, list):
                    for k in frm_keys:
                        if len(k) < 1: continue
                        p = re.compile(r"[^\+\=\-\</\w]{1}" + k + r"[^\+\>\-\=\w]{1}", flags=re.IGNORECASE)
                        search[k] = [p, val]
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
        term = term if term is not None else self.term
        if term is None :
            raise ValueError('The term arguement has to be set, either set by parse_one or constructor')
        with open(downloaded, "r", encoding=encoding) as f:
            content = f.read()

        pairs:List[List, List, Dict] = self.__construct_term_pair(term, from_lang, to_lang)
        pair:Dict = pairs[2] # key is val_of_from_lang, val is [compiled_re, translated_words]
        translated = {}
        for k, v in pair.items():
            for m in v[0].finditer(content):
                k_index = m.start() + 1 # m.start() is offset from 0 of content of html
                if k_index not in translated:
                    translated[k_index] = [k, v[1]] # v[1] is [translated_words]
        ordered_key = sorted(translated.keys())
        translated_file = self.std_path.joinpath(downloaded.name)
        with open(translated_file, "w+", encoding=encoding) as translated_f:
            start_i = 0
            key_index = 0
            key_len = len(ordered_key)
            while key_index < key_len:
                order_index = ordered_key[key_index]
                std_k = translated[order_index]
                k_len = len(std_k[0])
                same_len_as_before = order_index + k_len
                if start_i == same_len_as_before:
                    key_index += 1
                    continue
                translated_f.write(content[start_i:order_index + k_len])
                translated_f.write("[TERM:{}]".format(",".join(std_k[1]) if isinstance(std_k[1], list) else std_k[1]))
                start_i = order_index + k_len
                key_index += 1
            translated_f.flush()
        after = datetime.now()
        self.log.info(f"Standardized with [{after-before}]‘{translated_file}’")
        return translated_file
