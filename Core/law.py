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
<<<<<<< HEAD
print (uid)
# |(\d{3}-О/\d{4})|(\d{2}-О/\d{4})|(\d{1}-О/\d{4})
# |(\d{3}-ПРП/\d{4})|(\d{2}-ПРП/\d{4})|(\d{1}-ПРП/\d{4})|(ПР-\d{1}/\d{4})|(\d{3}-П/\d{4})|(\d{2}-П/\d{4})|(\d{1}-П/\d{4})
# |(\d{3}-Р/\d{4})|(\d{2}-Р/\d{4})|(\d{1}-Р/\d{4})|(\d{4}-О-Р/\d{4})|(\d{3}-О-Р/\d{4})|(\d{2}-О-Р/\d{4})|(\d{1}-О-Р/\d{4})
print (pdfLinks)
print (date)
=======
print( uid)
# \d{2}-/2018
print(pdfLinks)
print(date)
>>>>>>> bf12e3962d94f8347ea665260e2007b8b4e9aae5
#format {'uid': {'date': 'date string', 'url': 'link to pdf file'}}
# logo = urllib.urlopen("http://doc.ksrf.ru/decision/KSRFDecision343971.pdf").read()
# f = open("l.pdf", "wb")
# f.write(logo)
# f.close()