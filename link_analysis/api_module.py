# coding=utf-8
# Coded by Aleksandr Rodionov
# rexarrior@yandex.ru


# other imports---------------------------------------------------------
import os.path
import datetime
import time
import dateutil.parser
# License: Apache Software License, BSD License (Dual License)

# imports Core modules--------------------------------------------------
from web_crawler import ksrf
import web_crawler

if __package__:
    from link_analysis import models
    from link_analysis import visualizer
    from link_analysis import converters
    from link_analysis import link_handler
else:
    import models
    import visualizer
    import converters
    import wc_interface
    import link_handler
# methods---------------------------------------------------------------

# internal methods------------------------------------------------------
DECISIONS_FOLDER_NAME = 'Decision files'
JSON_HEADERS_FILENAME = 'DecisionHeaders.json'
JSON_HEADERS_FOR_CHECKING_LINKS_FILENAME = \
    'ForCheckingLinksDecisionHeaders.jsonlines'
PICKLE_HEADERS_FILENAME = 'DecisionHeaders.pickle'
PATH_TO_JSON_HEADERS = os.path.join(DECISIONS_FOLDER_NAME,
                                    JSON_HEADERS_FILENAME)
PATH_TO_JSON_HEADERS_FOR_CHECKING_LINKS_FILENAME = \
    os.path.join('Decision files',
                 'ForCheckingLinksDecisionHeaders.jsonlines')
PATH_TO_PICKLE_HEADERS = os.path.join(DECISIONS_FOLDER_NAME,
                                      PICKLE_HEADERS_FILENAME)
RESULTS_FOLDER_NAME = 'Results'
PICKLE_GRAPH_FILENAME = 'graph.pickle'
JSON_GRAPH_FILENAME = 'graph.json'
PATH_TO_PICKLE_GRAPH = os.path.join(RESULTS_FOLDER_NAME, PICKLE_GRAPH_FILENAME)
PATH_TO_JSON_GRAPH = os.path.join(RESULTS_FOLDER_NAME, JSON_GRAPH_FILENAME)
PICKLE_SUBGRAPH_FILENAME = 'subgraph.pickle'
JSON_SUBGRAPH_FILENAME = 'subgraph.json'
PATH_TO_PICKLE_SUBGRAPH = os.path.join(RESULTS_FOLDER_NAME,
                                       PICKLE_SUBGRAPH_FILENAME)
PATH_TO_JSON_SUBGRAPH = os.path.join(RESULTS_FOLDER_NAME,
                                     JSON_SUBGRAPH_FILENAME)

SUPERTYPES_TO_PARSE = {'КСРФ'}

MY_DEBUG = True


def load_and_visualize(pathTograph=PATH_TO_JSON_GRAPH):
    '''
    Load the stored earlier graph from the given filename and
    Visualize it with Visualizer module.
    '''
    graph = converters.load_json(pathTograph)
    visualizer.visualize_link_graph(graph, 20, 1, (20, 20))


# api methods-----------------------------------------------------------


