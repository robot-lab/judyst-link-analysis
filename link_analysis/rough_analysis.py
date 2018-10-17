import re
import sys
from link_analysis.models import Header, RoughLink

linkPattern = re.compile(
    r"(?<=\.\s)\s*?[А-Я][^\.!?]*?\sот[\s\d]+?(?:(?:января|февраля|марта|апреля"
    r"мая|июня|июля|августа|сентября|октября|ноября|декабря)+?[\s\d]+?года|"
    r"\d{2}\.\d{2}\.\d{4})[\s\d]+?(№|N)[\s\d]+?[-\w/]*[^\.!?]*?\..*?"
    r"(?=\s[А-Я])")
splitPattern = re.compile(
    r"(?i)о(?=т[\s\d]+?(?:(?:января|февраля|марта|апреля|мая|июня|июля|августа"
    r"|сентября|октября|ноября|декабря)+?[\s\d]+?года|\d{2}\.\d{2}\.\d{4})"
    r"(?=\s))")
datePattern = re.compile(
    r"(?i)т[\s\d]+?(?:(?:января|февраля|марта|апреля|мая|июня|июля|августа"
    r"|сентября|октября|ноября|декабря)+?[\s\d]+?года|\d{2}\.\d{2}\.\d{4})"
    r"(?=\s)")
numberPattern = re.compile(r'(?:№|N)[\s\d]+[-\w/]*')
opinionPattern = re.compile(r'(?i)мнение\s+судьи\s+конституционного')


def get_rough_links(header: Header):
    """
    :param header: instance of class models.Header
    """
    try:
        with open(header.text_location, 'r', encoding="utf-8") as file:
            text = file.read()
    except TypeError:
        return TypeError
    except FileNotFoundError:
        return FileNotFoundError
    roughLinks = []
    opinion = opinionPattern.search(text)
    if opinion is not None:
        matchObjects = linkPattern.finditer(text, endpos=opinion.start())
    else:
        matchObjects = linkPattern.finditer(text)
    for match in matchObjects:
        linksForSplit = match[0]
        context = linksForSplit
        position = match.start(0) + len(splitPattern.split(linksForSplit,
                                        maxsplit=1)[0]) + 1
        splitedLinksForDifferentYears = splitPattern.split(linksForSplit)[1:]
        for oneYearLinks in splitedLinksForDifferentYears:
            date = datePattern.search(oneYearLinks)[0]
            numbers = numberPattern.findall(oneYearLinks)
            for number in numbers:
                gottenRoughLink = 'о' + date + ' ' + number.upper()
                roughLinks.append(RoughLink(header, context, gottenRoughLink,
                                  position))
            position += len(oneYearLinks) + 1
    return roughLinks


PATH_NONE_VALUE_KEY = 'path has None value'
PATH_NOT_EXIST_KEY = 'path does not exist'


def get_rough_links_for_multiple_docs(headers: dict):
    """
    :param header: dict of instances of class models.Header
    return dict of lists of class RoughLink, also this dict may contain
    two lists of instances of class models.Header which were
    unsuccessfully processed
    """
    result = {}
    for decisionID in headers:
        maybeRoughLinks = get_rough_links(headers[decisionID])
        if maybeRoughLinks is TypeError:
            if PATH_NONE_VALUE_KEY not in result:
                result[PATH_NONE_VALUE_KEY] = []
            result[PATH_NONE_VALUE_KEY].append(headers[decisionID])
            continue
        if maybeRoughLinks is FileNotFoundError:
            if PATH_NOT_EXIST_KEY not in result:
                result[PATH_NOT_EXIST_KEY] = []
            result[PATH_NOT_EXIST_KEY].append(headers[decisionID])
            continue
        result[decisionID] = maybeRoughLinks
    return result


if (__name__ == '__main__'):
    from datetime import date
    h1 = Header('2028-О/2018', 'КС_РФ/О', 'some title1', date(2018, 7, 17),
                'http://doc.ksrf.ru/decision/KSRFDecision353855.pdf',
                r'Decision files\2028-О_2018.txt')
    h2 = Header('36-П/2018', 'КС_РФ/П', 'some title2', date(2018, 10, 15),
                'http://doc.ksrf.ru/decision/KSRFDecision357397.pdf')
    h3 = Header('33-П/2018', 'КС_РФ/П', 'some title3', date(2018, 7, 18),
                'http://doc.ksrf.ru/decision/KSRFDecision343519.pdf',
                r'Decision files\33-П_2018.txt')
    h4 = Header('30-П/2018', 'КС_РФ/П', 'some title4', date(2018, 7, 10),
                'http://doc.ksrf.ru/decision/KSRFDecision342302.pdf',
                r'path that not exist')
    h5 = Header('841-О/2018', 'КС_РФ/О', 'some title5', date(2018, 4, 12),
                'http://doc.ksrf.ru/decision/KSRFDecision332975.pdf',
                r'Decision files\841-О_2018.txt')
    headers = {'2028-О/2018': h1, '36-П/2018': h2, '33-П/2018': h3,
               '30-П/2018': h4, '841-О/2018': h5}
    roughLinks = get_rough_links_for_multiple_docs(headers)
    input('press any key...')
