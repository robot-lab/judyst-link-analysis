import re
import sys

pattern = re.compile(
    r'[Оо].[\s\d]+[яфмаисонд]\w+[\s\d]+года[\s\d]+№[\s\d]+[-\w]+')


def get_rude_links(pathToTextFile, decisionID):
    file = open(pathToTextFile, 'r', encoding="utf-8")
    text = file.read()
    file.close()
    docNumber = re.split(r'/', decisionID)[0]
    opinion = re.search('№ ' + docNumber, text)
    endpos = opinion.start() if opinion else sys.maxsize
    result = pattern.findall(text, endpos=endpos)
    return result


def get_rude_links_for_multiple_docs(headers):
    rudeLinks = {}
    for decisionID in headers:
        if 'not unique' in headers[decisionID]:
            continue
        rudeLinks[decisionID] = get_rude_links(
            headers[decisionID]['path to text file'], decisionID)
    return rudeLinks


if (__name__ == '__main__'):
    dictoftexts = {
        '35-П/2018': {
            'date': 'str',
            'url': 'some_url',
            'path to text file': r'C:\Users\GameOS\Desktop\Grub\input1.txt',
            'title': 'Full title'}
            }
    print(get_rude_links_for_multiple_docs(dictoftexts))