def process_period(
        firstDateOfDocsForProcessing=None, lastDateOfDocsForProcessing=None,
        supertypesForProcessing=None,
        docTypesForProcessing=None,
        firstDateForNodes=None, lastDateForNodes=None,
        nodesIndegreeRange=None, nodesOutdegreeRange=None,
        nodesSupertypes=None, nodesTypes=None,
        includeIsolatedNodes=True,
        firstDateFrom=None, lastDateFrom=None, docTypesFrom=None,
        supertypesFrom=None,
        firstDateTo=None, lastDateTo=None, docTypesTo=None,
        supertypesTo=None,
        weightsRange=None,
        graphOutputFilePath=PATH_TO_JSON_GRAPH, showPicture=False,
        takeHeadersFromLocalStorage=False,
        sendRequestToUpdatingHeadersInBaseFromSite=False,
        whichSupertypeUpdateFromSite=None):
    '''
    Process decisions from the date specified as firstDate to
    the date specified as lastDate.
    Write a graph of result of the processing and, if it was specified,
    draw graph and show it to user.
    '''
    if isinstance(firstDateOfDocsForProcessing, str):
        firstDateOfDocsForProcessing = dateutil.parser.parse(
            firstDateOfDocsForProcessing, dayfirst=True).date()
    if isinstance(lastDateOfDocsForProcessing, str):
        lastDateOfDocsForProcessing = dateutil.parser.parse(
            lastDateOfDocsForProcessing, dayfirst=True).date()
    if (firstDateOfDocsForProcessing is not None and
        lastDateOfDocsForProcessing is not None and
            firstDateOfDocsForProcessing > lastDateOfDocsForProcessing):
        raise ValueError("date error: The first date is later"
                         "than the last date.")

    if isinstance(firstDateForNodes, str):
        firstDateForNodes = dateutil.parser.parse(
            firstDateForNodes, dayfirst=True).date()
    if isinstance(lastDateForNodes, str):
        lastDateForNodes = dateutil.parser.parse(
            lastDateForNodes, dayfirst=True).date()
    if (firstDateForNodes is not None and
        lastDateForNodes is not None and
            firstDateForNodes > lastDateForNodes):
        raise ValueError("date error: The first date is later"
                         "than the last date.")

    if isinstance(firstDateFrom, str):
        firstDateFrom = dateutil.parser.parse(
            firstDateFrom, dayfirst=True).date()
    if isinstance(lastDateFrom, str):
        lastDateFrom = dateutil.parser.parse(
            lastDateFrom, dayfirst=True).date()
    if (firstDateFrom is not None and
        lastDateFrom is not None and
            firstDateFrom > lastDateFrom):
        raise ValueError(
            "date error: The first date is later than the last date.")

    if isinstance(firstDateTo, str):
        firstDateTo = dateutil.parser.parse(
            firstDateTo, dayfirst=True).date()
    if isinstance(lastDateTo, str):
        lastDateTo = dateutil.parser.parse(
            lastDateTo, dayfirst=True).date()
    if (firstDateTo is not None and
        lastDateTo is not None and
            firstDateTo > lastDateTo):
        raise ValueError(
            "date error: The first date is later than the last date.")

    if takeHeadersFromLocalStorage:
        jsonHeaders = converters.load_json(PATH_TO_JSON_HEADERS)
    else:
        #TODO: using param 'whichSupertypeReloadFromSite' isn't implemented
        print("Started to getting Headers from web_crawler.")
        jsonHeaders = wc_interface.get_all_headers(
            sendRequestToUpdatingHeadersInBaseFromSite,
            whichSupertypeUpdateFromSite)
        print("Finished getting Headers from web_crawler.")
        converters.save_json(jsonHeaders, PATH_TO_JSON_HEADERS)

    if jsonHeaders is None:
        raise ValueError("Where's the document headers, Lebowski?")

    decisionsHeaders = converters.convert_to_class_format(
        jsonHeaders, models.DocumentHeader)

    #Not using, just backup. Maybe delete later
    converters.save_pickle(decisionsHeaders, PATH_TO_PICKLE_HEADERS)

    hFilter = models.HeadersFilter(
        supertypesForProcessing,
        docTypesForProcessing,
        firstDateOfDocsForProcessing, lastDateOfDocsForProcessing)

    # filtered headers to processing
    usingHeaders = hFilter.get_filtered_headers(decisionsHeaders)

    clLinks = link_handler.parse(usingHeaders, decisionsHeaders,
                                 SUPERTYPES_TO_PARSE)
    jsonLinks = \
        converters.convert_dict_list_cls_to_json_serializable_format(clLinks)

    if MY_DEBUG:
        converters.save_pickle(clLinks, os.path.join(RESULTS_FOLDER_NAME,
                                                     'сleanLinks.pickle'))
        converters.save_json(jsonLinks, os.path.join(
            RESULTS_FOLDER_NAME, 'cleanLinks.json'))

    # got link graph
    linkGraph = link_handler.get_link_graph(clLinks)

    if MY_DEBUG:
        converters.save_pickle(linkGraph, PATH_TO_PICKLE_GRAPH)

    nFilter = models.GraphNodesFilter(
        nodesSupertypes,
        nodesTypes,
        firstDateForNodes, lastDateForNodes,
        nodesIndegreeRange, nodesOutdegreeRange)
    hFromFilter = models.HeadersFilter(
        supertypesFrom,
        docTypesFrom,
        firstDateFrom, lastDateFrom)
    hToFilter = models.HeadersFilter(
        supertypesTo,
        docTypesTo,
        firstDateTo, lastDateTo)
    eFilter = models.GraphEdgesFilter(hFromFilter, hToFilter, weightsRange)
    subgraph = linkGraph.get_subgraph(nFilter, eFilter, includeIsolatedNodes)

    if MY_DEBUG:
        converters.save_pickle(subgraph, PATH_TO_PICKLE_SUBGRAPH)

    linkGraphLists = (subgraph.get_nodes_as_IDs_list(),
                      subgraph.get_edges_as_list_of_tuples())

    converters.save_json(linkGraphLists, graphOutputFilePath)

    if showPicture:
        visualizer.visualize_link_graph(linkGraphLists, 20, 1, (40, 40))
    return jsonLinks

