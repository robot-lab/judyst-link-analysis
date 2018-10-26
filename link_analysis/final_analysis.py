import re
from models import Header, CleanLink, Positions
from models import LinkGraph
from rough_analysis import RoughLink
from typing import Dict, Tuple, List, Union
yearPattern = re.compile(r'(?<=\s)\d{4}(?=\s)')
numberPattern = re.compile(r'\d+(-[А-Яа-я]+)+')
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

if __name__ == '__main__':
    courtSiteContent = {}
    collectedLinks = {}
    courtSiteContent['1-П/2002'] = {
        'date': '15.01.2002',
        'title': 'бла-бла',
        'url': 'http://doc.ksrf.ru/decision/KSRFDecision30284.pdf'
        }
    courtSiteContent['8-П/2003'] = {
        'date': '14.05.2003',
        'title': 'бла-бла',
        'url': 'http://doc.ksrf.ru/decision/KSRFDecision30345.pdf'
        }
    courtSiteContent['8-П/2005'] = {
        'date': '14.07.2005',
        'title': 'бла-бла',
        'url': 'http://doc.ksrf.ru/decision/KSRFDecision30352.pdf'
        }
    courtSiteContent['10-П/2007'] = {
        'date': '12.07.2007',
        'title': 'бла-бла',
        'url': 'http://doc.ksrf.ru/decision/KSRFDecision19712.pdf'
        }
    courtSiteContent['4-П/2010'] = {
        'date': '26.02.2010',
        'title': 'бла-бла',
        'url': 'http://doc.ksrf.ru/decision/KSRFDecision36802.pdf'
        }
    courtSiteContent['11-П/2012'] = {
        'date': '14.05.2012',
        'title': 'бла-бла',
        'url': 'http://doc.ksrf.ru/decision/KSRFDecision99813.pdf'
        }
    courtSiteContent['7-П/2016'] = {
        'date': '10.03.2016',
        'title': 'бла-бла',
        'url': 'http://doc.ksrf.ru/decision/KSRFDecision225558.pdf'
        }
    courtSiteContent['1-П/2001'] = {
        'date': '25.01.2001',
        'title': 'бла-бла',
        'url': 'http://doc.ksrf.ru/decision/KSRFDecision30415.pdf'
        }
    courtSiteContent['7-П/1995'] = {
        'date': '06.06.1995',
        'title': 'бла-бла',
        'url': 'http://doc.ksrf.ru/decision/KSRFDecision30417.pdf'
        }
    courtSiteContent['14-П/1996'] = {
        'date': '13.06.1996',
        'title': 'бла-бла',
        'url': 'http://doc.ksrf.ru/decision/KSRFDecision30276.pdf'
        }
    courtSiteContent['14-П/1999'] = {
        'date': '28.10.1999',
        'title': 'бла-бла',
        'url': 'http://doc.ksrf.ru/decision/KSRFDecision30307.pdf'
        }
    courtSiteContent['14-П/2000'] = {
        'date': '22.11.2000',
        'title': 'бла-бла',
        'url': 'http://doc.ksrf.ru/decision/KSRFDecision30294.pdf'
        }
    courtSiteContent['12-П/2003'] = {
        'date': '14.07.2003',
        'title': 'бла-бла',
        'url': 'http://doc.ksrf.ru/decision/KSRFDecision30381.pdf'
        }
    courtSiteContent['6-П/2015'] = {
        'date': '31.03.2015',
        'title': 'бла-бла',
        'url': 'http://doc.ksrf.ru/decision/KSRFDecision191663.pdf'
        }
    courtSiteContent['11-П/2002'] = {
        'date': '19.06.2002',
        'title': 'бла-бла',
        'url': 'http://doc.ksrf.ru/decision/KSRFDecision30304.pdf'
        }
    courtSiteContent['244-О-П/2008'] = {
        'date': '20.03.2008',
        'title': 'бла-бла',
        'url': 'http://doc.ksrf.ru/decision/KSRFDecision17279.pdf'
        }
    courtSiteContent['738-О-О/2008'] = {
        'date': '06.10.2008',
        'title': 'бла-бла',
        'url': 'http://doc.ksrf.ru/decision/KSRFDecision17779.pdf'
        }
    courtSiteContent['1469-О/2015'] = {
        'date': '23.06.2015',
        'title': 'бла-бла',
        'url': 'http://doc.ksrf.ru/decision/KSRFDecision203108.pdf'
        }
    courtSiteContent['364-О/2005'] = {
        'date': '04.10.2005',
        'title': 'бла-бла',
        'url': 'http://doc.ksrf.ru/decision/KSRFDecision31253.pdf'
        }

    collectedLinks['35-П/2018'] = [
        'от 15 января 2002 года № 1-П',
        'от 14 мая 2003 6 года №8-П',
        'от 14 июля 2005 года № 8-П',
        'от 12 июля 2007 года № 10-П',
        'от 26 февраля 2010 года № 4-П',
        'от 14 мая 2012 года № 11-П',
        'от 10 марта 2016 года № 7-П',
        'от 25 января 2001 года № 1-П',
        'от 6 июня 1995 года № 7-П',
        'от 13 июня 1996 года № 14-П',
        'от 28 октября 1999 года № 14-П',
        'от 22 ноября 2000 года № 14-П',
        'от 14 июля 2003 года № 12-П',
        'от 12 июля 2007 года № 10-П',
        'от 31 марта 2015 года № 6-П',
        'от 19 июня 2002 года № 11-П',
        'от 20 марта 2008 года № 244-О-П',
        'от 6 октября 2008 года № 738-О-О',
        'от 23 июня 2015 года № 1469-О',
        'от 23 июня 2015 года № 1469-О',
        'от 4 октября 2005 года № 364-О'
        ]

    # response = get_clean_links(collectedLinks, courtSiteContent)
    # checkedLinks = response[0]
    # rejectedLinks = response[1]
    # print("Checked links: ")
    # print(checkedLinks)
    # print("Rejected links: ")
    # print(rejectedLinks)

    # reponse2 = get_link_graph(checkedLinks)
    # vertices = reponse2[0]
    # edges = reponse2[1]
    # print("Vertices: ")
    # print(vertices)
    # print("Edge list: ")
    # print(edges)
    print('ok')
