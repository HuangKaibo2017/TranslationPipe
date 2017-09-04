#!/usr/bin/python3.6
# -*- coding: UTF-8 -*-

from container.std_word import StandardWord
from pathlib import Path
import os, re, logging
# from collections import OrderedDict
import constant as c
from datetime import datetime

class Standardizor(object):
    def __init__(self, std_path:str):
        self._std_path = std_path

    def parse_single(self, download, word_pair:dict, ext_properties:dict):
        before = datetime.now()
        std_words = dict()
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
                    if k_index not in std_words:
                        std_words[k_index] = [std_k, std_v]
        ordered_key = sorted(std_words.keys())
        logging.info("ordered_key:%s.", ordered_key)
        std_f_name = os.path.join(self._std_path, str(Path(download).name))
        with open(std_f_name, "w+", encoding="utf-8") as s_f:
            start_i = 0
            key_index = 0
            key_len = len(ordered_key)
            while key_index < key_len:
                order_index = ordered_key[key_index]
                std_k = std_words[order_index]
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
            #     std_k = std_words[std_i]
            #     k_len = len(std_k[0])
            #     s_f.write(content[start_i:std_i + k_len])
            #     s_f.write("[翻译：{}]".format(",".join(std_k[1]) if isinstance(std_k[1], list) else std_k[1]))
            #     start_i = std_i + k_len
            s_f.flush()
        after = datetime.now()
        logging.info("Standardized with [%s]‘%s’.", after-before, std_f_name)
        return std_f_name

    def parse(self, files:dict, std_word:StandardWord):
        replace = dict()
        for k, v in files.items():
            if "standardized" in v and len(v[c.STANDARDIZED]) > 0:
                logging.info("**omitted. uri:'%s' is standardized, '%s'.", k, v[c.STANDARDIZED])
                continue
            if c.DOWNLOAD in v and len(v[c.DOWNLOAD]) > 0:
                word_pair = std_word.get_word_pair(v[c.LANG_SRC], v[c.LANG_DST])
                std_f_name = self.parse_single(v[c.DOWNLOAD], word_pair, std_word.ext_property)
                v[c.STANDARDIZED] = std_f_name
