# coding=utf-8
# Coded by Aleksandr Rodionov
# rexarrior@yandex.ru


# other imports---------------------------------------------------------
import os.path
from datetime import date

from dateutil import parser
# License: Apache Software License, BSD License (Dual License)

# imports Core modules--------------------------------------------------
import final_analysis
import models
import rough_analysis
import visualizer
import converters
from web_crawler import ksrf
# methods---------------------------------------------------------------


# internal methods------------------------------------------------------
DECISIONS_FOLDER_NAME = 'Decision files'
JSON_HEADERS_FILENAME = 'DecisionHeaders.json'
PICKLE_HEADERS_FILENAME = 'DecisionHeaders.pickle'
PATH_TO_JSON_HEADERS = os.path.join(DECISIONS_FOLDER_NAME,
                                    JSON_HEADERS_FILENAME)
PATH_TO_PICKLE_HEADERS = os.path.join(DECISIONS_FOLDER_NAME,
                                      PICKLE_HEADERS_FILENAME)
PATH_TO_JSON_GRAPH = 'graph.json'

MY_DEBUG = False

def collect_headers(pathToFileForSave, pagesNum=None):
    headersOld = ksrf.get_decision_headers(pagesNum)
    headersNew = converters.convert_to_class_format(headersOld, models.DocumentHeader)
    converters.save_pickle(headersNew, pathToFileForSave)
    return headersNew


def check_text_location_for_headers(headers, folder):
    '''
    Find files of the documents of the given headers
   and add path to file in Header.text_location if file was found
    '''
    for key in headers:
        # generate a possible path according to previously established rules
        pathToTextLocation = ksrf.get_possible_text_location(
            key, folder, ext='txt')
        # if path is exist put it to header
        if (os.path.exists(pathToTextLocation)):
            headers[key].text_location = pathToTextLocation


def download_texts_for_headers(headers, folder=DECISIONS_FOLDER_NAME):
    for key in headers:
        if (isinstance(headers[key], models.Header) and
            (headers[key].text_location is None or
                not os.path.exists(headers[key].text_location))):
            oldFormatHeader = headers[key].convert_to_dict()
            ksrf.download_decision_texts({key: oldFormatHeader}, folder)


def load_graph(pathToGraph=PATH_TO_JSON_GRAPH):
    '''
    Load the stored earlier graph from the given filename,
    unpack it with JSON and return as
    [[nodes], [edges: [from, to, weight]]
    '''
    return converters.load_json(pathToGraph)


# TO DO: Rewrite function after rewriting final_analysis module
def load_and_visualize(pathTograph=PATH_TO_JSON_GRAPH):
    '''
    Load the stored earlier graph from the given filename and
    Visualize it with Visualizer module.
    '''
    graph = load_graph(pathTograph)
    visualizer.visualize_link_graph(graph, 20, 1, (20, 20))


# api methods-----------------------------------------------------------


