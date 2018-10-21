# coding=utf-8
# Coded by Aleksandr Rodionov
# rexarrior@yandex.ru


# other imports---------------------------------------------------------
import os.path
from datetime import date


# imports Core modules--------------------------------------------------
import link_analysis.final_analysis as final_analysis
import link_analysis.models as models
import link_analysis.rough_analysis as rough_analysis
import link_analysis.visualizer as visualizer
import link_analysis.converters as converters
import web_crawler.ksrf as web_crawler

from dateutil import parser
# License: Apache Software License, BSD License (Dual License)

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


def collect_headers(pathToFileForSave, pagesNum):
    # TO DO: remake format returning by web_crawler
    headersOld = web_crawler.get_resolution_headers(pagesNum)
    headersNew = converters.convert_dictDict_to_dictDocumentHeader(headersOld)
    converters.save_pickle(headersNew, pathToFileForSave)
    return headersNew


def check_text_location_for_headers(headers, folder):
    '''
    Find files of the documents of the given headers
   and add path to file in Header.text_location if file was found
    '''
    for key in headers:
        # generate a possible path according to previously established rules
        pathToTextLocation = web_crawler.get_decision_filename_by_uid(
            key, folder, ext='txt')
        # if path is exist put it to header
        if (os.path.exists(pathToTextLocation)):
            headers[key].text_location = pathToTextLocation


def download_texts_for_headers(headers, folder=DECISIONS_FOLDER_NAME):
    for key in headers:
        if (isinstance(headers[key], models.Header) and
            (headers[key].text_location is None or
                not os.path.exists(headers[key].text_location))):

            # TO DO: remake loading by web_crawler
            web_crawler.load_resolution_texts({key: headers[key]}, folder)


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


