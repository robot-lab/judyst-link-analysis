import re
import sys

linkPattern = re.compile(
    r'[Оо].[\s\d]+[яфмаисонд]\w+[\s\d]+года[\s\d]+№[\s\d]+[-\w]+')
opinionPattern = re.compile(r'(?i)мнение\s+судьи\s+конституционного')


def get_rude_links(pathToTextFile):
    file = open(pathToTextFile, 'r', encoding="utf-8")
    text = file.read()
    file.close()
    opinion = opinionPattern.search(text)
    if opinion is not None:
        result = linkPattern.findall(text, endpos=opinion.start())
    else:
        result = linkPattern.findall(text)
    return result


def get_rude_links_for_multiple_docs(headers):
    rudeLinks = {}
    for decisionID in headers:
        if 'not unique' in headers[decisionID]:
            continue
        rudeLinks[decisionID] = get_rude_links(
            headers[decisionID]['path to text file'])
    return rudeLinks


if (__name__ == '__main__'):
    dictoftexts = {
        '35-П/2018': {
            'date': 'str',
            'url': 'some_url',
            'path to text file': r'C:\VS Code Python projects\GetAllBase' +
                                 r'KSRF\Decision files\5-П_2017.txt',
            'title': 'Full title'}
            }
    print(get_rude_links_for_multiple_docs(dictoftexts))
