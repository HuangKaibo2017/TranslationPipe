#!/usr/b#!/usr/bin/python3.6
# -*- coding: UTF-8 -*-
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
import sys, logging
sys.path.insert(0, "..")
from interface.icontainer import IContainer
import pandas as pd
from copy import deepcopy

class StandardWord(IContainer):

    def __init__(self, source:str, source_type:str, language_heads:dict):
        """

        :param source: source.
        :param source: type of source. It could be "csv_file", "xlsx_file", "csv_str".
        :param language_heads: for example: {'en':[1,2],'zh-cn':[3]}
        """
        super().__init__()
        self._dict = dict()
        df:pd.DataFrame = None
        if source_type == 'csv_file' or source_type == 'csv_str':
            df = pd.read_csv(source)
        elif source_type == 'xlsx_file':
            df = pd.read_excel(source)
        elif source_type == 'csv_str':
            raise NotImplementedError("source_type '{}' is not supported.".format(source_type))
        lang_keys = []
        for i, k in language_heads.items():
            lang_keys.append(i)
            self._dict[i] = {}
            for j in k:
                self._dict[i][j] = {}
        for row in df.itertuples(index=True):
            for i, k in language_heads.items():
                other_lang_keys = deepcopy(lang_keys)
                other_lang_keys.remove(i)
                for j in k:
                    if pd.isnull(row[j]):
                        continue
                    for o in other_lang_keys:
                        for l in language_heads[o]:
                            if pd.isnull(row[l]):
                                continue
                            if j in self._dict[i]:
                                if row[j] in self._dict[i][j]:
                                    if o in self._dict[i][j][row[j]]:
                                        self._dict[i][j][row[j]][o].append(row[l])
                                    else:
                                        self._dict[i][j][row[j]][o] = [row[l]]
                                else:
                                    self._dict[i][j][row[j]]= {o:[row[l]]}
                            else:
                                self._dict[i] = {j:{row[j]: {o:[row[l]]}}}
        self._language_heads = language_heads
        logging.info(self._dict)

    def get_keyword(self, src:str='en', dst:str='zh-cn'):
        res = None
        if 'en' in self._dict:
            res = dict()
            for k,v in self._dict[src].items():
                res[k] = dict()
                for k_i, v_i in v.items():
                    res[k][k_i] = v_i[dst]
        return res