def process_period(
        firstDateOfDocsForProcessing=None, lastDateOfDocsForProcessing=None,
        docTypesForProcessing=None,
        firstDateForNodes=None, lastDateForNodes=None,
        nodesIndegreeRange=None, nodesOutdegreeRange=None, nodesTypes=None,
        includeIsolatedNodes=True,
        firstDateFrom=None, lastDateFrom=None, docTypesFrom=None,
        firstDateTo=None, lastDateTo=None, docTypesTo=None,
        weightsRange=None,
        graphOutputFilePath=PATH_TO_JSON_GRAPH,
        showPicture=True, isNeedReloadHeaders=False):
    '''
    Process decisions from the date specified as firstDate to
    the date specified as lastDate.
    Write a graph of result of the processing and, if it was specified,
    draw graph and show it to user.
    '''
    if isinstance(firstDateOfDocsForProcessing, str):
        firstDateOfDocsForProcessing = parser.parse(
            firstDateOfDocsForProcessing, dayfirst=True).date()
    if isinstance(lastDateOfDocsForProcessing, str):
        lastDateOfDocsForProcessing = parser.parse(
            lastDateOfDocsForProcessing, dayfirst=True).date()
    if (firstDateOfDocsForProcessing is not None and
        lastDateOfDocsForProcessing is not None and
            firstDateOfDocsForProcessing > lastDateOfDocsForProcessing):
        raise ValueError("date error: The first date is later"
                         "than the last date.")

    if isinstance(firstDateForNodes, str):
        firstDateForNodes = parser.parse(
            firstDateForNodes, dayfirst=True).date()
    if isinstance(lastDateForNodes, str):
        lastDateForNodes = parser.parse(
            lastDateForNodes, dayfirst=True).date()
    if (firstDateForNodes is not None and
        lastDateForNodes is not None and
            firstDateForNodes > lastDateForNodes):
        raise ValueError("date error: The first date is later"
                         "than the last date.")

    if isinstance(firstDateFrom, str):
        firstDateFrom = parser.parse(
            firstDateFrom, dayfirst=True).date()
    if isinstance(lastDateFrom, str):
        lastDateFrom = parser.parse(
            lastDateFrom, dayfirst=True).date()
    if (firstDateFrom is not None and
        lastDateFrom is not None and
            firstDateFrom > lastDateFrom):
        raise ValueError("date error: The first date is later than the last date.")

    if isinstance(firstDateTo, str):
        firstDateTo = parser.parse(
            firstDateTo, dayfirst=True).date()
    if isinstance(lastDateTo, str):
        lastDateTo = parser.parse(
            lastDateTo, dayfirst=True).date()
    if (firstDateTo is not None and
        lastDateTo is not None and
            firstDateTo > lastDateTo):
        raise ValueError("date error: The first date is later than the last date.")

    decisionsHeaders = {}
    if (isNeedReloadHeaders or not os.path.exists(PATH_TO_PICKLE_HEADERS)):
        num = 3  # stub, del after web_crawler updating
        decisionsHeaders = collect_headers(PATH_TO_PICKLE_HEADERS, num)
    else:
        decisionsHeaders = converters.load_pickle(PATH_TO_PICKLE_HEADERS)

    hFilter = models.HeadersFilter(
        docTypesForProcessing,
        firstDateOfDocsForProcessing, lastDateOfDocsForProcessing)
    usingHeaders = hFilter.get_filtered_headers(decisionsHeaders)

    check_text_location_for_headers(usingHeaders, DECISIONS_FOLDER_NAME)


    download_texts_for_headers(usingHeaders, DECISIONS_FOLDER_NAME)

    decisionsHeaders.update(usingHeaders)

    converters.save_pickle(decisionsHeaders, PATH_TO_PICKLE_HEADERS)

    roughLinksDict = \
        rough_analysis.get_rough_links_for_multiple_docs(usingHeaders)
    if (rough_analysis.PATH_NONE_VALUE_KEY in roughLinksDict or
            rough_analysis.PATH_NOT_EXIST_KEY in roughLinksDict):
        raise ValueError('Some headers have no text')
    links = final_analysis.get_clean_links(roughLinksDict,
                                           decisionsHeaders)[0]
   
    if MY_DEBUG:
        converters.save_pickle(links, 'allCleanLinks.pickle')
    linkGraph = final_analysis.get_link_graph(links)
    if MY_DEBUG:
        converters.save_pickle(linkGraph, 'linkGraph.pickle')
    nFilter = models.GraphNodesFilter(
        nodesTypes, firstDateForNodes, lastDateForNodes, nodesIndegreeRange,
        nodesOutdegreeRange)
    hFromFilter = models.HeadersFilter(
        docTypesFrom,
        firstDateFrom, lastDateFrom)
    hToFilter = models.HeadersFilter(
        docTypesTo,
        firstDateTo, lastDateTo)
    eFilter = models.GraphEdgesFilter(hFromFilter, hToFilter, weightsRange)
    subgraph = linkGraph.get_subgraph(nFilter, eFilter, includeIsolatedNodes)
    if MY_DEBUG:
        converters.save_pickle(subgraph, 'subgraph.pickle')
    linkGraphLists = (subgraph.get_nodes_as_IDs_list(),
                      subgraph.get_edges_as_list_of_tuples())

    converters.save_json(linkGraphLists, graphOutputFilePath)
    if showPicture:
        visualizer.visualize_link_graph(linkGraphLists, 20, 1, (40, 40))
