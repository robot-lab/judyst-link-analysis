#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
import urllib
import re
html = urllib.urlopen("http://www.ksrf.ru/ru/Decision/Pages/default.aspx")
htmlForParse = html.read()
htmlForParseU =  unicode(htmlForParse, "utf-8")
pdfLinks = re.findall(r'(http://doc.ksrf.ru/decision/KSRFDecision\d{6}\b\.pdf|http://doc.ksrf.ru/decision/KSRFDecision\d{5}\b\.pdf)', htmlForParse)
date = re.findall(r'\d\d\.\d\d\.\d{4}', htmlForParse)
uid = re.findall(r'(\d{4}-О/\d{4})|(ПР-\d{1}/\d{4})', htmlForParse)
print uid
# |(\d{3}-О/\d{4})|(\d{2}-О/\d{4})|(\d{1}-О/\d{4})
# |(\d{3}-ПРП/\d{4})|(\d{2}-ПРП/\d{4})|(\d{1}-ПРП/\d{4})|(ПР-\d{1}/\d{4})|(\d{3}-П/\d{4})|(\d{2}-П/\d{4})|(\d{1}-П/\d{4})
# |(\d{3}-Р/\d{4})|(\d{2}-Р/\d{4})|(\d{1}-Р/\d{4})|(\d{4}-О-Р/\d{4})|(\d{3}-О-Р/\d{4})|(\d{2}-О-Р/\d{4})|(\d{1}-О-Р/\d{4})
print pdfLinks
print date
#format {'uid': {'date': 'date string', 'url': 'link to pdf file'}}
# logo = urllib.urlopen("http://doc.ksrf.ru/decision/KSRFDecision343971.pdf").read()
# f = open("l.pdf", "wb")
# f.write(logo)
# f.close()