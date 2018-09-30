import re

def GetRudeLinks(filename):
    file = open(filename,'r')
    R = file.read()
    file.close()
    n = R.find('Мнение судьи Конст')
    R = R[0:n] #to do:optimize

    pattern = re.compile(r'[Оо].[ \d]+[яфмаисонд]\w+[ \d]+года[ \d]+№[ \d]+[^ ),]+')
    result = pattern.findall(R)
    return result    

def GetRudeLinksForMultipleDocuments(dictoftexts):
    dictofrudelinks = {}
    for key in sorted(dictoftexts):
        dictofrudelinks[key] = GetRudeLinks(dictoftexts[key]['url'])
    return dictofrudelinks

if (__name__ == '__main__'):
    dictoftexts = {'35-П/2018':{'date':'str','url': r'C:\Users\GameOS\Desktop\Grub\input.txt','title':'Full title'}}
    print (GetRudeLinksForMultipleDocuments(dictoftexts))
