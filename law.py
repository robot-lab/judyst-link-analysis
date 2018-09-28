import urllib
import re
import unicodedata
html = urllib.request.urlopen("http://www.ksrf.ru/ru/Decision/Pages/default.aspx")
htmlForParse = html.read()
htmlForParse =  htmlForParse.decode('utf-8', 'replace')
print(htmlForParse)

pdfLinks = re.findall(r'(http://doc.ksrf.ru/decision/KSRFDecision\d{6}\b\.pdf|http://doc.ksrf.ru/decision/KSRFDecision\d{5}\b\.pdf)', htmlForParse)
date = re.findall(r'\d\d\.\d\d\.\d{4}', htmlForParse)
uid = re.findall(r'(\d{4}-О/\d{4})|(ПР-\d{1}/\d{4})', htmlForParse)
print( uid)
# \d{2}-/2018
print(pdfLinks)
print(date)
#format {'uid': {'date': 'date string', 'url': 'link to pdf file'}}
# logo = urllib.urlopen("http://doc.ksrf.ru/decision/KSRFDecision343971.pdf").read()
# f = open("l.pdf", "wb")
# f.write(logo)
# f.close()