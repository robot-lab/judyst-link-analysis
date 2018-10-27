import re
from typing import Dict, List, Union, Type, Set, Tuple

if __package__:
    from link_analysis.models import Header, RoughLink, Positions, CleanLink, \
         LinkGraph
else:
    from models import Header, RoughLink, Positions, CleanLink, LinkGraph
    import wc_interface


class _KsrfParser:
    # link pattern main parts
    lpMainParts = [
        r".*?\sот[\s\d]+?(?:(?:января|февраля|марта|апреля|мая|июня|июля|"
        r"августа|сентября|октября|ноября|декабря)+?[\s\d]+?года|\d{2}\."
        r"\d{2}\.\d{4})[\s\d]+?(?:№|N)[\s\d]+?[-\w/]*.*?"
        ]

    # link pattern prefixes
    lpPrefixes = [r"(?<=\.\s)\s*?[А-ЯA-Z]", r"(?<=^)\s*?[А-ЯA-Zа-яa-z]"]
    # link pattern postfixes
    lpPostfixes = [r"(?=\.\s[А-ЯA-Z])", r"(?=\.$)"]
    regexpes = []
    for pr in lpPrefixes:
        for mp in lpMainParts:
            for ps in lpPostfixes:
                regexpes.append(pr + mp + ps)
    bigRegexp = '(?:' + '|'.join(regexpes) + ')'

    rlLinkPattern = re.compile(bigRegexp)

    # pattern for removing of redundant leading sentences
    rlReductionPattern = re.compile(
        r"(?:[А-ЯA-Z].*[^А-ЯA-Z]\.\s*(?=[А-ЯA-Z])|^[А-ЯA-Zа-яa-z]"
        r".*[^А-ЯA-Z]\.\s*(?=[А-ЯA-Z]))")

    # other patterns
    rlSplitPattern = re.compile(r"""(?i)о(?=т[\s\d]+?(?:(?:января|февраля|марта|апреля|мая|июня|июля|
                августа|сентября|октября|ноября|декабря)+?[\s\d]+?года|\d{2}
                \.\d{2}\.\d{4})[\s\d]+?(?:№|N))""")
    rlDatePattern = re.compile(r"""(?i)т[\s\d]+?(?:(?:января|февраля|марта|апреля|мая|июня|июля|
                августа|сентября|октября|ноября|декабря)+?[\s\d]+?года|\d{2}
                \.\d{2}\.\d{4})(?=\s)""")
    rlNumberPattern = re.compile(r'(?:№|N)[\s\d]+[-\w/]*')
    rlOpinionPattern = re.compile(r'(?i)мнение\s+судьи\s+конституционного')

    # patterns for clean links processing:
    clYearPattern = re.compile(
        r'(?:(?<=\s)\d{4}(?=\s)|(?<=\d\d\.\d\d\.)\d{4}(?=\s))')
    clNumberPattern = re.compile(r'\d+(-[А-ЯA-Zа-яa-z]+)+')
    clSplitPattern = re.compile(r'(?:№|N)')

    @classmethod
    def get_rough_links(cls, header: Header) -> List[RoughLink]:
        """
        :param header: instance of class models.Header
        """
        text = wc_interface.get_text(header.doc_id)
        if not text:
            print(f"fileID: {header.doc_id}")
            raise ValueError("Where's the text, Lebowski?")
        roughLinks = []
        opinion = cls.rlOpinionPattern.search(text)
        if opinion is not None:
            matchObjects = cls.rlLinkPattern.finditer(text,
                                                      endpos=opinion.start())
        else:
            matchObjects = cls.rlLinkPattern.finditer(text)
        for match in matchObjects:
            linksForSplit = match[0]
            reduct = cls.rlReductionPattern.search(linksForSplit)
            if reduct is not None:
                reductCorrection = reduct.end()
                # context = linksForSplit.replace(reduct[0], '') + '.'
            else:
                reductCorrection = 0
                # context = linksForSplit
            linkCorrection = len(cls.rlSplitPattern.split(linksForSplit,
                                 maxsplit=1)[0])
            contextStartPos = match.start(0) + reductCorrection
            contextEndPos = match.end(0) + 1
            linkStartPos = match.start(0) + linkCorrection

            splitedLinksForDifferentYears = cls.rlSplitPattern.split(
                                                    linksForSplit)[1:]
            for oneYearLinks in splitedLinksForDifferentYears:
                date = cls.rlDatePattern.search(oneYearLinks)[0]
                matchNumbers = list(cls.rlNumberPattern.finditer(oneYearLinks))

                linkEndPos = linkStartPos + matchNumbers[-1].end(0) + 1
                for number in matchNumbers:
                    gottenRoughLink = 'о' + date + ' ' + number[0].upper()
                    roughLinks.append(
                        RoughLink(header, gottenRoughLink,
                                  Positions(contextStartPos, contextEndPos,
                                            linkStartPos, linkEndPos
                                            )
                                  )
                        )
                linkStartPos += len(oneYearLinks) + 1
        return roughLinks

    @classmethod
    def get_rough_links_for_docs(
            cls,
            headers: Dict[str, Header]) -> Dict[Header, List[RoughLink]]:
        """
        :param header: dict of instances of class models.Header
        return dict with list of instances of class RoughLink
        as element and instance class Header as key,
        also this dict may contain two lists of instances of
        lass models.Header which were unsuccessfully processed
        """
        result = {}  # type: Dict[Header, List[RoughLink]]
        for decisionID in headers:
            if not isinstance(headers[decisionID], Header):
                raise TypeError(
                    f"Any element of 'headers' must be instance of {Header}")
            maybeRoughLinks = cls.get_rough_links(headers[decisionID])
            result[headers[decisionID]] = maybeRoughLinks
        return result

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
    def parse(cls, headers: Dict[str, Header], headersBase: Dict[str, Header],
              supertype: str) -> Dict[Header, CleanLink]:
        roughLinks = cls.get_rough_links_for_docs(headers)
        response = cls.get_clean_links(roughLinks, headersBase, supertype)
        cleanLinks = response[0]
        return cleanLinks


_parsersDict = {
    'КСРФ': _KsrfParser
}


def parse(headers: Dict[str, Header], headersBase: Dict[str, Header],
          supertypes: Set[str]) -> Dict[Header, CleanLink]:
    if not hasattr(supertypes, '__iter__'):
        raise TypeError(f"'supertypes must be {set} or {list} or {tuple}")
    if isinstance(supertypes, str):
        supertypes = set([supertypes])
    allCleanLinks = {}
    for st in supertypes:
        if st in _parsersDict:
            parsed = _parsersDict[st].parse(headers, headersBase, st)
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
