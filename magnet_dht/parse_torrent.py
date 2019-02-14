#!/usr/bin/env python
# coding=utf-8

import os
import codecs
from pprint import pprint

from bencoder import bdecode

TORRENT_SAVE_PATH = "torrents"


class ParserTorrent:
    def __init__(self, torrent):
        self.meta_info = self.get_meta_info(torrent)

    @staticmethod
    def get_meta_info(torrent):
        """
        返回解码后的 meta info 字典
        """
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
        """
        获取种子多个文件名
        """
        files = self.meta_info[b"info"][b"files"]
        info = []
        for item in files:
            for k, v in item.items():
                if isinstance(v, list):
                    try:
                        v = [i.decode() for i in v]
                    except:
                        continue
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

    def get_createby(self):
        """
        返回创建种子创建时间
        """
        if b"created by" in self.meta_info:
            return self.meta_info[b"created by"]


def parse_torrent():
    for _, _, files in os.walk(TORRENT_SAVE_PATH):
        for file in files:
            info = ParserTorrent(os.path.join(TORRENT_SAVE_PATH, file))
            print(TORRENT_SAVE_PATH, file)
            pprint(info.get_filename())
            print()
