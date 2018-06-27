#!/usr/bin/env python
# coding=utf-8

from magnet_dht.crawler import start_server
from magnet_dht.magnet_to_torrent_aria2c import magnet2torrent
from magnet_dht.parse_torrent import parse_torrent


if __name__ == "__main__":
    start_server()
    # magnet2torrent()
    # parse_torrent()
