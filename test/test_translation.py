#!/usr/bin/python3.6
# -*- coding: UTF-8 -*-

import logging, os
from tool import get_root
logging.basicConfig(
    format='[%(filename)s:%(lineno)s %(asctime)s %(levelname)s %(funcName)16s()]\n%(message)s'
    , datefmt='%Y%m%d-%H%M%S', level=logging.INFO
    , filename=str(get_root().joinpath("test_translation.log")))
import unittest
from container.std_word import StandardWord
from copy import deepcopy
from datetime import datetime
from mini_spider.spiders import Spider
from translation.translations import Translation



class TestAlgorithm(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.info("setUpClass.\n")
        cls._download_path = str(get_root().joinpath("download"))
        cls._standardized_path = str(get_root().joinpath("standardized"))
        if not os.path.exists(cls._download_path):
            os.mkdir(cls._download_path)
        if not os.path.exists(cls._standardized_path):
            os.mkdir(cls._standardized_path)
        cls._csds_xlsx_file = get_root().joinpath("data", "cs-ds", "standard_word.xlsx")
        cls._csds_col = {'en': [1, 2], 'zh-cn': [3]}
        cls._csds_container = [cls._csds_xlsx_file, "xlsx_file", cls._csds_col]

    @classmethod
    def tearDownClass(cls):
        logging.info("tearDownClass\n")

    def setUp(self):
        logging.info("setup\n")

    def tearDown(self):
        logging.info("tearDown\n")

    @unittest.skip("disable for debug")
    def test_container(self):
        s_w = StandardWord(*self._csds_container)
        print(s_w._dict)
        print(s_w.get_keyword('en', 'zh-cn'))
        print(s_w.get_keyword('zh-cn', 'en'))

    @unittest.skip("disable for debug")
    def test_spider_agent(self):
        urls = {"https://deepmind.com/blog/ai-and-neuroscience-virtuous-circle/":{"download":"", "standardized":""}}
        sa = Spider(urls, self._download_path)
        sa.start()

    def test_standardized(self):
        file = {"https://deepmind.com/blog/ai-and-neuroscience-virtuous-circle/": {"download":r"C:\projects\personal\TranslationPipe\download\20170828115408438438.html", "standardized":""}}
        s_w = StandardWord(*self._csds_container)
        tran = Translation(s_w, self._standardized_path)
        tran.parse(file, 'en', 'zh-cn')
        print(file)


if __name__ == '__main__':
    logging.info("__main__\n")
    unittest.main()