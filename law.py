import urllib.request
import re
import unicodedata
import os.path
from inspect import getsourcefile

def GetResolutionHeaders():
	html = urllib.request.urlopen("http://www.ksrf.ru/ru/Decision/Pages/default.aspx")
	htmlForParse = html.read()
	htmlForParse =  htmlForParse.decode('utf-8', 'replace')
	# print(htmlForParse)
	pdfLinks = re.findall(r'(http://doc.ksrf.ru/decision/KSRFDecision\d{6}\b\.pdf|http://doc.ksrf.ru/decision/KSRFDecision\d{5}\b\.pdf)', htmlForParse)
	date = re.findall(r'\d\d\.\d\d\.\d{4}', htmlForParse)
	uid = re.findall(r'(\d{4}-О/\d{4})|(\d{3}-О/\d{4})|(\d{2}-О/\d{4})|(\d{1}-О/\d{4})|(\d{3}-ПРП/\d{4})|(\d{2}-ПРП/\d{4})|(\d{1}-ПРП/\d{4})|(ПР-\d{1}/\d{4})|(\d{3}-П/\d{4})|(\d{2}-П/\d{4})|(\d{1}-П/\d{4})|(\d{3}-Р/\d{4})|(\d{2}-Р/\d{4})|(\d{1}-Р/\d{4})|(\d{4}-О-Р/\d{4})|(\d{3}-О-Р/\d{4})|(\d{2}-О-Р/\d{4})|(\d{1}-О-Р/\d{4})', htmlForParse) #|(ПР-\d{1}/\d{4})
	uid = [[uid[i][j] for j in range(len(uid[i])) if uid[i][j] != '' ] for i in range(len(uid))]
	uid = [uid[i][0] for i in range(len(uid))]
	result = {}
	for i in range(0,len(uid)):
		result[uid[i]] = {'date': date[i], 'link': pdfLinks[i]}
	print(result)
	return result

def LoadResolutionTexts(result, folderName = "Decision Files"):
	for key in result:
		a = result[key]
		logo = urllib.request.urlopen(a["link"]).read()
		folderName = os.path.join(os.path.abspath(os.path.dirname(getsourcefile(lambda:0))))
		print(folderName)

		fileName = os.path.join(folderName, key + ".pdf")
		f = open(fileName,"wb")
		f.write(logo)
		f.close()

LoadResolutionTexts(GetResolutionHeaders())