#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import textwrap
import sys

import re
from collections import OrderedDict
from xlwt import Workbook
from lxml import etree

pattern = re.compile(r'</p>|<p>\n')


class XML2ExcelManager:

    def __init__(self, xml_file_name):
        self._tree = etree.parse(xml_file_name)
        self.root = self._tree.getroot()
        #suite_depth = 0
        self.content = []
        
    def xmlnode_to_list(self, node):
        dict = (
           ("suitename", ""),
           ("casename", ""),
           ("preconditions", ""),
           ("steps", ""),
           ("expected", ""),
           ("keywords", ""),
           ("caseid", "")
        )
        line = OrderedDict(dict)
        if node.tag == 'testsuite':
            line["suitename"] = node.get("name")
            self.content.append(line)
        if node.tag == 'testcase':
            line["casename"] = node.get("name")
            line["caseid"] = node.find("externalid").text
            line["preconditions"] = node.find("preconditions").text
            line["steps"] = node.find("steps/step/actions").text
            line["expected"] = node.find("steps/step/expectedresults").text
            line["keywords"] = []
            for keyword in node.findall("keywords/keyword"):
                line["keywords"].append(keyword.get("name"))
            self.content.append(line)
        for child in node.getchildren():
            self.xmlnode_to_list(child)

    def write_list_to_excel(self, excel_file_name):
        excel = Workbook()
        sheet1 = excel.add_sheet('Sheet1')
        # write title name
        row = sheet1.row(0)
        for idx, key in enumerate(self.content[0]):
            row.write(idx, key)

        for i in range(len(self.content)):
            row = sheet1.row(i+1)  # Offset for title
            for idx, key in enumerate(self.content[i]):
                val = self.content[i][key]
                if key!="keywords": # Because keywords is list, not string
                    val = pattern.sub('', val)
                else:
                    val = '\n'.join(val)
                row.write(idx, val)
        excel.save(excel_file_name)

if __name__ == '__main__':
    input=raw_input("Input excel name:")
    xem = XML2ExcelManager(input)
    xem.xmlnode_to_list(xem.root)
    xem.write_list_to_excel('output.xls')

