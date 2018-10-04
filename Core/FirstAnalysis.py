import re
import sys
pattern = re.compile(
    r'[Оо].[\s\d]+[яфмаисонд]\w+[\s\d]+года[\s\d]+№[\s\d]+[-\w]+')


def GetRudeLinks(filename, key):
    file = open(filename, 'r', encoding="utf-8")
    text = file.read()
    file.close()
    Slice = re.split(r'/', key)
    key = Slice[0]
    Opinion = re.search('№ ' + key, text)
    endpos = Opinion.start() if Opinion != None else sys.maxsize
    result = pattern.findall(text, endpos= endpos)
    return result

def GetRudeLinksForMultipleDocuments(dictoftexts):
    dictofrudelinks = {}
    for key in dictoftexts:
        dictofrudelinks[key] = GetRudeLinks(dictoftexts[key]['url'], key)
    return dictofrudelinks


if (__name__ == '__main__'):
    dictoftexts = {
        '35-П/2018': {
            'date': 'str',
            'url': r'C:\Users\GameOS\Desktop\Grub\input1.txt',
            'title': 'Full title'}
            }
    print(GetRudeLinksForMultipleDocuments(dictoftexts))