# end of ProcessPeriod--------------------------------------------------


def start_process_with(
        decisionID, depth,
        firstDateForNodes=None, lastDateForNodes=None, nodesIndegreeRange=None,
        nodesOutdegreeRange=None, nodesTypes=None, includeIsolatedNodes=True,
        firstDateFrom=None, lastDateFrom=None, docTypesFrom=None,
        firstDateTo=None, lastDateTo=None, docTypesTo=None,
        weightsRange=None,
        graphOutputFilePath=PATH_TO_JSON_GRAPH,
        showPicture=True, isNeedReloadHeaders=False,
        visualizerParameters=(20, 1, (40, 40))):
    '''
    Start processing decisions from the decision which uid was given and repeat
    this behavior recursively for given depth.
    '''
    if (depth < 0):
        raise "argument error: depth of the recursion must be large than 0."

    if isNeedReloadHeaders or not os.path.exists(PATH_TO_PICKLE_HEADERS):
        num = 3  # stub, del after web_crawler updating
        headers = collect_headers(PATH_TO_PICKLE_HEADERS, num)
    else:
        headers = converters.load_pickle(PATH_TO_PICKLE_HEADERS)
    if (decisionID not in headers):
        raise ValueError("Unknown uid")

    if isinstance(firstDateForNodes, str):
        firstDateForNodes = parser.parse(
            firstDateForNodes, dayfirst=True).date()
    if isinstance(lastDateForNodes, str):
        lastDateForNodes = parser.parse(
            lastDateForNodes, dayfirst=True).date()
    if (firstDateForNodes is not None and
        lastDateForNodes is not None and
            firstDateForNodes > lastDateForNodes):
        raise ValueError("date error: The first date is later than the last date.")

    if isinstance(firstDateFrom, str):
        firstDateFrom = parser.parse(
            firstDateFrom, dayfirst=True).date()
    if isinstance(lastDateFrom, str):
        lastDateFrom = parser.parse(
            lastDateFrom, dayfirst=True).date()
    if (firstDateFrom is not None and
        lastDateFrom is not None and
            firstDateFrom > lastDateFrom):
        raise ValueError("date error: The first date is later than the last date.")

    if isinstance(firstDateTo, str):
        firstDateTo = parser.parse(
            firstDateTo, dayfirst=True).date()
    if isinstance(lastDateTo, str):
        lastDateTo = parser.parse(
            lastDateTo, dayfirst=True).date()
    if (firstDateTo is not None and
        lastDateTo is not None and
            firstDateTo > lastDateTo):
        raise ValueError("date error: The first date is later than the last date.")

    check_text_location_for_headers(headers, DECISIONS_FOLDER_NAME)
    download_texts_for_headers(headers, DECISIONS_FOLDER_NAME)

    toProcess = {decisionID: headers[decisionID]}
    processed = {}
    allLinks = {headers[decisionID]: []}
    while depth > 0 and len(toProcess) > 0:
        depth -= 1
        roughLinksDict = rough_analysis.get_rough_links_for_multiple_docs(
            toProcess)
        if (rough_analysis.PATH_NONE_VALUE_KEY in roughLinksDict or
                rough_analysis.PATH_NOT_EXIST_KEY) in roughLinksDict:
            raise ValueError('Some headers have not text')
        cleanLinks = final_analysis.get_clean_links(roughLinksDict, headers)[0]
        allLinks.update(cleanLinks)
        processed.update(toProcess)
        toProcess = {}
        for decID in cleanLinks:
            for cl in cleanLinks[decID]:
                docID = cl.header_to.doc_id
                if (docID not in processed):
                    toProcess[docID] = headers[docID]

    linkGraph = final_analysis.get_link_graph(allLinks)
    if MY_DEBUG:
        converters.save_pickle(processed, 'processWithHeaders.pickle')
        converters.save_pickle(processed, 'processWithGraph.pickle')
    nFilter = models.GraphNodesFilter(
        nodesTypes, firstDateForNodes, lastDateForNodes, nodesIndegreeRange,
        nodesOutdegreeRange)
    hFromFilter = models.HeadersFilter(
        docTypesFrom,
        firstDateFrom, lastDateFrom)
    hToFilter = models.HeadersFilter(
        docTypesTo,
        firstDateTo, lastDateTo)
    eFilter = models.GraphEdgesFilter(hFromFilter, hToFilter, weightsRange)
    subgraph = linkGraph.get_subgraph(nFilter, eFilter, includeIsolatedNodes)
    if MY_DEBUG:
        converters.save_pickle(subgraph, 'processWithSubgraph.pickle')
    linkGraphLists = (subgraph.get_nodes_as_IDs_list(),
                      subgraph.get_edges_as_list_of_tuples())

    converters.save_json(linkGraphLists, graphOutputFilePath)
    if (showPicture):
        visualizer.visualize_link_graph(linkGraphLists,
                                        visualizerParameters[0],
                                        visualizerParameters[1],
                                        visualizerParameters[2])
