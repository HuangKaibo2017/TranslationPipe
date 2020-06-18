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


import constant as C
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
    folder_requirement = root.joinpath(C.DATA, C.REQUIREMENT)
    if not folder_requirement.exists():
        raise ValueError(f"requirement folder '{folder_requirement}' is not exists.")
    folder_term = root.joinpath(C.DATA, C.TERMNINOLOGY_FILE)
    if not folder_term.exists():
        raise ValueError(f"Terminology File '{folder_term}' is not exists.")
    folder_download = root.joinpath(C.DATA, C.REQ_DOWNLOAD)
    if not folder_download.exists():
        folder_download.mkdir(parents=True, exist_ok=True)
    folder_standardized = root.joinpath(C.DATA, C.REQ_STANDARDIZED)
    if not folder_standardized.exists():
        folder_standardized.mkdir(parents=True, exist_ok=True)
    folder_temp = root.joinpath(C.DATA, C.FOLDER_TEMP)
    if not folder_temp.exists():
        folder_temp.mkdir(parents=True, exist_ok=True)
    lg.info(
        f"root:{root}.\nfolder terminology:{folder_term}.\nfolder requirement:{folder_requirement}.\n"
        + f"folder download:{folder_download}.\nfolder standardized:{folder_standardized}.\n"
    )

    spider = Spider(folder_download)
    term = Terminology(folder_term, C.TYPE_FILE_CSV)
    std = Standardizor(folder_standardized)

    tasks: pd.DataFrame = load_task(folder_requirement)
    for index, row in enumerate(tasks.itertuples(index=True)):
        uri = get_val(row.uri)
        if uri is None or len(uri) < 2:
            continue
        src_language = get_val(row.src_language)
        dst_language = get_val(row.dst_language)
        download = get_val(row.download)
        standardized = get_val(row.standardized)
        encoding = get_val(row.encoding)
        if not download and len(download) < 1:
            download, encoding = spider.start_single(row.uri, Path.joinpath(folder_download, download))
            tasks.set_value(index, C.REQ_DOWNLOAD, download.name)
            tasks.set_value(index, C.REQ_ENCODING, encoding)
        else:
            download = folder_download.joinpath(download)
        if not standardized and len(standardized) < 1:
            word_pair = term.get_word_pair(src_language, dst_language)
            standardized = std.parse_single(download, word_pair, term.ext_property)
            tasks.set_value(index, C.REQ_STANDARDIZED, standardized.name)