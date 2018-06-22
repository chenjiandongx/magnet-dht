#!/usr/bin/env python
# coding=utf-8

import os
import codecs
from pprint import pprint

from bencoder import bdecode


class ParserTorrent:

    def __init__(self, torrent):
        self.meta_info = self.get_meta_info(torrent)

    @staticmethod
    def get_meta_info(torrent):
        with open(torrent, "rb") as f:
            return bdecode(f.read())

    def is_files(self):
        """
        判断种子文件为单文件或者多文件
        """
        if b"files" in self.meta_info[b"info"]:
            return True
        return False

    def get_creation_date(self):
        if b"creation date" in self.meta_info:
            return self.meta_info[b"creation date"]

    def _get_single_filename(self):
        """
        获取种子单个文件名
        """
        info = self.meta_info[b"info"]
        if b"name.utf-8" in info:
            filename = info[b"name.utf-8"]
        else:
            filename = info[b"name"]
        for c in filename:
            if c == "'":
                filename = filename.replace(c, "\\'")
        return filename.decode()

    def _get_multi_filename(self):
        files = self.meta_info[b"info"][b"files"]
        info = []
        for item in files:
            for k, v in item.items():
                if isinstance(v, list):
                    v = [i.decode() for i in v]
                elif isinstance(v, int):
                    v = round(v / 1024 / 1024, 2)
                else:
                    v = codecs.getencoder("hex")(v)[0].decode()
                info.append((k.decode(), v))
        return info

    def get_filename(self):
        """
        获取种子文件名
        """
        if self.is_files():
            return self._get_multi_filename()
        else:
            return self._get_single_filename()

        # 返回创建时间

    def get_createby(self):
        """
        返回创建种子创建时间
        """
        if b"created by" in self.meta_info:
            return self.meta_info[b"created by"]


if __name__ == "__main__":
    for root, dirs, files in os.walk("torrents"):
        for file in files:
            torrent_info = ParserTorrent("torrents/" + file)
            print("torrent", file)
            pprint(torrent_info.get_filename())
            print()
