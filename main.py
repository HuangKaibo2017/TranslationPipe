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


from typing import List, Any, AnyStr, Dict
import constant as C, config as CONF
import log, logging as l, sys
from pathlib import Path
from container.term import Terminology
from translation.standardizors import Standardizor
from mini_spider.spider import Spider
from tool import get_root, get_val
import pandas as pd
from zipfile import ZipFile, ZIP_DEFLATED
from pandas.io.excel import ExcelWriter
from shutil import copy2
from load_task import load_task


lg = l.getLogger(__name__)


if __name__ == "__main__":
    root = get_root()
    folder_requirement = root.joinpath(CONF.DIR_DATA, CONF.DIR_REQUIREMENT)
    if not folder_requirement.exists():
        raise ValueError(f"requirement folder '{folder_requirement}' is not exists.")
    folder_term = root.joinpath(CONF.DIR_DATA, CONF.DIR_TERM, CONF.TERMNINOLOGY_FILE)
    if not folder_term.exists():
        raise ValueError(f"Terminology File '{folder_term}' is not exists.")
    folder_download = root.joinpath(CONF.DIR_DATA, CONF.DIR_DOWNLOAD)
    if not folder_download.exists():
        folder_download.mkdir(parents=True, exist_ok=True)
    folder_standardized = root.joinpath(CONF.DIR_DATA, CONF.DIR_STANDARDIZED)
    if not folder_standardized.exists():
        folder_standardized.mkdir(parents=True, exist_ok=True)
    folder_temp = root.joinpath(CONF.DIR_DATA, CONF.DIR_TEMP)
    if not folder_temp.exists():
        folder_temp.mkdir(parents=True, exist_ok=True)
    lg.info(
        f"root:{root}.\nfolder terminology:{folder_term}.\nfolder requirement:{folder_requirement}.\n"
        + f"folder download:{folder_download}.\nfolder standardized:{folder_standardized}.\n"
    )

    spider = Spider(folder_download)
    term = Terminology(folder_term)
    std = Standardizor(folder_standardized, term)

    tasks: List = load_task(folder_requirement)
    for task in tasks:
        try:
            pth:Path = task[0]
            task_content:pd.DataFrame = task[1]
            for index, row in enumerate(task_content.itertuples(index=True)):
                uri = get_val(row.uri)
                if uri is None or len(uri) < 2:
                    continue
                src_language = get_val(row.src_language)
                dst_language = get_val(row.dst_language)
                downloaded = get_val(row.download)
                standardized = get_val(row.standardized)
                encoding = get_val(row.encoding)
                if not downloaded and len(downloaded) < 1:
                    downloaded, encoding = spider.start_single(row.uri, Path.joinpath(folder_download, downloaded))
                    task_content.loc[index, C.REQ_DOWNLOAD] = downloaded.name
                    task_content.loc[index, C.REQ_ENCODING] = encoding
                else:
                    downloaded = folder_download.joinpath(downloaded)
                if not standardized and len(standardized) < 1:
                    standardized = std.parse_one(downloaded=downloaded, from_lang=src_language, to_lang=dst_language, encoding=encoding)
                    task_content.loc[index, C.REQ_STANDARDIZED] = standardized.name

            ew = ExcelWriter(str(pth))
            task_content.to_excel(ew,index=False,encoding='utf-8')
            ew.save()
            ew.close()
        except:
            exc_type, exc_val, _ = sys.exc_info()
            lg.error("[{}]{}.".format(exc_type, exc_val), exc_info=True)