# end of start_process_with---------------------------------------------

if __name__ == "__main__":
    import time
    start_time = time.time()
    # process_period("18.06.1980", "18.07.2020", showPicture=False,
    #                isNeedReloadHeaders=False, includeIsolatedNodes=True)

    # process_period(
    #     firstDateOfDocsForProcessing='18.03.2013',
    #     lastDateOfDocsForProcessing='14.08.2018',
    #     docTypesForProcessing={'КСРФ/О', 'КСРФ/П'},
    #     firstDateForNodes='18.03.2014', lastDateForNodes='14.08.2017',
    #     nodesIndegreeRange=(0, 25), nodesOutdegreeRange=(0, 25),
    #     nodesTypes={'КСРФ/О', 'КСРФ/П'},
    #     includeIsolatedNodes=False,
    #     firstDateFrom='18.03.2016', lastDateFrom='14.08.2016',
    #     docTypesFrom={'КСРФ/О', 'КСРФ/П'},
    #     firstDateTo='18.03.2015', lastDateTo='14.08.2015',
    #     docTypesTo={'КСРФ/О', 'КСРФ/П'},
    #     weightsRange=(1, 5),
    #     graphOutputFilePath=PATH_TO_JSON_GRAPH,
    #     showPicture=True, isNeedReloadHeaders=False)
    
    # start_process_with(decisionID='КСРФ/1-П/2015', depth=3)
    # load_and_visualize()
    start_process_with(
        decisionID='КСРФ/1-П/2015', depth=10,
        firstDateForNodes='18.03.2014', lastDateForNodes='14.08.2018',
        nodesIndegreeRange=(0, 25), nodesOutdegreeRange=(0, 25),
        nodesTypes={'КСРФ/О', 'КСРФ/П'},
        includeIsolatedNodes=False,
        firstDateFrom='18.03.2011', lastDateFrom='14.08.2019',
        docTypesFrom={'КСРФ/О', 'КСРФ/П'},
        firstDateTo='18.03.2011', lastDateTo='14.08.2018',
        docTypesTo={'КСРФ/О', 'КСРФ/П'},
        weightsRange=(1, 5),
        graphOutputFilePath=PATH_TO_JSON_GRAPH,
        showPicture=True, isNeedReloadHeaders=False)

    print(f"Headers collection spent {time.time()-start_time} seconds.")
    # get_only_unique_headers()
    input('press any key...')