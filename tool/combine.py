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


# convert the terminology from 机器之心 and combine all together.
# There are three sources handled by this script.
# 1. data/cs-ds
# 2. data/ref/机器之心-github词汇集合项目.md
# 3. data/ref/Artificial-Intelligence-Terminology-master/data/...

"""
Solution

1.
    Table Design
    ------------
    id, int32, id of each row
    en_abbr, string[62], English Abbreviation of Terminology
    en, string[254], English Terminology
    cn_zh, string[254], Simple Chinese Terminology
    xxxx_x, string[254]. xxxx presents the three column name beyond, which are 'en_abbr', 'en' and 'zh'.
                         x presents num from 1 to 9.
    The basic format is language shortname, like cn_zh. It could be other languages. If there are
    more present-terms of one terminology, the suffix is '_x', the x is between 1 to 9.

2. 
    table partition
    ---------------
    partitioned by Char order, like A, B, C,...
    Each char occupies one sheet.
"""
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List, Any, AnyStr, Union


ROOT = Path('.')
ROOT_AI_TERM = ROOT.joinpath(Path('data','ref','Artificial-Intelligence-Terminology-master','data'))


def get_typed_df() -> Dict[str, Any]:
    dtypes = {
        'capital': '',
        'en': '',
        'en_abbr': '',
        'cn_zh': '',
    }
    return dtypes


def process():
    # python .\tool\combine.py
    # step 1, process  data/ref/Artificial-Intelligence-Terminology-master/data/... 
    print(ROOT_AI_TERM)
    data = []
    for f_rm in ROOT_AI_TERM.iterdir():
        print(f_rm)
        with open(str(f_rm), 'r', encoding='utf-8') as f:
            for line in f:
                items = line.split('|')
                if len(items) <= 2:
                    continue
                ens = items[0].split('/')
                en,en_abbr = ens[0].lower().strip(),''
                if len(en) < 1 or en == '英文' or en == '---': continue
                if len(ens) > 1:
                    en_abbr = ens[1].upper().strip()
                cn_zh = items[1].strip()
                data.append([en[0], en, en_abbr, cn_zh])
    # print(data)
    cols = get_typed_df()
    df = pd.DataFrame(data, columns=cols)
    df.to_csv(r'C:\Users\Ron\Desktop\export_dataframe.csv', index = False, header=True)


if __name__ == '__main__':
    process()



