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
USER_AGENT='Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like MAC OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Mobile/11D257 Chrome/54.0.2840.71 Safari/9537.53'

import os, logging
from datetime import datetime
import requests
from pathlib import Path
from tool import is_path_exists_or_creatable, get_valid_file_name
import constant as c


class Spider(object):
    def __init__(self, save_folder:str, *args, **kwargs):
        self._save_folder = save_folder

    def _parse(self, response:requests.Response):
        uri = Path(response.url).name
        file_name = "{}{}.html".format(datetime.now().strftime("%Y%m%d%H%M%S%f"), uri)
        if not is_path_exists_or_creatable(file_name):
            file_name = get_valid_file_name(file_name)
            # raise ValueError('Path is not valid:"{}".'.format(file_name))
        logging.info("date_str:%s", file_name)
        file_name = os.path.join(self._save_folder, file_name)
        logging.info("**try to save file[%s]:%s.", response.encoding, file_name) # encoding: utf-8
        logging.info("**url:%s", response.url)  # request link
        with open(file_name, "wb+") as f:
            f.write(response.content)
            f.flush()
        return (file_name, response.encoding)

    def start_single(self, uri, download):
        before = datetime.now()
        resp = requests.get(uri, headers={'user-agent': USER_AGENT})
        after = datetime.now()
        logging.info("responded with %s seconds.", after - before)
        return self._parse(resp)

    def start(self, links:dict):
        for k, v in links.items():
            logging.info("v:%s.%s", v, type(v[c.DOWNLOAD]))
            if 'download' in v and len(v[c.DOWNLOAD]) > 0:
                logging.info("**omitted. uri:'%s' is downloaded, '%s'.", k, v[c.DOWNLOAD])
                continue
            logging.info("**Requesting '%s'.", k)
            file_name, encoding = self.start_single(k, v[c.DOWNLOAD])
            logging.info("saved to '%s'", file_name)
            links[k][c.DOWNLOAD] = file_name
            links[k][c.ENCODING] = encoding

# Response Head.
# {
# 'strict-transport-security': 'max-age=2592000; includeSubDomains'
# , 'x-content-type-options': 'nosniff'
# , 'Content-Security-Policy': "script-src 'self' data: 'unsafe-inline' 'unsafe-eval' *.bootstrapcdn.com *.ampproject.org *.twitter.com *.twimg.com *.google-analytics.com *.youtube.com *.ytimg.com *.google.com *.gstatic.com    ; img-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob: *.twimg.com *.ytimg.com *.twitter.com storage.googleapis.com *.googleusercontent.com *.google-analytics.com *.ampproject.org *.gravatar.com *.google.com *.gstatic.com; default-src 'self'; frame-src 'self' *.twitter.com *.googleapis.com *.youtube.com *.ampproject.org *.google.com; style-src 'self' 'unsafe-inline' 'unsafe-eval' *.twitter.com *.twimg.com *.ampproject.org *.google.com; media-src 'self' storage.googleapis.com *.google.com; connect-src 'self' *.twitter.com *.googleapis.com *.youtube.com *.ampproject.org *.google.com *.google-analytics.com; font-src 'self' data: storage.googleapis.com *.google-analytics.com 'unsafe-inline' 'unsafe-eval' *.bootstrapcdn.com *.ampproject.org"
# , 'Expires': 'Mon, 28 Aug 2017 02:18:08 GMT'
# , 'Vary': 'Cookie, Accept-Encoding'
# , 'Last-Modified': 'Mon, 28 Aug 2017 02:17:38 GMT'
# , 'x-xss-protection': '1; mode=block'
# , 'Cache-Control': 'max-age=30'
# , 'X-Frame-Options': 'SAMEORIGIN'
# , 'Content-Type': 'text/html; charset=utf-8'
# , 'Content-Encoding': 'gzip'
# , 'X-Cloud-Trace-Context': 'b5abf27dd75e702905f5a2ffbdbb975b;o=1'
# , 'Date': 'Mon, 28 Aug 2017 02:17:38 GMT'
# , 'Server': 'Google Frontend'
# , 'Transfer-Encoding': 'chunked'
# }
