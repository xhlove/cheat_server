#!/usr/bin/env python3.7
# coding=utf-8
'''
# 作者: weimo
# 创建日期: 2020-01-18 01:01:09
# 上次编辑时间: 2020-02-22 18:35:25
# 一个人的命运啊,当然要靠自我奋斗,但是...
'''
import os
import sys
import json
import chardet
import datetime
import email.utils
import urllib.parse
from http import HTTPStatus
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler

def load_config():
    config = {}
    config_path = "config.json"
    if os.path.isfile(config_path):
        with open(config_path, "rb") as f:
            # 只读256是为了避免读取文件太大，虽然一般不会太大
            _encoding = chardet.detect(f.read(256))["encoding"]
        with open(config_path, "r", encoding=_encoding) as f:
            config = json.loads(f.read())
    return config

class MyHandler(SimpleHTTPRequestHandler):

    def __init__(self, *args, config: dict = {}, **kwargs):
        self.config = config
        kwargs["directory"] = os.path.join(os.getcwd(), config["scripts_path"])
        super().__init__(*args, **kwargs)

    def send_head(self):
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            parts = urllib.parse.urlsplit(self.path)
            if not parts.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(HTTPStatus.MOVED_PERMANENTLY)
                new_parts = (parts[0], parts[1], parts[2] + '/',
                             parts[3], parts[4])
                new_url = urllib.parse.urlunsplit(new_parts)
                self.send_header("Location", new_url)
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        try:
            fs = os.fstat(f.fileno())
            # Use browser cache if possible
            if ("If-Modified-Since" in self.headers
                    and "If-None-Match" not in self.headers):
                # compare If-Modified-Since and time of last file modification
                try:
                    ims = email.utils.parsedate_to_datetime(
                        self.headers["If-Modified-Since"])
                except (TypeError, IndexError, OverflowError, ValueError):
                    # ignore ill-formed values
                    pass
                else:
                    if ims.tzinfo is None:
                        # obsolete format with no timezone, cf.
                        # https://tools.ietf.org/html/rfc7231#section-7.1.1.1
                        ims = ims.replace(tzinfo=datetime.timezone.utc)
                    if ims.tzinfo is datetime.timezone.utc:
                        # compare to UTC datetime of last modification
                        last_modif = datetime.datetime.fromtimestamp(
                            fs.st_mtime, datetime.timezone.utc)
                        # remove microseconds, like in If-Modified-Since
                        last_modif = last_modif.replace(microsecond=0)

                        if last_modif <= ims:
                            self.send_response(HTTPStatus.NOT_MODIFIED)
                            self.end_headers()
                            f.close()
                            return None

            self.send_response(HTTPStatus.OK)
            # self.send_header("Content-type", ctype)
            # self.send_header("Content-Length", str(fs[6]))
            # self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.send_custom_header()
            self.end_headers()
            return f
        except:
            f.close()
            raise

    def send_custom_header(self):
        if self.path.startswith("/"):
            js_path = self.path.lstrip("/")
        else:
            js_path = self.path
        if self.config.get(js_path) is None:
            return
        headers = self.config[js_path]
        for key, value in headers.items():
            self.send_header(key, value)

    def send_response(self, code, message=None):
        self.log_request(code)
        self.send_response_only(code, message)
        # self.send_header('Server', self.version_string())
        # self.send_header('Date', self.date_time_string())

    def send_header(self, keyword, value):
        if self.request_version != 'HTTP/0.9':
            if not hasattr(self, '_headers_buffer'):
                self._headers_buffer = []
            self._headers_buffer.append(
                ("%s: %s\r\n" % (keyword, value)).encode('latin-1', 'strict'))

        if keyword.lower() == 'connection':
            if value.lower() == 'close':
                self.close_connection = True
            elif value.lower() == 'keep-alive':
                self.close_connection = False

def main():
    config = load_config()
    Handler = partial(MyHandler, config=config)
    server = HTTPServer((config["host"], config["port"]), Handler)
    print("Starting server, listen at: http://{host}:{port}".format(**config))
    server.serve_forever()

if __name__ == '__main__':
    main()