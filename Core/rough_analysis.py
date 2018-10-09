import re
import sys

linkPattern = re.compile(
 r'(?i)от[\s\d]+[яфмаисонд]\w+[\s\d]+года[\s\d]+№[\s\d]+[-\w]+[^.)(]*?[)(\.]')
splitPattern = re.compile(r'(?i)о(?=т[\s\d]+[яфмаисонд]\w+[\s\d]+года)')
datePattern = re.compile(r'(?i)т[\s\d]+[яфмаисонд]\w+[\s\d]+года')
numberPattern = re.compile(r'№[\s\d]+[-\w]+')
opinionPattern = re.compile(r'(?i)мнение\s+судьи\s+конституционного')


def get_rude_links(pathToTextFile):
    file = open(pathToTextFile, 'r', encoding="utf-8")
    text = file.read()
    file.close()
    roughLinks = []
    opinion = opinionPattern.search(text)
    if opinion is not None:
        parsed = linkPattern.findall(text, endpos=opinion.start())
    else:
        parsed = linkPattern.findall(text)
    for linksForSplit in parsed:
        splitedLinksForDifferentYears = splitPattern.split(linksForSplit)[1:]
        for oneYearLinks in splitedLinksForDifferentYears:
            date = datePattern.search(oneYearLinks)[0]
            numbers = numberPattern.findall(oneYearLinks)
            for number in numbers:
                roughLinks.append('о' + date + ' ' + number)
    return roughLinks


def get_rude_links_for_multiple_docs(headers):
    rudeLinks = {}
    for decisionID in headers:
        if 'not unique' in headers[decisionID]:
            continue
        rudeLinks[decisionID] = get_rude_links(
            headers[decisionID]['path to text file'])
    return rudeLinks


if (__name__ == '__main__'):
    # dictoftexts = {
    #     '35-П/2018': {
    #         'date': 'str',
    #         'url': 'some_url',
    #         'path to text file': r'C:\VS Code Python projects\GetAllBase' +
    #                              r'KSRF\Decision files\5-П_2017.txt',
    #         'title': 'Full title'}
    #         }
    # print(get_rude_links_for_multiple_docs(dictoftexts))
    roughLinks = get_rude_links('841-О_2018.txt')
    print(roughLinks)
    input()
