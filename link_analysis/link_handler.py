import re
from typing import Dict, List, Union, Type, Set, Tuple, Iterator

if __package__:
    from link_analysis.models import Header, RoughLink, Positions, CleanLink, \
         LinkGraph
    from link_analysis import wc_interface
else:
    from models import Header, RoughLink, Positions, CleanLink, LinkGraph
    import wc_interface

sMainParts = [r".*?\.\s*?"]
sPrefixes = [r"(?<=\.\s)\s*?[А-ЯA-Z]", r"(?<=^)\s*?[А-ЯA-Zа-яa-z]",
             r"(?<=\ufeff)\s*?[А-ЯA-Zа-яa-z]"]
sPostfixes = [r"(?=\s[А-ЯA-Z])", r"(?=$)"]
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


class _KsrfParser:
    rlMainParts = [
        r"от[\s\d]+?(?:(?:января|февраля|марта|апреля|мая|июня|"
        r"июля|августа|сентября|октября|ноября|декабря)+?[\s\d]+?года|\d{2}\."
        r"\d{2}\.\d{4})[\s\d]+?(?:№|N)[\s\d]+?[-А-ЯA-Zа-яa-z/]*.*?"]
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
    rlNumberPattern = re.compile(r'(?:№|N)[\s\d]+[-0-9A-ЯA-Zа-яa-z]+')
    rlOpinionPattern = re.compile(r'(?i)мнение\s+судьи\s+конституционного')

    # patterns for clean links processing:
    clYearPattern = re.compile(
        r"(?:(?<=\s)\d{4}(?=\s)|(?<=\d\d\.\d\d\.)\d{4}(?=\s)|"
        r"(?<=\d\d\.\d\d\.)\d{4}(?=$))")
    clNumberPattern = re.compile(r'\d+(-[А-ЯA-Zа-яa-z]+)+')
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
    def parse(
            cls, header: Header, sentenceMatchObjects: list,
            headersBase: Dict[str, Header],
            supertype: str) -> Dict[Header, CleanLink]:
        roughLinks = cls.get_rough_links(header, sentenceMatchObjects)
        response = cls.get_clean_links(roughLinks, headersBase, supertype)
        cleanLinks = response[0]
        return cleanLinks


_parsersDict = {
    'КСРФ': _KsrfParser
}


def parse(headersToParsing: Dict[str, Header], headersBase: Dict[str, Header],
          supertypes: Set[str]) -> Dict[Header, CleanLink]:
    if not hasattr(supertypes, '__iter__'):
        raise TypeError(f"'supertypes must be {set} or {list} or {tuple}")
    if isinstance(supertypes, str):
        supertypes = set([supertypes])
    allCleanLinks = {}
    for doc_id in headersToParsing:
        text = wc_interface.get_text(doc_id)
        if text is None:
                print(f"fileID: {doc_id}")
                raise ValueError("Where's the text, Lebowski?")
        sentenceMatchObjects = list(_sentenceSeparator(text))
        for st in supertypes:
            if st in _parsersDict:
                parsed = _parsersDict[st].parse(
                    headersToParsing[doc_id], sentenceMatchObjects,
                    headersBase, st)
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
