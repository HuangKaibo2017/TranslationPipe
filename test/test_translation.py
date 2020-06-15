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
        tran = Standardizor(self._standardized_path)
        tran.parse(file, s_w)
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