# end of ProcessPeriod--------------------------------------------------


def start_process_with(
        decisionID, depth,
        firstDateForNodes=None, lastDateForNodes=None,
        nodesIndegreeRange=None, nodesOutdegreeRange=None,
        nodesSupertypes=None, nodesTypes=None,
        includeIsolatedNodes=True,
        firstDateFrom=None, lastDateFrom=None, docTypesFrom=None,
        supertypesFrom=None,
        firstDateTo=None, lastDateTo=None, docTypesTo=None,
        supertypesTo=None,
        weightsRange=None,
        graphOutputFilePath=PATH_TO_JSON_GRAPH, showPicture=False,
        takeHeadersFromLocalStorage=False,
        sendRequestToUpdatingHeadersInBaseFromSite=False,
        whichSupertypeUpdateFromSite=None,
        visualizerParameters=(20, 1, (40, 40))):
    '''
    Start processing decisions from the decision which uid was given and repeat
    this behavior recursively for given depth.
    '''
    if (depth < 0):
        raise "argument error: depth of the recursion must be large than 0."

    if isinstance(firstDateForNodes, str):
        firstDateForNodes = dateutil.parser.parse(
            firstDateForNodes, dayfirst=True).date()
    if isinstance(lastDateForNodes, str):
        lastDateForNodes = dateutil.parser.parse(
            lastDateForNodes, dayfirst=True).date()
    if (firstDateForNodes is not None and
        lastDateForNodes is not None and
            firstDateForNodes > lastDateForNodes):
        raise ValueError(
            "Date error: The first date is later than the last date.")

    if isinstance(firstDateFrom, str):
        firstDateFrom = dateutil.parser.parse(
            firstDateFrom, dayfirst=True).date()
    if isinstance(lastDateFrom, str):
        lastDateFrom = dateutil.parser.parse(
            lastDateFrom, dayfirst=True).date()
    if (firstDateFrom is not None and
        lastDateFrom is not None and
            firstDateFrom > lastDateFrom):
        raise ValueError(
            "date error: The first date is later than the last date.")

    if isinstance(firstDateTo, str):
        firstDateTo = dateutil.parser.parse(
            firstDateTo, dayfirst=True).date()
    if isinstance(lastDateTo, str):
        lastDateTo = dateutil.parser.parse(
            lastDateTo, dayfirst=True).date()
    if (firstDateTo is not None and
        lastDateTo is not None and
            firstDateTo > lastDateTo):
        raise ValueError(
            "date error: The first date is later than the last date.")

    if takeHeadersFromLocalStorage:
        jsonHeaders = converters.load_json(PATH_TO_JSON_HEADERS)
    else:
        #TODO: using param 'whichSupertypeReloadFromSite' is not implemented
        print("Started to getting Headers from web_crawler.")
        jsonHeaders = wc_interface.get_all_headers(
            sendRequestToUpdatingHeadersInBaseFromSite,
            whichSupertypeUpdateFromSite)
        print("Finished getting Headers from web_crawler.")
        converters.save_json(jsonHeaders, PATH_TO_JSON_HEADERS)

    if jsonHeaders is None:
        raise ValueError(
            "Where's the document headers, Lebowski?")

    decisionsHeaders = \
        converters.convert_to_class_format(jsonHeaders, models.DocumentHeader)

    #Not using, just backup. Maybe delete later
    converters.save_pickle(decisionsHeaders, PATH_TO_PICKLE_HEADERS)

    if decisionID not in decisionsHeaders:
        raise ValueError("Unknown docID")

    toProcess = {decisionID: decisionsHeaders[decisionID]}
    processed = {}
    allLinks = {decisionsHeaders[decisionID]: []}
    while depth > 0 and len(toProcess) > 0:
        depth -= 1
        cleanLinks = link_handler.parse(toProcess, decisionsHeaders,
                                        SUPERTYPES_TO_PARSE)
        allLinks.update(cleanLinks)
        processed.update(toProcess)
        toProcess = {}
        for decID in cleanLinks:
            for cl in cleanLinks[decID]:
                docID = cl.header_to.doc_id
                if (docID not in processed):
                    toProcess[docID] = decisionsHeaders[docID]

    linkGraph = link_handler.get_link_graph(allLinks)
    jsonLinks = \
        converters.convert_dict_list_cls_to_json_serializable_format(allLinks)

    if MY_DEBUG:
        converters.save_pickle(allLinks, os.path.join(
            RESULTS_FOLDER_NAME, 'processedWithсleanLinks.pickle'))
        converters.save_json(jsonLinks, os.path.join(
            RESULTS_FOLDER_NAME, 'processedWithcleanLinks.json'))
        converters.save_pickle(linkGraph, os.path.join(
            RESULTS_FOLDER_NAME, 'processedlinkGraph.pickle'))

    nFilter = models.GraphNodesFilter(
        nodesSupertypes,
        nodesTypes,
        firstDateForNodes, lastDateForNodes,
        nodesIndegreeRange, nodesOutdegreeRange)
    hFromFilter = models.HeadersFilter(
        supertypesFrom,
        docTypesFrom,
        firstDateFrom, lastDateFrom)
    hToFilter = models.HeadersFilter(
        supertypesTo,
        docTypesTo,
        firstDateTo, lastDateTo)
    eFilter = models.GraphEdgesFilter(hFromFilter, hToFilter, weightsRange)
    subgraph = linkGraph.get_subgraph(nFilter, eFilter, includeIsolatedNodes)
    if MY_DEBUG:
        converters.save_pickle(subgraph, os.path.join(
            RESULTS_FOLDER_NAME, 'processWithSubgraph.pickle'))
    linkGraphLists = (subgraph.get_nodes_as_IDs_list(),
                      subgraph.get_edges_as_list_of_tuples())

    converters.save_json(linkGraphLists, graphOutputFilePath)
    if (showPicture):
        visualizer.visualize_link_graph(linkGraphLists,
                                        visualizerParameters[0],
                                        visualizerParameters[1],
                                        visualizerParameters[2])
