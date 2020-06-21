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


import constant as C, log, logging as l, sys
from interface.icontainer import IContainer
import pandas as pd, numpy as np
from copy import deepcopy
from pathlib import Path
from typing import Any, List, Dict


class Terminology(IContainer):
    r"""The container of AI tech Terminology.

    parameters
    ----------
    terminology_file: Path
        The terminology file full path. If it is a path with file name, only the file is to be used. If it is a 
        directry, all files of the directry and sub-directry are loaded.

    methods
    -------

    attributes
    ----------
    term: pd.DataFrame
        container of terminology dataframe

    terminology_file: Path
        The terminology file full path
    """


    def __init__(self, terminology_file:Path=None):
        if not terminology_file.is_file():
            raise ValueError('terminology_file arguement has to be file')
        if terminology_file.suffix != '.csv':
            raise ValueError(f'terminology_file arguement ({terminology_file.suffix}) has to be "csv" suffix file')

        def parse(val:Any) -> Any:
            r"""Convert value to 1. string type; 2. List if string is with VAL_SEP; 3. NaN like value to "".
            """
            str_val = str(val)
            temp = str_val.split(self.VAL_SEP)
            return temp if len(temp) > 1 else str_val

        super().__init__()
        self.COL_NAME = [C.LANG_EN_CAP, C.LANG_EN, C.LANG_EN_ABBR, C.LANG_CN_ZH]
        self.TERM_INDEX = {
            'INDEX': 0, C.LANG_EN: 1, C.LANG_EN_ABBR: 2, C.LANG_CN_ZH: 3
        }
        self.VAL_SEP = '/'
        self.COL_CONV = {
            C.LANG_EN_CAP: parse, C.LANG_EN: parse, C.LANG_EN_ABBR: parse, C.LANG_CN_ZH: parse
        }
        self.log = l.getLogger(__name__)
        self.terminology_file = terminology_file
        self.term = pd.read_csv(str(terminology_file), names=self.COL_NAME, converters=self.COL_CONV, encoding='utf-8', header=0)
        # self.term.sort_values(by=C.LANG_EN)#, ascending=[True, False], inplace=True, axis=1)
        # self.term.sort_values(by=[C.LANG_EN], ascending=[False], inplace=True, axis=1)
        self.term = self.term.drop([C.LANG_EN_CAP], axis=1)
