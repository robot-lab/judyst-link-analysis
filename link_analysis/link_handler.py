import re
import os
from typing import Dict, List, Union, Type, Set, Tuple, Iterator

import json
import dateutil
import itertools
PATH_TO_JSON_HEADERS_FOR_CHECKING_LINKS_FILENAME = \
    os.path.join('Decision files', 'ForCheckingLinksDecisionHeaders.jsonlines')

if __package__:
    from link_analysis.models import Header, RoughLink, Positions, CleanLink, \
         LinkGraph, DocumentHeader
    from link_analysis import wc_interface
    from link_analysis import converters
else:
    from models import Header, RoughLink, Positions, CleanLink, LinkGraph, \
        DocumentHeader
    import wc_interface
    import converters

sMainParts = [r".*?\.\s*?"]
sPrefixes = [r"(?<=\.\s)\s*?[ЁА-ЯA-Z]", r"(?<=^)\s*?[ёЁА-ЯA-Zа-яa-z]",
             r"(?<=\ufeff)\s*?[ёЁА-ЯA-Zа-яa-z]"]
sPostfixes = [r"(?=\s[ЁА-ЯA-Z])", r"(?=$)"]
sRegexpes = []
for pr in sPrefixes:
    for mp in sMainParts:
        for ps in sPostfixes:
            sRegexpes.append(pr + mp + ps)
sBigRegexp = '(?:' + '|'.join(sRegexpes) + ')'
sentencePattern = re.compile(sBigRegexp)

# SRE_MATCH_TYPE = type(re.match('', ''))


def _sentenceSeparator(text: str):  # -> Iterator[SRE_MATCH_TYPE]:
    return sentencePattern.finditer(text)


def _get_next_dec_for_link_checking(
        stringNumber=1,
        filePath=PATH_TO_JSON_HEADERS_FOR_CHECKING_LINKS_FILENAME):
    file = open(filePath, 'r', encoding='utf-8')
    try:
        while True:
            lines = []
            for _ in itertools.repeat(None, stringNumber):
                line = file.readline().strip('\n')
                if line[-1] == '}':
                    line = line[:-1]
                if line[0] == '{':
                    line = line[1:]
                if not line:
                    break
                else:
                    lines.append(line)
            jsonText = '{' + f"{', '.join(lines)}" + '}'
            yield json.loads(jsonText)
    except StopIteration:
        if lines:
            jsonText = '{' + f"{', '.join(lines)}" + '}'
            yield json.loads(jsonText)
    finally:
        file.close()
        raise StopIteration