# end of start_process_with---------------------------------------------


def get_all_links_from_all_headers(
        sendRequestToUpdatingHeadersInBaseFromSite=False,
        whichSupertypeUpdateFromSite=False):

    print("Started to getting Headers from web_crawler.")
    start_time = time.time()
    jsonHeaders = wc_interface.get_all_headers(
            sendRequestToUpdatingHeadersInBaseFromSite,
            whichSupertypeUpdateFromSite)
    print("Finished getting Headers from web_crawler. "
          f"It spent {time.time()-start_time} seconds.")

    if jsonHeaders is None:
        raise ValueError("Where's the document headers, Lebowski?")

    decisionsHeaders = converters.convert_to_class_format(
        jsonHeaders, models.DocumentHeader)

    clLinks = link_handler.parse(decisionsHeaders, decisionsHeaders,
                                 SUPERTYPES_TO_PARSE)
    jsonLinks = \
        converters.convert_dict_list_cls_to_json_serializable_format(clLinks)

    return jsonLinks


def get_CODE_links_from_all_headers(
        sendRequestToUpdatingHeadersInBaseFromSite=False,
        whichSupertypeUpdateFromSite=False):

    print("Started to getting Headers from web_crawler.")
    start_time = time.time()
    jsonHeaders = wc_interface.get_all_headers(
            sendRequestToUpdatingHeadersInBaseFromSite,
            whichSupertypeUpdateFromSite)
    print("Finished getting Headers from web_crawler. "
          f"It spent {time.time()-start_time} seconds.")

    if jsonHeaders is None:
        raise ValueError("Where's the document headers, Lebowski?")

    decisionsHeaders = converters.convert_to_class_format(
        jsonHeaders, models.DocumentHeader)

    clLinks = link_handler.parse(decisionsHeaders, decisionsHeaders,
                                 {'ГКРФ', 'НКРФ', 'КОАПРФ', 'УКРФ'})
    jsonLinks = \
        converters.convert_dict_list_cls_to_json_serializable_format(clLinks)

    return jsonLinks