# TO DO: Rewrite all functions below this line.
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
    if firstDateOfDocsForProcessing is None:
        firstDateOfDocsForProcessing = date.min
    if lastDateOfDocsForProcessing is None:
        lastDateOfDocsForProcessing = date.max
    if isinstance(firstDateOfDocsForProcessing, str):
        firstDateOfDocsForProcessing = parser.parse(
            firstDateOfDocsForProcessing, dayfirst=True).date()
    if isinstance(lastDateOfDocsForProcessing, str):
        lastDateOfDocsForProcessing = parser.parse(
            lastDateOfDocsForProcessing, dayfirst=True).date()
    if (firstDateOfDocsForProcessing > lastDateOfDocsForProcessing):
        raise "date error: The first date is later than the last date."

    if firstDateForNodes is None:
        firstDateForNodes = date.min
    if lastDateForNodes is None:
        lastDateForNodes = date.max
    if isinstance(firstDateForNodes, str):
        firstDateForNodes = parser.parse(
            firstDateForNodes, dayfirst=True).date()
    if isinstance(lastDateForNodes, str):
        lastDateForNodes = parser.parse(
            lastDateForNodes, dayfirst=True).date()
    if (firstDateForNodes > lastDateForNodes):
        raise "date error: The first date is later than the last date. "

    if firstDateFrom is None:
        firstDateFrom = date.min
    if lastDateFrom is None:
        lastDateFrom = date.max
    if isinstance(firstDateFrom, str):
        firstDateFrom = parser.parse(
            firstDateFrom, dayfirst=True).date()
    if isinstance(lastDateFrom, str):
        lastDateFrom = parser.parse(
            lastDateFrom, dayfirst=True).date()
    if (firstDateFrom > lastDateFrom):
        raise "date error: The first date is later than the last date. "

    if firstDateTo is None:
        firstDateTo = date.min
    if lastDateTo is None:
        lastDateTo = date.max
    if isinstance(firstDateTo, str):
        firstDateTo = parser.parse(
            firstDateTo, dayfirst=True).date()
    if isinstance(lastDateTo, str):
        lastDateTo = parser.parse(
            lastDateTo, dayfirst=True).date()
    if (firstDateTo > lastDateTo):
        raise "date error: The first date is later than the last date. "

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

    linkGraph = final_analysis.get_link_graph(links)
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
        isShowPicture=True, isNeedReloadHeaders=False,
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
        raise "Unknown uid"

    if firstDateForNodes is None:
        firstDateForNodes = date.min
    if lastDateForNodes is None:
        lastDateForNodes = date.max
    if isinstance(firstDateForNodes, str):
        firstDateForNodes = parser.parse(
            firstDateForNodes, dayfirst=True).date()
    if isinstance(lastDateForNodes, str):
        lastDateForNodes = parser.parse(
            lastDateForNodes, dayfirst=True).date()
    if (firstDateForNodes > lastDateForNodes):
        raise "date error: The first date is later than the last date. "

    if firstDateFrom is None:
        firstDateFrom = date.min
    if lastDateFrom is None:
        lastDateFrom = date.max
    if isinstance(firstDateFrom, str):
        firstDateFrom = parser.parse(
            firstDateFrom, dayfirst=True).date()
    if isinstance(lastDateFrom, str):
        lastDateFrom = parser.parse(
            lastDateFrom, dayfirst=True).date()
    if (firstDateFrom > lastDateFrom):
        raise "date error: The first date is later than the last date. "

    if firstDateTo is None:
        firstDateTo = date.min
    if lastDateTo is None:
        lastDateTo = date.max
    if isinstance(firstDateTo, str):
        firstDateTo = parser.parse(
            firstDateTo, dayfirst=True).date()
    if isinstance(lastDateTo, str):
        lastDateTo = parser.parse(
            lastDateTo, dayfirst=True).date()
    if (firstDateTo > lastDateTo):
        raise "date error: The first date is later than the last date. "

    check_text_location_for_headers(headers, DECISIONS_FOLDER_NAME)
    download_texts_for_headers(headers, DECISIONS_FOLDER_NAME)

    toProcess = {decisionID: headers[decisionID]}
    processed = {}
    allLinks = {decisionID: []}
    while depth > 0 and len(toProcess) > 0:
        depth -= 1
        roughLinksDict = rough_analysis.get_rough_links_for_multiple_docs(
            toProcess)
        if (rough_analysis.PATH_NONE_VALUE_KEY in roughLinksDict or
                rough_analysis.PATH_NOT_EXIST_KEY) in roughLinksDict:
            raise 'Some headers have not text'
        cleanLinks = final_analysis.get_clean_links(roughLinksDict, headers)[0]
        allLinks.update(cleanLinks)
        processed.update(toProcess)
        toProcess = {}
        for decID in cleanLinks:
            for cl in cleanLinks[decID]:
                id_ = cl.header_to.id
                if (id_ not in processed):
                    toProcess[id_] = headers[id_]

    linkGraph = final_analysis.get_link_graph(allLinks)
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
    linkGraphLists = (subgraph.get_nodes_as_IDs_list(),
                      subgraph.get_edges_as_list_of_tuples())

    converters.save_json(linkGraphLists, graphOutputFilePath)
    if (isShowPicture):
        visualizer.visualize_link_graph(linkGraphLists,
                                        visualizerParameters[0],
                                        visualizerParameters[1],
                                        visualizerParameters[2])
# end of start_process_with---------------------------------------------

if __name__ == "__main__":
    # process_period("18.06.1980", "18.07.2020", showPicture=False,
    #                isNeedReloadHeaders=False)
    process_period(
        firstDateOfDocsForProcessing='18.03.2013', lastDateOfDocsForProcessing='14.08.2018',
        docTypesForProcessing={'КСРФ/О', 'КСРФ/П'},
        firstDateForNodes='18.03.2014', lastDateForNodes='14.08.2017',
        nodesIndegreeRange=(0, 25), nodesOutdegreeRange=(0, 25), nodesTypes={'КСРФ/О', 'КСРФ/П'},
        includeIsolatedNodes=True,
        firstDateFrom='18.03.2016', lastDateFrom='14.08.2016', docTypesFrom={'КСРФ/О', 'КСРФ/П'},
        firstDateTo='18.03.2015', lastDateTo='14.08.2015', docTypesTo={'КСРФ/О', 'КСРФ/П'},
        weightsRange=(1, 5),
        graphOutputFilePath=PATH_TO_JSON_GRAPH,
        showPicture=True, isNeedReloadHeaders=False)
    print('all done')