class _KsrfParser:
    rlMainParts = [
        r"от[\s\d]+?(?:(?:января|февраля|марта|апреля|мая|июня|"
        r"июля|августа|сентября|октября|ноября|декабря)+?[\s\d]+?года|\d{2}\."
        r"\d{2}\.\d{4})[\s\d]+?(?:№|N)[\s\d]+?[-ёЁА-ЯA-Zа-яa-z/]*.*?"]
    rlPrefixes = [r"(?i)(?<=\s)", r"(?i)(?<=^)"]
    rlPostfixes = [r"(?=\sот)", r"(?=$)"]
    rlRegexpes = []
    for pr in rlPrefixes:
        for mp in rlMainParts:
            for ps in rlPostfixes:
                rlRegexpes.append(pr + mp + ps)
    rlBigRegexp = '(?:' + '|'.join(rlRegexpes) + ')'
    rlinkPattern = re.compile(rlBigRegexp)
    rlDatePattern = re.compile(
        r"(?i)от[\s\d]+?(?:(?:января|февраля|марта|апреля|мая|июня|июля|"
        r"августа|сентября|октября|ноября|декабря)+?[\s\d]+?года|\d{2}"
        r"\.\d{2}\.\d{4})(?=\s)")
    rlNumberPattern = re.compile(r'(?:№|N)[\s\d]+[-0-9ёЁA-ЯA-Zа-яa-z]+')
    rlOpinionPattern = re.compile(r'(?i)мнение\s+судьи\s+конституционного')

    # patterns for clean links processing:
    clYearPattern = re.compile(
        r"(?:(?<=\s)\d{4}(?=\s)|(?<=\d\d\.\d\d\.)\d{4}(?=\s)|"
        r"(?<=\d\d\.\d\d\.)\d{4}(?=$))")
    clNumberPattern = re.compile(r'\d+(-[ёЁА-ЯA-Zа-яa-z]+)+')
    clSplitPattern = re.compile(r'(?:№|N)')

    @classmethod
    def get_rough_links(
            cls, header: Header, sentenceMatchObjects) -> List[RoughLink]:
        """
        :param header: instance of class models.Header
        """
        if not isinstance(header, Header):
            raise TypeError(f"'header' must be instance of {Header}")
        roughLinks = []
        for sentenceMatch in sentenceMatchObjects:
            sentence = sentenceMatch[0]

            opinion = cls.rlOpinionPattern.search(sentence)
            if opinion is not None:  # According to the technical task.
                break                # May change in the future.
            linkMatchObjects = cls.rlinkPattern.finditer(sentence)
            contextStartPos = sentenceMatch.start(0)
            contextEndPos = contextStartPos + len(sentence.rstrip())
            for linkMatch in linkMatchObjects:
                date = cls.rlDatePattern.search(linkMatch[0])[0]
                linkStartPos = contextStartPos + linkMatch.start(0)
                matchNumbers = list(cls.rlNumberPattern.finditer(linkMatch[0]))
                if matchNumbers:
                    linkEndPos = linkStartPos + matchNumbers[-1].end(0)
                else:
                    continue
                for number in matchNumbers:
                    gottenRoughLink = date + ' ' + number[0].upper()
                    roughLinks.append(
                        RoughLink(header, gottenRoughLink,
                                  Positions(contextStartPos, contextEndPos,
                                            linkStartPos, linkEndPos
                                            )
                                  )
                        )
        return {header: roughLinks}

    @classmethod
    def get_clean_links(
            cls,
            collectedLinks: Dict[Header, List[RoughLink]],
            courtSiteContent: Dict[str, Header],
            courtPrefix: str) -> Tuple[Dict[Header, List[CleanLink]],
                                       Dict[Header, List[RoughLink]]]:
        '''
        Gets clean links.
        arguments:
        collected_links: a dictionary with list of instances of class RoughLink
        as element and instance class Header as key.
        court_site_content: a dictionary with intance of class DocumentHeader
        as element and string with court decision ID (uid) as a key.
        '''
        rejectedLinks = {}  # type: Dict[Header, List[RoughLink]]
        checkedLinks = {}  # type: Dict[Header, List[CleanLink]]
        for headerFrom in collectedLinks:
            checkedLinks[headerFrom] = []
            for link in collectedLinks[headerFrom]:
                spam = cls.clSplitPattern.split(link.body)
                number = cls.clNumberPattern.search(spam[-1])
                years = cls.clYearPattern.findall(spam[0])
                if years and number:
                    eggs = False
                    while years:
                        gottenID = (courtPrefix + '/' + number[0].upper() +
                                    '/' + years.pop())
                        if gottenID in courtSiteContent:
                            eggs = True
                            years.clear()
                            headerTo = courtSiteContent[gottenID]
                            positionAndContext = link.positions
                            cleanLink = None
                            for cl in checkedLinks[headerFrom]:
                                if cl.header_to == headerTo:
                                    cleanLink = cl
                                    break
                            if cleanLink is not None:
                                cleanLink.citations_number += 1
                                cleanLink.append(positionAndContext)
                            else:
                                cleanLink = CleanLink(headerFrom, headerTo, 1,
                                                      positionAndContext)
                                checkedLinks[headerFrom].append(cleanLink)
                    if not eggs:
                        if headerFrom not in rejectedLinks:
                            rejectedLinks[headerFrom] = []
                        rejectedLinks[headerFrom].append(link)
                else:
                    if headerFrom not in rejectedLinks:
                        rejectedLinks[headerFrom] = []
                    rejectedLinks[headerFrom].append(link)
        return (checkedLinks, rejectedLinks)

    @classmethod
    def get_clean_links2(
            cls,
            collectedLinks: Dict[Header, List[RoughLink]],
            courtSiteContent: Dict[str, Header],
            courtPrefix: str) -> Tuple[Dict[Header, List[CleanLink]],
                                       Dict[Header, List[RoughLink]]]:
        '''
        Gets clean links.
        arguments:
        collected_links: a dictionary with list of instances of class RoughLink
        as element and instance class Header as key.
        court_site_content: a dictionary with intance of class DocumentHeader
        as element and string with court decision ID (uid) as a key.
        '''
        rejectedLinks = {}  # type: Dict[Header, List[RoughLink]]
        checkedLinks = {}  # type: Dict[Header, List[CleanLink]]
        for headerFrom in collectedLinks:
            checkedLinks[headerFrom] = []
            for link in collectedLinks[headerFrom]:
                spam = cls.clSplitPattern.split(link.body)
                number = cls.clNumberPattern.search(spam[-1])
                years = cls.clYearPattern.findall(spam[0])
                if years and number:
                    eggs = False
                    while years:
                        gottenID = (courtPrefix + '/' + number[0].upper() +
                                    '/' + years.pop())
                        for dec in _get_next_dec_for_link_checking(3000000000):
                            if gottenID in dec:
                                courtSiteContent = converters.\
                                   convert_to_class_format(dec, DocumentHeader)
                                eggs = True
                                years.clear()
                                headerTo = courtSiteContent[gottenID]
                                positionAndContext = link.positions
                                cleanLink = None
                                for cl in checkedLinks[headerFrom]:
                                    if cl.header_to == headerTo:
                                        cleanLink = cl
                                        break
                                if cleanLink is not None:
                                    cleanLink.citations_number += 1
                                    cleanLink.append(positionAndContext)
                                else:
                                    cleanLink = CleanLink(
                                        headerFrom, headerTo, 1,
                                        positionAndContext)
                                    checkedLinks[headerFrom].append(cleanLink)
                                break
                    if not eggs:
                        if headerFrom not in rejectedLinks:
                            rejectedLinks[headerFrom] = []
                        rejectedLinks[headerFrom].append(link)
                else:
                    if headerFrom not in rejectedLinks:
                        rejectedLinks[headerFrom] = []
                    rejectedLinks[headerFrom].append(link)
        return (checkedLinks, rejectedLinks)

    @classmethod
    def parse(
           cls, header: Header, sentenceMatchObjects: list,
           headersBase: Dict[str, Header],
           supertype: str, headersForCheckingLinks) -> Dict[Header, CleanLink]:
        roughLinks = cls.get_rough_links(header, sentenceMatchObjects)
        response = cls.get_clean_links(roughLinks, headersBase, supertype)
        cleanLinks = response[0]
        return cleanLinks


