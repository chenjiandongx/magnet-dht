#!/usr/bin/env python
# coding=utf-8

import argparse

from magnet_dht.crawler import start_server
from magnet_dht.magnet_to_torrent_aria2c import magnet2torrent
from magnet_dht.parse_torrent import parse_torrent


def get_parser():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(description="start manage.py with flag.")
    parser.add_argument("-s", action="store_true", help="run start_server func.")
    parser.add_argument("-m", action="store_true", help="run magnet2torrent func")

    parser.add_argument("-p", action="store_true", help="run parse_torrent func")
    return parser


def command_line_runner():
    """
    执行命令行操作
    """
    parser = get_parser()
    args = vars(parser.parse_args())

    if args["s"]:
        start_server()
    elif args["m"]:
        magnet2torrent()
    elif args["p"]:
        parse_torrent()


if __name__ == "__main__":
    command_line_runner()
