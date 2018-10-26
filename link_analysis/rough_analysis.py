import re
from typing import Dict, List, Union, Type

if __package__:
    from link_analysis.models import Header, RoughLink, Positions
    from link_analysis import wc_interface
else:
    from models import Header, RoughLink, Positions
    import wc_interface

# link pattern main part
lpMP = (r".*?\sот[\s\d]+?(?:(?:января|февраля|марта|апреля|мая|июня|июля|"
        r"августа|сентября|октября|ноября|декабря)+?[\s\d]+?года|\d{2}\."
        r"\d{2}\.\d{4})[\s\d]+?(?:№|N)[\s\d]+?[-\w/]*.*?")
# link pattern prefix #1
lpPRF1 = r"(?<=\.\s)\s*?[А-ЯA-Z]"
# link pattern postfix #1
lpPSF1 = r"(?=\.\s[А-ЯA-Z])"
# link pattern prefix #2
lpPRF2 = r"(?<=^)\s*?[А-ЯA-Zа-яa-z]"
# link pattern postfix #2
lpPSF2 = r"(?=\.$)"
linkPattern = re.compile(f"""(?:{lpPRF1+lpMP+lpPSF1}|{lpPRF1+lpMP+lpPSF2}|
            {lpPRF2+lpMP+lpPSF1}|{lpPRF2+lpMP+lpPSF2})""", re.VERBOSE)

# pattern for removing of redundant leading sentences
reductionPattern = re.compile(r"(?:[А-ЯA-Z].*[^А-ЯA-Z]\.\s*(?=[А-ЯA-Z])|^[А-ЯA-Zа-яa-z]"
                              r".*[^А-ЯA-Z]\.\s*(?=[А-ЯA-Z]))")

# other patterns
splitPattern = re.compile(r"""(?i)о(?=т[\s\d]+?(?:(?:января|февраля|марта|апреля|мая|июня|июля|
            августа|сентября|октября|ноября|декабря)+?[\s\d]+?года|\d{2}
            \.\d{2}\.\d{4})[\s\d]+?(?:№|N))""")
datePattern = re.compile(r"""(?i)т[\s\d]+?(?:(?:января|февраля|марта|апреля|мая|июня|июля|
            августа|сентября|октября|ноября|декабря)+?[\s\d]+?года|\d{2}
            \.\d{2}\.\d{4})(?=\s)""")
numberPattern = re.compile(r'(?:№|N)[\s\d]+[-\w/]*')
opinionPattern = re.compile(r'(?i)мнение\s+судьи\s+конституционного')


def get_rough_links(header: Header) -> Union[List[RoughLink], Type[TypeError], Type[FileNotFoundError]]:
    """
    :param header: instance of class models.Header
    """
    text = wc_interface.get_text(header.doc_id)
    if not text:
        print(f"fileID: {header.doc_id}")
        raise ValueError("Where's the text, Lebowski?")
    roughLinks = []
    opinion = opinionPattern.search(text)
    if opinion is not None:
        matchObjects = linkPattern.finditer(text, endpos=opinion.start())
    else:
        matchObjects = linkPattern.finditer(text)
    for match in matchObjects:
        linksForSplit = match[0]
        reduct = reductionPattern.search(linksForSplit)
        if reduct is not None:
            reductCorrection = reduct.end()
            #context = linksForSplit.replace(reduct[0], '') + '.'
        else:
            reductCorrection = 0
            #context = linksForSplit
        linkCorrection = len(splitPattern.split(linksForSplit,
                                        maxsplit=1)[0])
        contextStartPos = match.start(0) + reductCorrection
        contextEndPos = match.end(0) + 1
        linkStartPos = match.start(0) + linkCorrection 

        splitedLinksForDifferentYears = splitPattern.split(linksForSplit)[1:]
        for oneYearLinks in splitedLinksForDifferentYears:
            date = datePattern.search(oneYearLinks)[0]
            matchNumbers = list(numberPattern.finditer(oneYearLinks))

            linkEndPos = linkStartPos + matchNumbers[-1].end(0) + 1
            for number in matchNumbers:
                gottenRoughLink = 'о' + date + ' ' + number[0].upper()
                roughLinks.append(RoughLink(header, gottenRoughLink,
                                  Positions(contextStartPos, contextEndPos,
                                            linkStartPos, linkEndPos)))
            linkStartPos += len(oneYearLinks) + 1           
    return roughLinks


def get_rough_links_for_docs(
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
            raise TypeError(f"Any element of 'headers' must be instance of {Header}")
        maybeRoughLinks = get_rough_links(headers[decisionID])
        result[headers[decisionID]] = maybeRoughLinks
    return result


if (__name__ == '__main__'):
    print('ok')