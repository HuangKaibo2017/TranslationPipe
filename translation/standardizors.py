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


import log, logging as l, os, re
from container.term import Terminology
from pathlib import Path
# from collections import OrderedDict
import constant as c
from datetime import datetime

class Standardizor(object):
    def __init__(self, std_path:str):
        self.log = l.getLogger(__name__)
        self._std_path = std_path

    def parse_single(self, download, word_pair:dict, ext_properties:dict):
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
        # self.log.info("ordered_key:%s.", ordered_key)
        std_f_name = os.path.join(self._std_path, str(Path(download).name))
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

            # for std_i in ordered_key:
            #     std_k = terms[std_i]
            #     k_len = len(std_k[0])
            #     s_f.write(content[start_i:std_i + k_len])
            #     s_f.write("[翻译：{}]".format(",".join(std_k[1]) if isinstance(std_k[1], list) else std_k[1]))
            #     start_i = std_i + k_len
            s_f.flush()
        after = datetime.now()
        self.log.info("Standardized with [%s]‘%s’.", after-before, std_f_name)
        return std_f_name

    def parse(self, files:dict, term:Terminology):
        replace = dict()
        for k, v in files.items():
            if "standardized" in v and len(v[c.STANDARDIZED]) > 0:
                self.log.info("**omitted. uri:'%s' is standardized, '%s'.", k, v[c.STANDARDIZED])
                continue
            if c.DOWNLOAD in v and len(v[c.DOWNLOAD]) > 0:
                word_pair = term.get_word_pair(v[c.LANG_SRC], v[c.LANG_DST])
                std_f_name = self.parse_single(v[c.DOWNLOAD], word_pair, term.ext_property)
                v[c.STANDARDIZED] = std_f_name
