import re
pattern = re.compile(
    r'[Оо].[\s\d]+[яфмаисонд]\w+[\s\d]+года[\s\d]+№[\s\d]+[-\w]+')


def GetRudeLinks(filename):
    file = open(filename, 'r', encoding="utf-8")
    R = file.read()
    file.close()
    Slice = re.split(r'[Мм]нение\s[Сс]удьи\s[Кк]онст', R, maxsplit=1)
    result = pattern.findall(Slice[0])
    return result


def GetRudeLinksForMultipleDocuments(dictoftexts):
    dictofrudelinks = {}
    for key in sorted(dictoftexts):
        dictofrudelinks[key] = GetRudeLinks(dictoftexts[key]['url'])
    return dictofrudelinks


if (__name__ == '__main__'):
    dictoftexts = {
        '35-П/2018': {
            'date': 'str',
            'url': r'C:\Users\GameOS\Desktop\Grub\input1.txt',
            'title': 'Full title'}
            }
    print(GetRudeLinksForMultipleDocuments(dictoftexts))
