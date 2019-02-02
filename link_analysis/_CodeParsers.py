import re
from typing import Dict, List, Type, Tuple
import dateutil
import os
import itertools
import json

if __package__:
    from link_analysis.models import Header, RoughLink, Positions, CleanLink, \
         DocumentHeader
    from link_analysis import converters
else:
    from models import Header, RoughLink, Positions, CleanLink, \
        DocumentHeader
    import converters

PATH_TO_JSON_HEADERS_FOR_CHECKING_LINKS_FILENAME = \
    os.path.join('Decision files', 'ForCheckingLinksDecisionHeaders.jsonlines')

REJECTED = 0


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
    kind1PatternTemplate = r"""(?i)
            (?:{partWordsRegex}(?P<part>
                                    (?:\d+(?:\.[-–—\d\s]+)*
                                    (?:,\s+|\s*и\s+|\s*или\s+)*)+
                                )\s*
            )*
            {articleWordsRegex}(?P<article>
                                    (?:\d+(?:\.[-–—\d\s]+)*
                                    (?:\s*["«][а-яё,\s]*?["»])*
                                    (?:,\s+|\s*и\s+|\s*или\s+|;\s+)*)+
                                )
    """
    kind2PatternTemplate = r"""(?i)
        {articleWordsRegex}(?P<article>
                                (?:\d+(?:\.[-–—\d\s]+)*
                                (?:\s*["«][а-яё,\s]*?["»])*
                                (?:,\s+|\s*и\s+|\s*или\s+)*)+
                            )\s*
        (?:{partWordsRegex}(?P<part>
                                (?:\d+(?:\.[-–—\d\s]+)*
                                (?:,\s+|\s*и\s+|\s*или\s+|;\s+)*)+
                            )
        )*
    """
    articlesAndPartsPatternTemplate = r"""(?i)
        (?:
            (?P<kind1_part1_article2>
                (?:
                    (?:{partWordsRegex}(?=(?P<n1>(?:\d+(?:\.[-–—\d\s]+)*
                                    (?:,\s+|\s*и\s+|\s*или\s+)*)+))(?P=n1)\s*)*
                    {articleWordsRegex}(?=(?P<n2>(?:\d+(?:\.[-–—\d\s]+)*
                                    (?:\s*["«][а-яё,\s]*?["»])*
                                    (?:,\s+|\s*и\s+|\s*или\s+|;\s+)*)+))(?P=n2)
                )+
                \s*{codeWordsRegex}
            |
                {codeWordsRegex}\s*\([^)]*?
                    (?:
                        (?:{partWordsRegex}(?=(?P<n3>(?:\d+(?:\.[-–—\d\s]+)*
                                        (?:,\s+|\s*и\s+|\s*или\s+)*)+))(?P=n3)\s*)+
                        {articleWordsRegex}(?=(?P<n4>(?:\d+(?:\.[-–—\d\s]+)*
                                        (?:\s*["«][а-яё,\s]*?["»])*
                                        (?:,\s+|\s*и\s+|\s*или\s+|;\s+)*)+))(?P=n4)
                    )+
                .*?\)
            )
            |
            (?P<kind2_article1_part2>
                (?:
                    {articleWordsRegex}(?=(?P<n5>(?:\d+(?:\.[-–—\d\s]+)*
                                       (?:\s*["«][а-яё,\s]*?["»])*
                                       (?:,\s+|\s*и\s+|\s*или\s+)*)+))(?P=n5)\s*
                    (?:{partWordsRegex}(?=(?P<n6>(?:\d+(?:\.[-–—\d\s]+)*
                                       (?:,\s+|\s*и\s+|\s*или\s+|;\s+)*)+))(?P=n6))*
                )+
                \s*{codeWordsRegex}
            |
                {codeWordsRegex}\s*\([^)]*?
                    (?:
                        {articleWordsRegex}(?=(?P<n7>(?:\d+(?:\.[-–—\d\s]+)*
                                           (?:\s*["«][а-яё,\s]*?["»])*
                                           (?:,\s+|\s*и\s+|\s*или\s+)*)+))(?P=n7)\s*
                        (?:{partWordsRegex}(?=(?P<n8>(?:\d+(?:\.[-–—\d\s]+)*
                                           (?:,\s+|\s*и\s+|\s*или\s+|;\s+)*)+))(?P=n8))*
                    )+
                .*?\)
            )
        )"""

    rlOpinionPattern = re.compile(r'(?i)мнение\s+судьи\s+конституционного')
    numberRangePattern = re.compile(
        r"(?P<pattern>\d+(?:\.\d+)*(?:\.(?:\d+[-–—])*?))"
        r"(?P<firstNum>\d+)\s*[-–—]\s*\1(?P<lastNum>\d+)",
        re.VERBOSE)
    stripPattern = re.compile(r'(?:[\n\s,;\.]+$|^[\n\s,;\.]+)')
    splitPattern = re.compile(r'\s*[,;ил]+\s*')
    quitedTitlePattern = re.compile(r'(?i)\s*["«][а-яё,\s]*?["»]\s*')

    @classmethod
    def _init_patterns(cls):
        partWordsRegex = f'{cls.partWordsRegex}'
        articleWordsRegex = f'{cls.articleWordsRegex}'
        codeWordsRegex = f'{cls.codeWordsRegex}'
        kind1PatternTemplate = f'{cls.kind1PatternTemplate}'
        kind1PatternRegex = kind1PatternTemplate.\
            replace('{partWordsRegex}', partWordsRegex).\
            replace('{articleWordsRegex}', articleWordsRegex)
        cls.kind1Pattern = re.compile(kind1PatternRegex, re.VERBOSE)
        kind2PatternTemplate = f'{cls.kind2PatternTemplate}'
        kind2PatternRegex = kind2PatternTemplate.\
            replace('{partWordsRegex}', partWordsRegex).\
            replace('{articleWordsRegex}', articleWordsRegex)
        cls.kind2Pattern = re.compile(kind2PatternRegex, re.VERBOSE)
        articlesAndPartsPatternTemplate = \
            f'{cls.articlesAndPartsPatternTemplate}'
        articlesAndPartsPatternRegex = articlesAndPartsPatternTemplate.\
            replace('{partWordsRegex}', partWordsRegex).\
            replace('{articleWordsRegex}', articleWordsRegex).\
            replace('{codeWordsRegex}', codeWordsRegex)
        cls.articlesAndPartsPattern = re.compile(
            articlesAndPartsPatternRegex, re.VERBOSE)

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
                splNum = cls.stripPattern.sub('', splNum).replace(' ', '')
                numRange = cls.numberRangePattern.search(splNum)
                if numRange is not None:
                    pattern = numRange['pattern']
                    first = int(numRange['firstNum'])
                    last = int(numRange['lastNum'])
                    for i in range(first, last+1):
                        nums.append(pattern + str(i))
                elif splNum != '':
                    nums.append(splNum)
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
                            articleNums = get_nums_from_range(match['article'])
                            for articleNum in articleNums:
                                roughLinks.append(
                                    RoughLink(
                                        header,
                                        f"{cls.ARTICLE_SIGN}-{articleNum}",
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
        debug = False
        if debug:
            with open(
                    'thisNotWriteInRejected.txt', 'r', encoding='utf-8') as ff:
                dontWrite = ff.read()
        if debug and len(response[1]) > 0:
            global REJECTED
            for key in response[1]:
                REJECTED += len(response[1][key])
            print(f'\nTotal rejected: {REJECTED}')
            with open('rejected_links.txt', 'at', encoding='utf-8') as file:
                for key in response[1]:
                    for link in response[1][key]:
                        print(f"\nrejected link: {cls.CODE_PREFIX} {link.body}"
                              f" from file "
                              f"{header.doc_id.replace('/', '_')}.txt\n")
                        if f'{cls.CODE_PREFIX} {link.body}' not in dontWrite:
                            file.write(
                                f"rejected link: {cls.CODE_PREFIX} {link.body}"
                                f" from file "
                                f"{header.doc_id.replace('/', '_')}.txt\n")
        cleanLinks = response[0]
        return cleanLinks


class KoaprfCodeParser(_BaseCodeParser):
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
KoaprfCodeParser._init_patterns()


class GkrfCodeParser(_BaseCodeParser):
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
GkrfCodeParser._init_patterns()


class NkrfCodeParser(_BaseCodeParser):
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
NkrfCodeParser._init_patterns()


class UkrfCodeParser(_BaseCodeParser):
    CODE_PREFIX = 'УКРФ'
    articleWordsRegex = r'(?:стат[а-яё]+\s+|(?:ст\.\s*){1,2}\s*)'
    partWordsRegex = r'(?:част[а-яё]+\s+|(?:ч\.\s*){1,2}\s*)'
    codeWordsRegex = \
        r"""
        (?:УКРФ\s+РФ|УКРФ\s+Российск[а-яё]+\s+Федерац[а-яё]+|
        Уголов[а-яё]+\s+Кодекс[а-яё]+\s+Российск[а-яё]+\s+Федерац[а-яё]+|
        Уголов[а-яё]+\s+Кодекс[а-яё]+\s+РФ)
        """
UkrfCodeParser._init_patterns()
