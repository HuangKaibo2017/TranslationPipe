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
import logging, os, sys
from os import path

from container.std_word import StandardWord
from translation.standardizors import Standardizor
from mini_spider.spiders import Spider
from tool import get_root, get_val
# from openpyxl import load_workbook, workbook
import constant as c
import pandas as pd
# from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from pandas.io.excel import ExcelWriter
from glob import glob
from shutil import copy2

logging.basicConfig(
    format='[%(filename)s:%(lineno)s %(asctime)s %(levelname)s %(funcName)16s()]\n%(message)s'
    , datefmt='%Y%m%d-%H%M%S', level=logging.INFO)

if __name__ == "__main__":
    root = get_root()
    folder_requirement = str(root.joinpath(c.DATA, c.REQUIREMENT))
    if not path.exists(folder_requirement):
        raise ValueError("requirement folder '{}' is not exists.".format(folder_requirement))
    folder_std_word = root.joinpath(c.DATA, c.CS_DS)
    if not path.exists(folder_std_word):
        raise ValueError("standard word folder '{}' is not exists.".format(folder_std_word))
    folder_download = str(root.joinpath(c.DATA, c.DOWNLOAD))
    if not path.exists(folder_download):
        os.mkdir(folder_download)
    folder_standardized = root.joinpath(c.DATA, c.STANDARDIZED)
    if not path.exists(folder_standardized):
        os.mkdir(folder_standardized)
    folder_temp = root.joinpath(c.DATA, c.FOLDER_TEMP)
    if not path.exists(folder_temp):
        os.mkdir(folder_temp)
    logging.info("root:%s.\nfolder_std_word:%s.\nfolder_requirement:%s.\nfolder_download:%s.\nfolder_standardized:%s.\n"
                 , root, folder_std_word, folder_requirement, folder_download, folder_standardized)

    spider = Spider(folder_download)
    std_word = StandardWord(folder_std_word, c.TYPE_FILE_XLSX)
    std = Standardizor(folder_standardized)

    info = dict()
    files = glob(path.join(folder_requirement, "*.xlsx"))
    for i in files:
        if path.basename(i).startswith("~$"):
            continue
        df: pd.DataFrame = None
        try:
            logging.info("**processing ‘%s’.", i)
            df: pd.DataFrame = pd.read_excel(i, na_values=[''],na_filter=False)
            index = 0
            for row in df.itertuples(index=True):
                uri = get_val(row.uri, "")
                if uri is None or len(uri) < 2:
                    continue
                src_language = get_val(row.src_language, "")
                dst_language = get_val(row.dst_language, "")
                download = get_val(row.download, "")
                standardized = get_val(row.standardized, "")
                encoding = get_val(row.encoding, "")
                if not download and len(download) < 1:
                    download, encoding = spider.start_single(row.uri, path.join(folder_download, download))
                    df.set_value(index, 'download', path.basename(download))
                    df.set_value(index, 'encoding', encoding)
                else:
                    download = path.join(folder_download, download)
                if not standardized and len(standardized) < 1:
                    word_pair = std_word.get_word_pair(src_language, dst_language)
                    standardized = std.parse_single(download, word_pair, std_word.ext_property)
                    df.set_value(index, 'standardized', path.basename(standardized))
                index += 1
            # writer = pd.ExcelWriter(i)
            # df.to_excel(writer)
            # writer.save()

            # archive = ZipFile(f, 'w', ZIP_DEFLATED, allowZip64=True)
            save_i = path.join(folder_temp, path.basename(i))
            if path.exists(save_i):
                os.remove(save_i)
            ew = ExcelWriter(save_i)
            df.to_excel(ew,index=False,encoding='utf-8')
            ew.save()
            ew.close()
            if df is not None:
                del df
            if path.exists(save_i):
                if path.exists(i):
                    os.remove(i)
                copy2(save_i, i)
                os.remove(save_i)
        except:
            exc_type, exc_val, _ = sys.exc_info()
            logging.error("[{}]{}.".format(exc_type, exc_val), exc_info=True)