class _BaseCodeParser:
    CODE_PREFIX = 'КОАПРФ'
    RD_SIGN = 'РЕД'
    ARTICLE_SIGN = 'СТ'
    PART_SIGN = 'Ч'
    articleWordsRegex = r'(?:стат[а-яё]+\s+|(?:ст\.\s*){1,2}\s*)'
    partWordsRegex = r'(?:част[а-яё]+\s+|(?:ч\.\s*){1,2}\s*)'
    codeWordsRegex = \
        r"""
        (?:КоАП\s+РФ|КоАП\s+Российск[а-яё]+\s+Федерац[а-яё]+|
        Кодекс[а-яё]+\s+Российск[а-яё]+\s+Федерац[а-яё]+\s+
        об административн[а-яё]+\s+правонарушен[а-яё]+|
        Кодекс[а-яё]+\s+РФ\s+об административн[а-яё]+\s+правонарушен[а-яё]+)
        """
    kind1Pattern = re.compile(rf"""(?i)
            (?:{partWordsRegex}(?P<part>
                                    (?:\d+(?:\.[-–—\d\s]+)*
                                    (?:,\s+|\s+и\s+|\s+или\s+)*)+
                                )\s*
            )*
            {articleWordsRegex}(?P<article>
                                    (?:\d+(?:\.[-–—\d\s]+)*
                                    (?:\s*["«][а-яё,\s]*?["»])*
                                    (?:,\s+|\s+и\s+|\s+или\s+|;\s+)*)+
                                )
    """, re.VERBOSE)
    kind2Pattern = re.compile(rf"""(?i)
        {articleWordsRegex}(?P<article>
                                (?:\d+(?:\.[-–—\d\s]+)*
                                (?:\s*["«][а-яё,\s]*?["»])*
                                (?:,\s+|\s+и\s+|\s+или\s+)*)+
                            )\s*
        (?:{partWordsRegex}(?P<part>
                                (?:\d+(?:\.[-–—\d\s]+)*
                                (?:,\s+|\s+и\s+|\s+или\s+|;\s+)*)+
                            )
        )*
    """, re.VERBOSE)
    articlesAndPartsPattern = re.compile(rf"""(?i)
        (?:
            (?P<kind1_part1_article2>
                (?:
                    (?:{partWordsRegex}(?=(?P<n1>(?:\d+(?:\.[-–—\d\s]+)*
                                    (?:,\s+|\s+и\s+|\s+или\s+)*)+))(?P=n1)\s*)*
                    {articleWordsRegex}(?=(?P<n2>(?:\d+(?:\.[-–—\d\s]+)*
                                    (?:\s*["«][а-яё,\s]*?["»])*
                                    (?:,\s+|\s+и\s+|\s+или\s+|;\s+)*)+))(?P=n2)
                )+
                \s*{codeWordsRegex}
            |
                {codeWordsRegex}\s*\(.*?
                    (?:
                        (?:{partWordsRegex}(?=(?P<n3>(?:\d+(?:\.[-–—\d\s]+)*
                                        (?:,\s+|\s+и\s+|\s+или\s+)*)+))(?P=n3)\s*)+
                        {articleWordsRegex}(?=(?P<n4>(?:\d+(?:\.[-–—\d\s]+)*
                                        (?:\s*["«][а-яё,\s]*?["»])*
                                        (?:,\s+|\s+и\s+|\s+или\s+|;\s+)*)+))(?P=n4)
                    )+
                .*?\)
            )
            |
            (?P<kind2_article1_part2>
                (?:
                    {articleWordsRegex}(?=(?P<n5>(?:\d+(?:\.[-–—\d\s]+)*
                                       (?:\s*["«][а-яё,\s]*?["»])*
                                       (?:,\s+|\s+и\s+|\s+или\s+)*)+))(?P=n5)\s*
                    (?:{partWordsRegex}(?=(?P<n6>(?:\d+(?:\.[-–—\d\s]+)*
                                       (?:,\s+|\s+и\s+|\s+или\s+|;\s+)*)+))(?P=n6))*
                )+
                \s*{codeWordsRegex}
            |
                {codeWordsRegex}\s*\(.*?
                    (?:
                        {articleWordsRegex}(?=(?P<n7>(?:\d+(?:\.[-–—\d\s]+)*
                                           (?:\s*["«][а-яё,\s]*?["»])*
                                           (?:,\s+|\s+и\s+|\s+или\s+)*)+))(?P=n7)\s*
                        (?:{partWordsRegex}(?=(?P<n8>(?:\d+(?:\.[-–—\d\s]+)*
                                           (?:,\s+|\s+и\s+|\s+или\s+|;\s+)*)+))(?P=n8))*
                    )+
                .*?\)
            )
        )""", re.VERBOSE)

    rlOpinionPattern = re.compile(r'(?i)мнение\s+судьи\s+конституционного')
    numberRangePattern = re.compile(
        r"(?P<pattern>\d+(?:\.\d+)*(?:\.(?:\d+[-–—])*?))"
        r"(?P<firstNum>\d+)\s*[-–—]\s*\1(?P<lastNum>\d+)",
        re.VERBOSE)
    stripPattern = re.compile(r'(?:[\n\s,;]+$|^[\n\s,;]+)')
    splitPattern = re.compile(r'\s*[,;ил]+\s*')
    quitedTitlePattern = re.compile(r'(?i)\s*["«][а-яё,\s]*?["»]\s*')

    @classmethod
    def get_rough_links(
            cls, header: Header, sentenceMatchObjects,
            findInOpinion: bool=False) -> List[RoughLink]:
        """
        :param header: instance of class models.Header
        """

        def get_nums_from_range(match):
            splitedNums = cls.splitPattern.split(
                cls.quitedTitlePattern.sub('', match).strip())
            nums = []
            for splNum in splitedNums:
                numRange = cls.numberRangePattern.search(splNum)
                if numRange is not None:
                    pattern = numRange['pattern']
                    first = int(numRange['firstNum'])
                    last = int(numRange['lastNum'])
                    for i in range(first, last+1):
                        nums.append(pattern + str(i))
                elif splNum != '':
                    nums.append(cls.stripPattern.sub('', splNum))
            return nums

        if not isinstance(header, Header):
            raise TypeError(f"'header' must be instance of {Header}")
        roughLinks = []
        for sentenceMatch in sentenceMatchObjects:
            sentence = sentenceMatch[0]
            if findInOpinion:
                opinion = cls.rlOpinionPattern.search(sentence)
                if opinion is not None:  # According to the technical task.
                    break                # May change in the future.
            contextStartPos = sentenceMatch.start(0)
            contextEndPos = contextStartPos + len(sentence.rstrip())
            for linkMatch in cls.articlesAndPartsPattern.finditer(sentence):
                linkStartPos = contextStartPos + linkMatch.start(0)
                linkEndPos = linkStartPos + len(linkMatch.group(0).rstrip())
                if linkMatch.group('kind1_part1_article2') is not None:
                    matches = cls.kind1Pattern.finditer(
                        linkMatch['kind1_part1_article2'])
                elif linkMatch.group('kind2_article1_part2') is not None:
                    matches = cls.kind2Pattern.finditer(
                        linkMatch['kind2_article1_part2'])
                else:
                    raise Exception("it's bad")
                for match in matches:
                        if match['part'] is None:
                            nums = get_nums_from_range(match['article'])
                            for num in nums:
                                roughLinks.append(
                                    RoughLink(header,
                                              f"{cls.ARTICLE_SIGN}-{num}",
                                              Positions(contextStartPos,
                                                        contextEndPos,
                                                        linkStartPos,
                                                        linkEndPos
                                                        )
                                              )
                                    )
                        else:
                            articleNums = get_nums_from_range(match['article'])
                            for articleNum in articleNums:
                                nums = get_nums_from_range(match['part'])
                                for num in nums:
                                    roughLinks.append(
                                        RoughLink(header,
                                                  (f"{cls.ARTICLE_SIGN}-"
                                                   f"{articleNum}/"
                                                   f"{cls.PART_SIGN}-{num}"),
                                                  Positions(contextStartPos,
                                                            contextEndPos,
                                                            linkStartPos,
                                                            linkEndPos
                                                            )
                                                  )
                                        )
        return {header: roughLinks}

    @classmethod
    def get_clean_links(
            cls,
            collectedLinks: Dict[Header, List[RoughLink]],
            courtSiteContent: Dict[str, Header],
            courtPrefix: str,
            headersForCheckingLinks) -> Tuple[Dict[Header, List[CleanLink]],
                                              Dict[Header, List[RoughLink]]]:
        rejectedLinks = {}  # type: Dict[Header, List[RoughLink]]
        checkedLinks = {}  # type: Dict[Header, List[CleanLink]]
        for headerFrom in collectedLinks:
            releaseDate = headerFrom.release_date
            checkedLinks[headerFrom] = []
            for link in collectedLinks[headerFrom]:
                eggs = False
                for date in sorted(headersForCheckingLinks, reverse=True):
                    if date > releaseDate:
                        continue
                    gottenID = (f"{cls.CODE_PREFIX}/{cls.RD_SIGN}-"
                                f"{date.strftime('%d.%m.%Y')}/{link.body}")
                    if gottenID in headersForCheckingLinks[date]:
                        gottenID = headersForCheckingLinks[date][gottenID]
                        eggs = True
                        break
                if not eggs:
                    if headerFrom not in rejectedLinks:
                            rejectedLinks[headerFrom] = []
                    rejectedLinks[headerFrom].append(link)
                    continue

                fakeHeaderTo = Header(
                    gottenID, 'супертип', 'тип', 'заголовок',
                    dateutil.parser.parse(
                        '01.01.0001', dayfirst=True).date(), 'урл')
                headerTo = fakeHeaderTo
                positionAndContext = link.positions
                cleanLink = None
                for cl in checkedLinks[headerFrom]:
                    if cl.header_to == headerTo:
                        cleanLink = cl
                        break
                if cleanLink is not None:
                    cleanLink.citations_number += 1
                    cleanLink.append(positionAndContext)
                else:
                    cleanLink = CleanLink(headerFrom, headerTo, 1,
                                          positionAndContext)
                    checkedLinks[headerFrom].append(cleanLink)
        return (checkedLinks, rejectedLinks)

    @classmethod
    def parse(
           cls, header: Header, sentenceMatchObjects: list,
           headersBase: Dict[str, Header],
           supertype: str, headersForCheckingLinks) -> Dict[Header, CleanLink]:
        roughLinks = cls.get_rough_links(header, sentenceMatchObjects)
        response = cls.get_clean_links(roughLinks, headersBase, supertype,
                                       headersForCheckingLinks)
        cleanLinks = response[0]
        return cleanLinks


