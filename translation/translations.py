#!/usr/bin/python3.6
# -*- coding: UTF-8 -*-

from container.std_word import StandardWord
from pathlib import Path
import os, re
from collections import OrderedDict

class Translation(object):
    def __init__(self, std:StandardWord, std_path:str):
        self._std = std
        self._std_path = std_path

    def parse(self, files:dict, src_lang:str='en', dst_lang:str='zh-cn'):
        std = self._std.get_keyword(src_lang, dst_lang)
        replace = OrderedDict()
        for k, v in files.items():
            if "standardized" in v and len(v["standardized"]) > 0:
                continue
            if "download" in v and len(v["download"]) > 0:
                content:str = None
                with open(v["download"], "r", encoding="utf-8") as f:
                    content = f.read()
                for std_dict in std.values():
                    for std_k, std_v in std_dict.items():
                        p = re.compile(r"[^\=\-\</\w]{1}"+std_k+r"[^\>\-\=\w]{1}",re.IGNORECASE)
                        for m in p.finditer(content):
                            replace[m.start()+1] = [std_k, std_v]
                        # def search_word(replace_d:dict, src:str, start_index, std_wd, replace_word):
                        #     std_wd_k = "{} ".format(std_wd)
                        #     start_index = src.find(std_wd_k, start_index)
                        #     if start_index > 0:
                        #         replace_d[start_index] = [std_wd, replace_word]
                        #         search_word(replace_d, src, start_index+1, std_wd, replace_word)
                        # search_word(replace, content, 0, std_k, std_v)
                ordered_key = sorted(replace.keys())
                std_f_name = os.path.join(self._std_path, str(Path(v["download"]).name).replace(".html", "_std.html"))
                with open(std_f_name, "w+", encoding="utf-8") as s_f:
                    start_i = 0
                    for std_i in ordered_key:
                        std_k = replace[std_i]
                        k_len = len(std_k[0])
                        s_f.write(content[start_i:std_i+k_len])
                        s_f.write("[翻译：{}]".format(",".join(std_k[1]) if isinstance(std_k[1], list) else std_k[1]))
                        start_i = std_i+k_len
                    s_f.flush()
                v["standardized"] = std_f_name