if __name__ == "__main__":
    start_time = time.time()
    # process_period("18.06.1980", "18.07.2020", showPicture=False,
    #                sendRequestToUpdatingHeadersInBaseFromSite=False,
    #                includeIsolatedNodes=True,
    #                takeHeadersFromLocalStorage=True)
    # process_period("18.06.1980", "18.07.2020", showPicture=False,
    #                sendRequestToUpdatingHeadersInBaseFromSite=False,
    #                includeIsolatedNodes=True,
    # takeHeadersFromLocalStorage=True)
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
    #     showPicture=True, sendRequestToUpdatingHeadersInBaseFromSite=False,
    #     takeHeadersFromLocalStorage=True)

    # start_process_with(decisionID='КСРФ/1-П/2015', depth=3)

    # load_and_visualize()

    # start_process_with(
    #     decisionID='КСРФ/1-П/2015', depth=10,
    #     firstDateForNodes='18.03.2014', lastDateForNodes='14.08.2018',
    #     nodesIndegreeRange=(0, 25), nodesOutdegreeRange=(0, 25),
    #     nodesTypes={'КСРФ/О', 'КСРФ/П'},
    #     includeIsolatedNodes=False,
    #     firstDateFrom='18.03.2011', lastDateFrom='14.08.2019',
    #     docTypesFrom={'КСРФ/О', 'КСРФ/П'},
    #     firstDateTo='18.03.2011', lastDateTo='14.08.2018',
    #     docTypesTo={'КСРФ/О', 'КСРФ/П'},
    #     weightsRange=(1, 5),
    #     graphOutputFilePath=PATH_TO_JSON_GRAPH,
    #     showPicture=True, sendRequestToUpdatingHeadersInBaseFromSite=False,
    #     takeHeadersFromLocalStorage=True)

    # source = web_crawler.Crawler.get_data_source('LocalFileStorage')
    # text=source.get_data('КСРФ/19-П/2014',
    #                       web_crawler.DataType.DOCUMENT_TEXT)
    # text = wc_interface.get_text('КСРФ/1010-О-О/2008')
    # process_period("01.09.2018", "18.07.2019", showPicture=True,
    #                sendRequestToUpdatingHeadersInBaseFromSite=False,
    #                includeIsolatedNodes=True,
    #                takeHeadersFromLocalStorage=False)
    # process_period("12.04.2018", "12.04.2018", showPicture=True,
    #                sendRequestToUpdatingHeadersInBaseFromSite=False,
    #                includeIsolatedNodes=True,
    #                takeHeadersFromLocalStorage=False)
    # cl1 = converters.load_pickle("Results0\сleanLinks.pickle")
    # cl2 = converters.load_pickle("Results\сleanLinks.pickle")
    # import my_funs
    # my_funs.compare_clealinks(cl1, cl2)
    # print(f"Headers collection spent {time.time()-start_time} seconds.")

    # process_period(
    #     nodesIndegreeRange=(0, 25), nodesOutdegreeRange=(0, 25),
    #     graphOutputFilePath=PATH_TO_JSON_GRAPH,
    #     showPicture=False, sendRequestToUpdatingHeadersInBaseFromSite=False,
    #     takeHeadersFromLocalStorage=True)

    # response = get_all_links_from_all_headers()
    # converters.save_json(response, 'cleanLinks.json')
    # print(f"\nFound links: {len(response)}. "
    #       f"Time: {time.time()-start_time} seconds.")
    response = get_CODE_links_from_all_headers()
    print(f"\nFound links: {len(response)}. "
          f"Time: {time.time()-start_time} seconds.")
    converters.save_json(response, r'ГКРФ_НКРФ_КоАП_УК_cleaLinks.json')
    input('press any key...')
