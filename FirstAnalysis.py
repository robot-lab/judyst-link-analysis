import re

def GetRudeLinks(filename):
    file = open(filename,'r', encoding="utf-8")
    R = file.read()
    file.close()
    n = R.find('Мнение судьи Конст')
    R = R[0:n] #to do:optimize

    pattern = re.compile(r'[Оо][Tт][\s\d]+[яфмаисонд]\w+[\s\d]+года[\s\d]+№[\s\d]+[-\w]+')
    result = pattern.findall(R)
    return result    

def GetRudeLinksForMultipleDocuments(dictoftexts):
    dictofrudelinks = {}
    for key in sorted(dictoftexts):
        dictofrudelinks[key] = GetRudeLinks(dictoftexts[key]['url'])
    return dictofrudelinks

if (__name__ == '__main__'):
    dictoftexts = {'35-П/2018':{'date':'str','url': r'Decision Files\2043-О_2018.txt','title':'Full title'}}
    print (GetRudeLinksForMultipleDocuments(dictoftexts))
