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


import constant as C, config as CONF
import log, logging as lg
import unittest
from copy import deepcopy
from datetime import datetime
import pandas as pd, numpy as np
from tool import get_root
from container.term import Terminology
from mini_spider.spider import Spider
from translation.standardizors import Standardizor


class TestTranslation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.log = lg.getLogger(__name__)
        # cls.log.info("setUpClass.\n")
        cls.root = get_root()
        cls.download_path = cls.root.joinpath(CONF.DIR_DOWNLOAD)
        cls.standardized_path = cls.root.joinpath(CONF.DIR_STANDARDIZED)
        if not cls.download_path.exists():
            cls.download_path.mkdir()
        if not cls.standardized_path.exists():
            cls.standardized_path.mkdir()
        cls.term_file = cls.root.joinpath(CONF.DIR_DATA, CONF.DIR_TERM, CONF.TERMNINOLOGY_FILE)


    # @classmethod
    # def tearDownClass(cls):
    #     cls.log.info("tearDownClass\n")

    # def setUp(self):
    #     self.log.info("setup\n")

    # def tearDown(self):
    #     self.log.info("tearDown\n")


    # @unittest.skip("disable for debug")
    def test_spider_agent(self):
        # python -m unittest test.test_translation.TestTranslation.test_spider_agent
        urls = {"https://deepmind.com/blog/ai-and-neuroscience-virtuous-circle/":{C.REQ_DOWNLOAD:"", C.REQ_STANDARDIZED:""}}
        sa = Spider(self.download_path)
        sa.start(urls)


    def test_standardized(self):
        # python -m unittest test.test_translation.TestTranslation.test_spider_agent
        file = {
            "https://deepmind.com/blog/ai-and-neuroscience-virtuous-circle/": 
            {
                C.DOWNLOAD:r"C:\projects\personal\TranslationPipe\download\20170828115408438438.html", C.REQ_STANDARDIZED:""
            }
        }
        term = Terminology(self.term_file)
        tran = Standardizor(self.standardized_path)
        tran.parse(file, term)
        self.log.info(file)

    def test_terminology(self):
        # python -m unittest test.test_translation.TestTranslation.test_terminology
        self.log.info(f'term_file:{self.term_file}')
        term = Terminology(self.term_file)
        # self.log.info(term.term)
        self.assertEqual(type(term.term), pd.DataFrame)


if __name__ == '__main__':
    unittest.main()