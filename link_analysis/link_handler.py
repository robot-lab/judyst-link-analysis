import re
import os
from typing import Dict, List, Type, Set, Iterator

import json
import dateutil

if __package__:
    from link_analysis.models import Header, RoughLink, Positions, CleanLink, \
         LinkGraph, DocumentHeader
    from link_analysis import wc_interface
    from link_analysis import converters
    from link_analysis._KsrfParser import KsrfParser
    from link_analysis._CodeParsers import KoaprfCodeParser, GkrfCodeParser, \
        NkrfCodeParser, UkrfCodeParser, _get_next_dec_for_link_checking, \
        PATH_TO_JSON_HEADERS_FOR_CHECKING_LINKS_FILENAME
else:
    from models import Header, RoughLink, Positions, CleanLink, LinkGraph, \
        DocumentHeader
    import wc_interface
    import converters
    from _KsrfParser import KsrfParser
    from _CodeParsers import KoaprfCodeParser, GkrfCodeParser, \
        NkrfCodeParser, UkrfCodeParser, _get_next_dec_for_link_checking, \
        PATH_TO_JSON_HEADERS_FOR_CHECKING_LINKS_FILENAME

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


def _sentenceSeparator(text: str):  # -> Iterator[SRE_MATCH_TYPE]:
    return sentencePattern.finditer(text)


_parsersDict = {
    'КСРФ': KsrfParser,
    'ГКРФ': GkrfCodeParser,
    'НКРФ': NkrfCodeParser,
    'КОАПРФ': KoaprfCodeParser,
    'УКРФ': UkrfCodeParser
}

_NnDelPattern = re.compile(r'-N\d+-')


def parse(headersToParsing: Dict[str, Header], headersBase: Dict[str, Header],
          supertypes: Set[str]) -> Dict[Header, CleanLink]:

    def get_headersForCheckingLinks():
        import time
        start_time = time.time()

        def rekey(hs):
            dateKeyedHs = {}
            for key in hs:
                try:
                    datekey = dateutil.parser.parse(key, dayfirst=True).date()
                except ValueError:
                    continue
                dateKeyedHs[datekey] = hs[key]
            return dateKeyedHs
        print('Start to prepare headers for checking links.')  # debug print
        PREPARED_FILE_NAME = 'preparedFileForCheckingLinks.json'
        PATH_TO_PREPARED_FILE = os.path.join(
            os.path.dirname(PATH_TO_JSON_HEADERS_FOR_CHECKING_LINKS_FILENAME),
            PREPARED_FILE_NAME)
        if os.path.exists(PATH_TO_PREPARED_FILE):
            hs = converters.load_json(PATH_TO_PREPARED_FILE)
            dateKeyedHs = rekey(hs)
            print(f'Finish to prepare headers for checking links. '
                  f'It spent {time.time()-start_time} seconds.')  # debug print
            return dateKeyedHs
        hs = {}
        for decs in _get_next_dec_for_link_checking(1000):
            for key in decs:
                if decs[key]['supertype'] not in supertypes:
                    continue
                try:
                    effectiveDate = decs[key]['effective_date']
                except KeyError:
                    continue
                try:
                    dateutil.parser.parse(effectiveDate, dayfirst=True).date()
                except ValueError:
                    continue
                if effectiveDate not in hs:
                    hs[effectiveDate] = {}
                hs[effectiveDate][_NnDelPattern.sub('-', key)] = key
        converters.save_json(hs, PATH_TO_PREPARED_FILE)
        dateKeyedHs = rekey(hs)
        print(f'Finish to prepare headers for checking links. '
              f'It spent {time.time()-start_time} seconds.')  # debug print
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
            f'Find links in document {docCounter}/{len(headersToParsing)}...'
            f' doc_id: {doc_id:40}', end='\r')  # debug print
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
