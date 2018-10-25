import re
from typing import Dict, List, Union
from models import Header, RoughLink, DuplicateHeader

# link pattern main part
lpMP = (r".*?\sот[\s\d]+?(?:(?:января|февраля|марта|апреля|мая|июня|июля|"
        r"августа|сентября|октября|ноября|декабря)+?[\s\d]+?года|\d{2}\."
        r"\d{2}\.\d{4})[\s\d]+?(№|N)[\s\d]+?[-\w/]*.*?")
# link pattern prefix #1
lpPRF1 = r"(?<=\.\s)\s*?[А-Я]"
# link pattern postfix #1
lpPSF1 = r"(?=\.\s[А-Я])"
# link pattern prefix #2
lpPRF2 = r"(?<=^)\s*?[А-Яа-я]"
# link pattern postfix #2
lpPSF2 = r"(?=\.$)"
linkPattern = re.compile(
    f"(?:{lpPRF1+lpMP+lpPSF1}|{lpPRF1+lpMP+lpPSF2}|{lpPRF2+lpMP+lpPSF1}|"
    f"{lpPRF2+lpMP+lpPSF2})", re.VERBOSE)

# pattern for removing of redundant leading sentences
reductionPattern = re.compile(r"(?:[А-Я].*[^А-Я]\.\s*(?=[А-Я])|^[А-Яа-я]"
                              r".*[^А-Я]\.\s*(?=[А-Я]))")

# same part of two regular expressions below
samePart = (r"т[\s\d]+?(?:(?:января|февраля|марта|апреля|мая|июня|июля|"
            r"августа|сентября|октября|ноября|декабря)+?[\s\d]+?года|\d{2}"
            r"\.\d{2}\.\d{4})(?=\s)")
splitPattern = re.compile(
    f"(?i)о(?={samePart})")
datePattern = re.compile(
    f"(?i){samePart}")
numberPattern = re.compile(r'(?:№|N)[\s\d]+[-\w/]*')
opinionPattern = re.compile(r'(?i)мнение\s+судьи\s+конституционного')


def get_rough_links(header: Header) -> List[RoughLink]:
    """
    :param header: instance of class models.Header
    """
    try:
        with open(header.text_location, 'r', encoding='utf-8') as file:
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
        context = reductionPattern.sub('', linksForSplit) + '.'
        position = match.start(0) + len(splitPattern.split(linksForSplit,
                                        maxsplit=1)[0]) + 1
        splitedLinksForDifferentYears = splitPattern.split(linksForSplit)[1:]
        for oneYearLinks in splitedLinksForDifferentYears:
            date = datePattern.search(oneYearLinks)[0]
            numbers = numberPattern.findall(oneYearLinks)
            for number in numbers:
                gottenRoughLink = 'о' + date + ' ' + number.upper()
                roughLinks.append(RoughLink(header, gottenRoughLink, context,
                                  position))
            position += len(oneYearLinks) + 1
    return roughLinks


PATH_NONE_VALUE_KEY = 'path has None value'
PATH_NOT_EXIST_KEY = 'path does not exist'


def get_rough_links_for_multiple_docs(
        headers: Dict[str, Union[Header, DuplicateHeader]]) -> Dict[Header, List[RoughLink]]:
    """
    :param header: dict of instances of class models.Header
    return dict with list of instances of class RoughLink
    as element and instance class Header as key,
    also this dict may contain two lists of instances of
    lass models.Header which were unsuccessfully processed
    """
    result = {}  # type: Dict[Header, List[RoughLink]]
    for decisionID in headers:
        if isinstance(headers[decisionID], DuplicateHeader):
            continue
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
        result[headers[decisionID]] = maybeRoughLinks
    return result


if (__name__ == '__main__'):
    from datetime import date
    # h1 = Header('2028-О/2018', 'КСРФ/О', 'some title1', date(2018, 7, 17),
    #             'http://doc.ksrf.ru/decision/KSRFDecision353855.pdf',
    #             r'Decision files\КСРФ_2028-О_2018.txt')
    # h2 = Header('36-П/2018', 'КСРФ/П', 'some title2', date(2018, 10, 15),
    #             'http://doc.ksrf.ru/decision/KSRFDecision357397.pdf')
    # h3 = Header('33-П/2018', 'КСРФ/П', 'some title3', date(2018, 7, 18),
    #             'http://doc.ksrf.ru/decision/KSRFDecision343519.pdf',
    #             r'Decision files\КСРФ_33-П_2018.txt')
    # h4 = Header('30-П/2018', 'КСРФ/П', 'some title4', date(2018, 7, 10),
    #             'http://doc.ksrf.ru/decision/KSRFDecision342302.pdf',
    #             r'path that not exist')
    # h5 = Header('841-О/2018', 'КСРФ/О', 'some title5', date(2018, 4, 12),
    #             'http://doc.ksrf.ru/decision/KSRFDecision332975.pdf',
    #             r'Decision files\КСРФ_841-О_2018.txt')
    # headers = {'2028-О/2018': h1, '36-П/2018': h2, '33-П/2018': h3,
    #            '30-П/2018': h4, '841-О/2018': h5}
    # roughLinks = get_rough_links_for_multiple_docs(headers)
    # input('press any key...')

    h = Header('test5', 'ксрф', 'А', 'title', date(1991, 3, 2), 'url', r'C:\VS Code Projects\test5.txt')
    r=get_rough_links(h)
    print('s')