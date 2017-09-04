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
from translation.standardizors import Standardizor
from requirement import Requirement
import constant as c

class TestAlgorithm(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.info("setUpClass.\n")
        cls._download_path = str(get_root().joinpath(c.DOWNLOAD))
        cls._standardized_path = str(get_root().joinpath(c.STANDARDIZED))
        if not os.path.exists(cls._download_path):
            os.mkdir(cls._download_path)
        if not os.path.exists(cls._standardized_path):
            os.mkdir(cls._standardized_path)
        cls._csds_xlsx_file = str(get_root().joinpath(c.DATA, c.CS_DS))
        cls._csds_col = {'en': [1, 2], 'zh-cn': [3]}
        cls._csds_container = [cls._csds_xlsx_file, c.TYPE_FILE_XLSX]

    @classmethod
    def tearDownClass(cls):
        logging.info("tearDownClass\n")

    def setUp(self):
        logging.info("setup\n")

    def tearDown(self):
        logging.info("tearDown\n")


    def test_container(self):
        s_w = StandardWord(*self._csds_container)
        print(s_w._dict)
        print(s_w.get_word_pair('en', 'zh-cn'))
        print(s_w.get_word_pair('zh-cn', 'en'))

    @unittest.skip("disable for debug")
    def test_spider_agent(self):
        urls = {"https://deepmind.com/blog/ai-and-neuroscience-virtuous-circle/":{c.DOWNLOAD:"", c.STANDARDIZED:""}}
        sa = Spider(self._download_path)
        sa.start(urls)

    @unittest.skip("disable for debug")
    def test_standardized(self):
        file = {"https://deepmind.com/blog/ai-and-neuroscience-virtuous-circle/": {c.DOWNLOAD:r"C:\projects\personal\TranslationPipe\download\20170828115408438438.html", c.STANDARDIZED:""}}
        s_w = StandardWord(*self._csds_container)
        tran = Standardizor(s_w, self._standardized_path)
        tran.parse(file, 'en', 'zh-cn')
        print(file)

    @unittest.skip("disable for debug")
    def test_request_list(self):
        root = str(get_root().joinpath(c.DATA, c.REQUIREMENT))
        rl = Requirement(root)
        rl.load_info()
        print(rl.info)

if __name__ == '__main__':
    logging.info("__main__\n")
    unittest.main()