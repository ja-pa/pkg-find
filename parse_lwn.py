#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 10:25:01 2021

"""

import requests
from bs4 import BeautifulSoup


def get_lwn_links():
    r = requests.get('https://www.lwn.net', allow_redirects=True)
    soup = BeautifulSoup(r.content, 'lxml')
    is_security = False
    security_links = []

    for tag in soup.find_all():
        if tag.name == "h2" or tag.name == "a":
            text = tag.text.strip()
            find_head = text.find("Security updates for")
            find_link = text.find("Full Story")
            if find_head >= 0:
                is_security = True
            if find_link >= 0 and is_security is True:
                url = str(tag).split('"')[1]
                security_links.append("https://lwn.net" + url)
                is_security = False
    return security_links


def get_lwn_article(url):
    r = requests.get(url, allow_redirects=True)
    soup = BeautifulSoup(r.content, 'lxml')
    table_list = []

    for row in soup.find_all("tr"):
        cells = [item.text for item in row.find_all("td")]
        if cells:
            table_list.append(cells)
    return table_list


def parse_pkg(pkg_text_raw):
    valid_names = [
        "Architecture", "CPE-ID", "Depends", "Description",
        "Essential", "Filename", "Installed-Size", "License",
        "NOTE", "Package", "Provides", "Section",
        "SHA256sum", "Size", "Status", "Version"
        ]
    pkg = {}
    for line in pkg_text_raw.splitlines():
        pkg_item = line.split(":", 1)
        if len(pkg_item) == 2:
            name, val = pkg_item
            if name in valid_names:
                pkg[name] = val.strip()
    return pkg


def parse_pkg_list(url):
    r = requests.get(url, allow_redirects=True)

    package_raw_split = r.text.split("\n\n")
    pkg_list = []
    for item in package_raw_split:
        pkg = parse_pkg(item)
        if bool(pkg):
            pkg_list.append(pkg)
    return pkg_list


uu = parse_pkg_list("https://downloads.openwrt.org/snapshots/targets/mvebu/cortexa53/packages/Packages")
