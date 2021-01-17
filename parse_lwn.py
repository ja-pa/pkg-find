#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 10:25:01 2021

"""

import requests
from bs4 import BeautifulSoup


def get_url(text, return_first=True):
    soup = BeautifulSoup(text, 'lxml')
    tmp = []
    for link in soup.findAll('a'):
        tmp.append(link.get('href'))
    if return_first:
        if len(tmp) >= 1:
            return tmp[0]
        else:
            return ""
    return tmp


class Lwn:
    def __init__(self):
        pass

    def get_security_urls(self):
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

    def parse_security_tbl(self, url):
        # Dist. 	ID 	Release 	Package 	Date
        r = requests.get(url, allow_redirects=True)
        soup = BeautifulSoup(r.content, 'lxml')
        table_list = []

        for row in soup.find_all("tr"):
            url = get_url(str(row))
            cells = [item.text for item in row.find_all("td")]
            if cells:
                dist, dist_id, release, package, sec_date = cells
                package_list = [pkg.strip() for pkg in package.split(",")]
                item = {"Dist": dist, "ID": dist_id, "Release": release,
                        "Package": package_list, "Date": sec_date, "URL": url}
                table_list.append(item)
        return table_list


class OpenWrtPkg:
    def __init__(self, urls=["https://downloads.openwrt.org/snapshots/targets/mvebu/cortexa53/packages/Packages"]):
        self.pkg_list_url = urls
        self.pkg_list = []

        # Parse all packages from url list
        for url in urls:
            self.pkg_list = self.pkg_list + self._parse_pkg_list(url)

    def _parse_pkg(self, pkg_text_raw):
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

    def _parse_pkg_list(self, url):
        r = requests.get(url, allow_redirects=True)
        package_raw_split = r.text.split("\n\n")
        pkg_list = []
        for item in package_raw_split:
            pkg = self._parse_pkg(item)
            if bool(pkg):
                pkg_list.append(pkg)
        return pkg_list

    def find_pkgs(self, pkg_name, exact_match=True):
        ret = []
        for item in self.pkg_list:
            if exact_match is True:
                if item["Package"] == pkg_name:
                    ret.append(item)
            else:
                tmp_pkg = item["Package"].lower()
                if tmp_pkg.find(pkg_name.lower()) >= 0:
                    ret.append(item)
        return ret


urls = [
      "https://downloads.openwrt.org/snapshots/targets/mvebu/cortexa53/packages/Packages",
      "https://downloads.openwrt.org/snapshots/packages/aarch64_cortex-a53/packages/Packages"
      ]
owrt = OpenWrtPkg(urls)

"""
print(len(aa.pkg_list))
uu=aa.find_pkgs("tor",True)
"""

ll = Lwn()
#sec_url = ll.get_security_urls()
#url = sec_url[0]

for url in ll.get_security_urls():
    for sec_item in ll.parse_security_tbl(url):
        for pkg in sec_item["Package"]:
            #find_pkgs = owrt.find_pkgs(pkg)
            for found_pkg in owrt.find_pkgs(pkg):
                
                if found_pkg:
                    print("Lwn", sec_item["URL"])
                    print()
                    print("Owrt", found_pkg["Package"], found_pkg["Version"])
