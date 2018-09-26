import urllib
f = urllib.urlopen("http://www.ksrf.ru/ru/Decision/Pages/default.aspx")
print f.read()
logo = urllib.urlopen("http://doc.ksrf.ru/decision/KSRFDecision343971.pdf").read()
f = open("l.pdf", "wb")
f.write(logo)
f.close()