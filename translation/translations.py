#!/usr/bin/python3.6
# -*- coding: UTF-8 -*-

from container.std_word import StandardWord
from pathlib import Path
import os, re, logging
# from collections import OrderedDict
import constant as c

class Standardizor(object):
    def __init__(self, std_path:str):
        self._std_path = std_path

    def parse_single(self, download, word_pair:dict):
        replace = dict()
        content: str = None
        with open(download, "r", encoding="utf-8") as f:
            content = f.read()
        for std_dict in word_pair.values():
            for std_k, std_v in std_dict.items():
                p = re.compile(r"[^\=\-\</\w]{1}" + std_k + r"[^\>\-\=\w]{1}", re.IGNORECASE)
                for m in p.finditer(content):
                    replace[m.start() + 1] = [std_k, std_v]
        ordered_key = sorted(replace.keys())
        std_f_name = os.path.join(self._std_path, str(Path(download).name))
        with open(std_f_name, "w+", encoding="utf-8") as s_f:
            start_i = 0
            for std_i in ordered_key:
                std_k = replace[std_i]
                k_len = len(std_k[0])
                s_f.write(content[start_i:std_i + k_len])
                s_f.write("[翻译：{}]".format(",".join(std_k[1]) if isinstance(std_k[1], list) else std_k[1]))
                start_i = std_i + k_len
            s_f.flush()
        return std_f_name


    def parse(self, files:dict, std_word:StandardWord):
        replace = dict()
        for k, v in files.items():
            if "standardized" in v and len(v[c.STANDARDIZED]) > 0:
                logging.info("**omitted. uri:'%s' is standardized, '%s'.", k, v[c.STANDARDIZED])
                continue
            if c.DOWNLOAD in v and len(v[c.DOWNLOAD]) > 0:
                content:str = None
                with open(v[c.DOWNLOAD], "r", encoding="utf-8") as f:
                    content = f.read()
                word_pair = std_word.get_word_pair(v[c.LANG_SRC], v[c.LANG_DST])
                for std_dict in word_pair.values():
                    for std_k, std_v in std_dict.items():
                        p = re.compile(r"[^\=\-\</\w]{1}" + std_k + r"[^\>\-\=\w]{1}", re.IGNORECASE)
                        for m in p.finditer(content):
                            replace[m.start()+1] = [std_k, std_v]
                ordered_key = sorted(replace.keys())
                std_f_name = os.path.join(self._std_path, str(Path(v[c.DOWNLOAD]).name).replace(".html", "_std.html"))
                with open(std_f_name, "w+", encoding="utf-8") as s_f:
                    start_i = 0
                    for std_i in ordered_key:
                        std_k = replace[std_i]
                        k_len = len(std_k[0])
                        s_f.write(content[start_i:std_i+k_len])
                        s_f.write("[翻译：{}]".format(",".join(std_k[1]) if isinstance(std_k[1], list) else std_k[1]))
                        start_i = std_i+k_len
                    s_f.flush()
                v[c.STANDARDIZED] = std_f_name
