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
from pathlib import Path
import constant as c

class StandardWord(IContainer):

    def __init__(self, root:str, source_type:str):
        """

        :param source: source.
        :param source: type of source. It could be "csv_file", "xlsx_file", "csv_str".
        :param language_heads: for example: {'en':[1,2],'zh-cn':[3]}
        """
        super().__init__()
        self._root = root
        self._dict = dict()
        self._cache = dict()
        self.ext_property = dict()
        p = Path(self._root)
        for i in p.glob("*.xlsx"):
            if Path(i).name.startswith("~$"):
                continue
            df: pd.DataFrame = None
            try:
                if source_type == c.TYPE_FILE_CSV:
                    df = pd.read_csv(i)
                elif source_type == c.TYPE_FILE_XLSX:
                    df = pd.read_excel(i)
                else:
                    raise NotImplementedError("source_type '{}' is not supported.".format(source_type))
                lang_keys = []
                index = 1
                language_heads = {}
                for i in df.keys():
                    dot = i.find(".")
                    # right now, only extend property is IGNORECASE.
                    k, ext = (str(i)[0:dot], str(i)[dot+1:]) if dot > 0 else (i, "")
                    if len(ext) > 0:
                        self.ext_property[index] = ext
                    if k not in lang_keys:
                        lang_keys.append(k)
                    if k not in language_heads:
                        language_heads[k] = [index]
                    else:
                        language_heads[k].append(index)
                    if k not in self._dict:
                        self._dict[k] = {}
                        self._dict[k][index] = {}
                    else:
                        if index not in self._dict[k]:
                            self._dict[k][index] = {}
                    index += 1
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
                                            self._dict[i][j][row[j]] = {o: [row[l]]}
                                    else:
                                        self._dict[i] = {j: {row[j]: {o: [row[l]]}}}
                self._language_heads = language_heads
            except:
                exc_type, exc_val, _ = sys.exc_info()
                logging.error("err[{}]:{}".format(exc_type, exc_val, exc_info=True))
            finally:
                if df is not None:
                    del df
        # logging.info(self._dict)

    def get_word_pair(self, src:str= 'en', dst:str= 'zh-cn'):
        key = "{}{}".format(src, dst)
        if key in self._cache:
            return self._cache[key]
        res = None
        if 'en' in self._dict:
            res = dict()
            for k,v in self._dict[src].items():
                res[k] = dict()
                for k_i, v_i in v.items():
                    res[k][k_i] = v_i[dst]
        self._cache[key] = res
        return res