class _GkrfCodeParser(_BaseCodeParser):
    CODE_PREFIX = 'ГКРФ'
    articleWordsRegex = r'(?:стат[а-яё]+\s+|(?:ст\.\s*){1,2}\s*)'
    partWordsRegex = (r'(?:част[а-яё]+\s+|(?:ч\.\s*){1,2}\s*|'
                      r'пункт[а-яё]*\s+|(?:п\.\s*){1,2}\s*)')
    codeWordsRegex = \
        r"""
        (?:ГКРФ\s+РФ|ГКРФ\s+Российск[а-яё]+\s+Федерац[а-яё]+|
        Гражданск[а-яё]+\s+Кодекс[а-яё]+\s+Российск[а-яё]+\s+Федерац[а-яё]+|
        Гражданск[а-яё]+\s+Кодекс[а-яё]+\s+РФ)
        """
    # kind1Pattern, kind2Pattern articlesAndPartsPattern are same as in the
    # _BaseCodeParser, necessary to redefine because of the order of computing
    # the strings (the final string would coincided with the string
    # from the _BaseCodeParser)
    kind1Pattern = re.compile(rf"""(?i)
            (?:{partWordsRegex}(?P<part>
                                    (?:\d+(?:\.[-–—\d\s]+)*
                                    (?:,\s+|\s+и\s+|\s+или\s+)*)+
                                )\s*
            )*
            {articleWordsRegex}(?P<article>
                                    (?:\d+(?:\.[-–—\d\s]+)*
                                    (?:\s*["«][а-яё,\s]*?["»])*
                                    (?:,\s+|\s+и\s+|\s+или\s+|;\s+)*)+
                                )
    """, re.VERBOSE)
    kind2Pattern = re.compile(rf"""(?i)
        {articleWordsRegex}(?P<article>
                                (?:\d+(?:\.[-–—\d\s]+)*
                                (?:\s*["«][а-яё,\s]*?["»])*
                                (?:,\s+|\s+и\s+|\s+или\s+)*)+
                            )\s*
        (?:{partWordsRegex}(?P<part>
                                (?:\d+(?:\.[-–—\d\s]+)*
                                (?:,\s+|\s+и\s+|\s+или\s+|;\s+)*)+
                            )
        )*
    """, re.VERBOSE)
    articlesAndPartsPattern = re.compile(rf"""(?i)
        (?:
            (?P<kind1_part1_article2>
                (?:
                    (?:{partWordsRegex}(?=(?P<n1>(?:\d+(?:\.[-–—\d\s]+)*
                                    (?:,\s+|\s+и\s+|\s+или\s+)*)+))(?P=n1)\s*)*
                    {articleWordsRegex}(?=(?P<n2>(?:\d+(?:\.[-–—\d\s]+)*
                                    (?:\s*["«][а-яё,\s]*?["»])*
                                    (?:,\s+|\s+и\s+|\s+или\s+|;\s+)*)+))(?P=n2)
                )+
                \s*{codeWordsRegex}
            |
                {codeWordsRegex}\s*\(.*?
                    (?:
                        (?:{partWordsRegex}(?=(?P<n3>(?:\d+(?:\.[-–—\d\s]+)*
                                        (?:,\s+|\s+и\s+|\s+или\s+)*)+))(?P=n3)\s*)+
                        {articleWordsRegex}(?=(?P<n4>(?:\d+(?:\.[-–—\d\s]+)*
                                        (?:\s*["«][а-яё,\s]*?["»])*
                                        (?:,\s+|\s+и\s+|\s+или\s+|;\s+)*)+))(?P=n4)
                    )+
                .*?\)
            )
            |
            (?P<kind2_article1_part2>
                (?:
                    {articleWordsRegex}(?=(?P<n5>(?:\d+(?:\.[-–—\d\s]+)*
                                       (?:\s*["«][а-яё,\s]*?["»])*
                                       (?:,\s+|\s+и\s+|\s+или\s+)*)+))(?P=n5)\s*
                    (?:{partWordsRegex}(?=(?P<n6>(?:\d+(?:\.[-–—\d\s]+)*
                                       (?:,\s+|\s+и\s+|\s+или\s+|;\s+)*)+))(?P=n6))*
                )+
                \s*{codeWordsRegex}
            |
                {codeWordsRegex}\s*\(.*?
                    (?:
                        {articleWordsRegex}(?=(?P<n7>(?:\d+(?:\.[-–—\d\s]+)*
                                           (?:\s*["«][а-яё,\s]*?["»])*
                                           (?:,\s+|\s+и\s+|\s+или\s+)*)+))(?P=n7)\s*
                        (?:{partWordsRegex}(?=(?P<n8>(?:\d+(?:\.[-–—\d\s]+)*
                                           (?:,\s+|\s+и\s+|\s+или\s+|;\s+)*)+))(?P=n8))*
                    )+
                .*?\)
            )
        )""", re.VERBOSE)


