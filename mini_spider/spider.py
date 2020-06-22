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


from typing import List, AnyStr, Dict, Any, Tuple
import log, logging as l
import constant as C
from datetime import datetime
import requests as r
from pathlib import Path
from tool import is_path_exists_or_creatable, get_valid_file_name


class Spider(object):
    r"""Spider: download webpage to specific local path as html files.

    parameters
    ----------
    save_folder: str
        the root folder of downloaded web page.
    """

    USER_AGENT='Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like MAC OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Mobile/11D257 Chrome/54.0.2840.71 Safari/9537.53'


    def __init__(self, save_folder:Path, **kwargs):
        self.log = l.getLogger(__name__)
        self._save_folder:Path = save_folder


    def _parse(self, resp: r.Response) -> (Path, str):
        uri = Path(resp.url).name
        file_name = f'{datetime.now().strftime("%Y%m%d%H%M%S%f")}{uri}.html'
        if not is_path_exists_or_creatable(file_name):
            file_name = get_valid_file_name(file_name)
        # self.log.info(f"file_name:{file_name}")
        file_name = self._save_folder.joinpath(file_name)
        # self.log.info(f"**try to save file[{resp.encoding}]:{file_name}") # encoding: utf-8
        # self.log.info(f"**url:{resp.url}")  # request link
        with open(file_name, "wb+") as f:
            f.write(resp.content)
            f.flush()
        return (file_name, resp.encoding)


    def start_single(self, uri:AnyStr, download:Path=None) -> (Path, str):
        r"""Start download and save content to a local path.

        parameters
        ----------
        uri: str. The uri of the content from internet.

        returns
        -------
        Return content save full path and encoding of the content.
        """
        before = datetime.now()
        resp = r.get(uri, headers={'user-agent': self.USER_AGENT})
        after = datetime.now()
        res:Tuple = self._parse(resp)
        self.log.info(f"Downloaded '{uri}' to '{res[0]}' with {after - before} seconds")
        return res


    def start(self, links: dict):
        for k, v in links.items():
            self.log.info(f"v:{v}.{v[C.REQ_DOWNLOAD]}")
            if C.REQ_DOWNLOAD in v and len(v[C.REQ_DOWNLOAD]) > 0:
                self.log.info(f"**omitted. uri:'{k}' is downloaded, '{v[C.REQ_DOWNLOAD]}'")
                continue
            self.log.info(f"**Requesting '{k}'")
            file_name, encoding = self.start_single(k, v[C.REQ_DOWNLOAD])
            self.log.info(f"saved to '{file_name}'")
            links[k][C.REQ_DOWNLOAD] = file_name
            links[k][C.REQ_ENCODING] = encoding


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
