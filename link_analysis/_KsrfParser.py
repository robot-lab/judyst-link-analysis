import re
from typing import Dict, List, Type, Tuple

if __package__:
    from link_analysis.models import Header, RoughLink, Positions, CleanLink, \
         DocumentHeader
    from link_analysis import converters
    from link_analysis._CodeParsers import _get_next_dec_for_link_checking
else:
    from models import Header, RoughLink, Positions, CleanLink, \
        DocumentHeader
    import converters
    from _CodeParsers import _get_next_dec_for_link_checking


class KsrfParser:
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