class _NkrfCodeParser(_BaseCodeParser):
    CODE_PREFIX = 'НКРФ'
    articleWordsRegex = r'(?:стат[а-яё]+\s+|(?:ст\.\s*){1,2}\s*)'
    partWordsRegex = (r'(?:част[а-яё]+\s+|(?:ч\.\s*){1,2}\s*|'
                      r'пункт[а-яё]*\s+|(?:п\.\s*){1,2}\s*)')
    codeWordsRegex = \
        r"""
        (?:НКРФ\s+РФ|НКРФ\s+Российск[а-яё]+\s+Федерац[а-яё]+|
        Налогов[а-яё]+\s+Кодекс[а-яё]+\s+Российск[а-яё]+\s+Федерац[а-яё]+|
        Налогов[а-яё]+\s+Кодекс[а-яё]+\s+РФ)
        """
    # kind1Pattern, kind2Pattern articlesAndPartsPattern are same as in the
    # _BaseCodeParser, necessary to redefine because of the order of computing
    # the strings (the final string would coincided with the string
    # from the _BaseCodeParser)
    kind1Pattern = re.compile(rf"""(?i)
            (?:{partWordsRegex}(?P<part>
                                    (?:\d+(?:\.[-–—\d\s]+)*
                                    (?:,\s+|\s+и\s+|\s+или\s+)*)+
                                )\s*
            )*
            {articleWordsRegex}(?P<article>
                                    (?:\d+(?:\.[-–—\d\s]+)*
                                    (?:\s*["«][а-яё,\s]*?["»])*
                                    (?:,\s+|\s+и\s+|\s+или\s+|;\s+)*)+
                                )
    """, re.VERBOSE)
    kind2Pattern = re.compile(rf"""(?i)
        {articleWordsRegex}(?P<article>
                                (?:\d+(?:\.[-–—\d\s]+)*
                                (?:\s*["«][а-яё,\s]*?["»])*
                                (?:,\s+|\s+и\s+|\s+или\s+)*)+
                            )\s*
        (?:{partWordsRegex}(?P<part>
                                (?:\d+(?:\.[-–—\d\s]+)*
                                (?:,\s+|\s+и\s+|\s+или\s+|;\s+)*)+
                            )
        )*
    """, re.VERBOSE)
    articlesAndPartsPattern = re.compile(rf"""(?i)
        (?:
            (?P<kind1_part1_article2>
                (?:
                    (?:{partWordsRegex}(?=(?P<n1>(?:\d+(?:\.[-–—\d\s]+)*
                                    (?:,\s+|\s+и\s+|\s+или\s+)*)+))(?P=n1)\s*)*
                    {articleWordsRegex}(?=(?P<n2>(?:\d+(?:\.[-–—\d\s]+)*
                                    (?:\s*["«][а-яё,\s]*?["»])*
                                    (?:,\s+|\s+и\s+|\s+или\s+|;\s+)*)+))(?P=n2)
                )+
                \s*{codeWordsRegex}
            |
                {codeWordsRegex}\s*\(.*?
                    (?:
                        (?:{partWordsRegex}(?=(?P<n3>(?:\d+(?:\.[-–—\d\s]+)*
                                        (?:,\s+|\s+и\s+|\s+или\s+)*)+))(?P=n3)\s*)+
                        {articleWordsRegex}(?=(?P<n4>(?:\d+(?:\.[-–—\d\s]+)*
                                        (?:\s*["«][а-яё,\s]*?["»])*
                                        (?:,\s+|\s+и\s+|\s+или\s+|;\s+)*)+))(?P=n4)
                    )+
                .*?\)
            )
            |
            (?P<kind2_article1_part2>
                (?:
                    {articleWordsRegex}(?=(?P<n5>(?:\d+(?:\.[-–—\d\s]+)*
                                       (?:\s*["«][а-яё,\s]*?["»])*
                                       (?:,\s+|\s+и\s+|\s+или\s+)*)+))(?P=n5)\s*
                    (?:{partWordsRegex}(?=(?P<n6>(?:\d+(?:\.[-–—\d\s]+)*
                                       (?:,\s+|\s+и\s+|\s+или\s+|;\s+)*)+))(?P=n6))*
                )+
                \s*{codeWordsRegex}
            |
                {codeWordsRegex}\s*\(.*?
                    (?:
                        {articleWordsRegex}(?=(?P<n7>(?:\d+(?:\.[-–—\d\s]+)*
                                           (?:\s*["«][а-яё,\s]*?["»])*
                                           (?:,\s+|\s+и\s+|\s+или\s+)*)+))(?P=n7)\s*
                        (?:{partWordsRegex}(?=(?P<n8>(?:\d+(?:\.[-–—\d\s]+)*
                                           (?:,\s+|\s+и\s+|\s+или\s+|;\s+)*)+))(?P=n8))*
                    )+
                .*?\)
            )
        )""", re.VERBOSE)

