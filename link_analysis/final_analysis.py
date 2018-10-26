import re
from models import Header, CleanLink, Positions
from models import LinkGraph
from rough_analysis import RoughLink
from typing import Dict, Tuple, List, Union

yearPattern = re.compile(r'(?:(?<=\s)\d{4}(?=\s)|(?<=\d\d\.\d\d\.)\d{4}(?=\s))')
numberPattern = re.compile(r'\d+(-[А-ЯA-Zа-яa-z]+)+')
splitPattern = re.compile(r'(?:№|N)')


def get_clean_links(
        collectedLinks: Dict[Header, List[RoughLink]],
        courtSiteContent: Dict[str, Header],
        courtPrefix: str='КСРФ/') -> Tuple[Dict[Header, List[CleanLink]],
                                           Dict[Header, List[RoughLink]]]:
    '''
    Gets clean links.
    arguments:
    collected_links: a dictionary with list of instances of class Rough link
    as element and instance class Header as key.
    court_site_content: a dictionary with intance of class DocumentHeader
    as element and string with court decision ID (uid) as a key.
    '''
    rejectedLinks = {}  # type: Dict[Header, List[RoughLink]]
    checkedLinks = {}  # type: Dict[Header, List[CleanLink]]
    for headerFrom in collectedLinks:
        checkedLinks[headerFrom] = []
        for link in collectedLinks[headerFrom]:
            spam = splitPattern.split(link.body)
            number = numberPattern.search(spam[-1])
            years = yearPattern.findall(spam[0])
            if years and number:
                eggs = False
                while years:
                    gottenID = (courtPrefix + number[0].upper() +
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