_parsersDict = {
    'КСРФ': _KsrfParser,
    'ГКРФ': _GkrfCodeParser,
    'НКРФ': _NkrfCodeParser
}

_NnDelPattern = re.compile(r'-N\d+-')


def parse(headersToParsing: Dict[str, Header], headersBase: Dict[str, Header],
          supertypes: Set[str]) -> Dict[Header, CleanLink]:
    def get_headersForCheckingLinks():
        print('Start to prepare headers for checking links.')  # debug print
        hs = {}
        for decs in _get_next_dec_for_link_checking(1000):
            for key in decs:
                if decs[key]['supertype'] not in supertypes:
                    continue
                try:
                    effectiveDate = decs[key]['effective_date']
                except KeyError:
                    continue
                if effectiveDate not in hs:
                    hs[effectiveDate] = {}
                hs[effectiveDate][_NnDelPattern.sub('-', key)] = key
        dateKeyedHs = {}
        for key in hs:
            try:
                datekey = dateutil.parser.parse(key, dayfirst=True).date()
            except ValueError:
                continue
            dateKeyedHs[datekey] = hs[key]
        print('Finish to prepare headers for checking links.')  # debug print
        return dateKeyedHs
    headersForCheckingLinks = get_headersForCheckingLinks()
    if not hasattr(supertypes, '__iter__'):
        raise TypeError(f"'supertypes must be {set} or {list} or {tuple}")
    if isinstance(supertypes, str):
        supertypes = set([supertypes])
    allCleanLinks = {}
    docCounter = 0  # debug
    for doc_id in headersToParsing:
        docCounter += 1
        print(
            f'Find links in document {doc_id}  {docCounter}'
            f'/{len(headersToParsing)}...',
            end='\r')  # debug print
        text = wc_interface.get_text(doc_id)
        if text is None:
                print(f"fileID: {doc_id}")
                raise ValueError("Where's the text, Lebowski?")
        sentenceMatchObjects = list(_sentenceSeparator(text))
        for st in supertypes:
            if st in _parsersDict:
                parsed = _parsersDict[st].parse(
                    headersToParsing[doc_id], sentenceMatchObjects,
                    headersBase, st, headersForCheckingLinks)
                for h in parsed:
                    if h in allCleanLinks:
                        allCleanLinks[h].extend(parsed[h])
                    else:
                        allCleanLinks[h] = parsed[h]
    return allCleanLinks


def get_link_graph(checkedLinks: Dict[Header, List[CleanLink]]) -> LinkGraph:
    '''
    Gets Link Graph, returning instance of clas LinkGraph
    argument: checked_links is a dictionary with list of instances
    of class CleanLink as element and string with court decision ID (uid)
    as a key.
    '''
    linkGraph = LinkGraph()
    for header in checkedLinks:
        linkGraph.add_node(header)
        for cl in checkedLinks[header]:
            linkGraph.add_node(cl.header_to)
            linkGraph.add_edge(cl)
    return linkGraph

if __name__ == '__main__':
    print(1)
    pat = _BaseCodeParser.articlesAndPartsPattern
    # a = _get_next_dec_for_link_checking()
    # for r in a:
    #     print(r)
    # print('end')
    # while True:
    #     b = next(a)
    #     if b is None:
    #         break
    #     print(b)
