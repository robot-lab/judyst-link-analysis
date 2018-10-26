# coding=utf-8
# Coded by Aleksandr Rodionov
# rexarrior@yandex.ru


# other imports---------------------------------------------------------
import os.path
import datetime

import dateutil.parser
# License: Apache Software License, BSD License (Dual License)

# imports Core modules--------------------------------------------------
import final_analysis
import models
import rough_analysis
import visualizer
import converters
import wc_interface
# methods---------------------------------------------------------------


# internal methods------------------------------------------------------
DECISIONS_FOLDER_NAME = 'Decision files'
JSON_HEADERS_FILENAME = 'DecisionHeaders.json'
PICKLE_HEADERS_FILENAME = 'DecisionHeaders.pickle'
PATH_TO_JSON_HEADERS = os.path.join(DECISIONS_FOLDER_NAME,
                                    JSON_HEADERS_FILENAME)
PATH_TO_PICKLE_HEADERS = os.path.join(DECISIONS_FOLDER_NAME,
                                      PICKLE_HEADERS_FILENAME)
RESULTS_FOLDER_NAME = 'ResultsTrue'                                    
PICKLE_GRAPH_FILENAME = 'graph.pickle'
JSON_GRAPH_FILENAME = 'graph.json'
PATH_TO_PICKLE_GRAPH = os.path.join(RESULTS_FOLDER_NAME, PICKLE_GRAPH_FILENAME)
PATH_TO_JSON_GRAPH = os.path.join(RESULTS_FOLDER_NAME, JSON_GRAPH_FILENAME)
PICKLE_SUBGRAPH_FILENAME = 'subgraph.pickle'
JSON_SUBGRAPH_FILENAME = 'subgraph.json'
PATH_TO_PICKLE_SUBGRAPH = os.path.join(RESULTS_FOLDER_NAME, PICKLE_SUBGRAPH_FILENAME)
PATH_TO_JSON_SUBGRAPH = os.path.join(RESULTS_FOLDER_NAME, JSON_SUBGRAPH_FILENAME)

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
        nodesIndegreeRange=None, nodesOutdegreeRange=None, nodesTypes=None,
        includeIsolatedNodes=True,
        firstDateFrom=None, lastDateFrom=None, docTypesFrom=None,
        supertypesFrom=None,
        firstDateTo=None, lastDateTo=None, docTypesTo=None,
        supertypesTo=None,
        weightsRange=None,
        graphOutputFilePath=PATH_TO_JSON_GRAPH,
        showPicture=True, takeHeadersFromLocalStorage=True, sendRequestToUpdatingHeadersInBaseFromSite=False, whichSupertypeUpdateFromSite=None):
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
        raise ValueError("date error: The first date is later than the last date.")

    if isinstance(firstDateTo, str):
        firstDateTo = dateutil.parser.parse(
            firstDateTo, dayfirst=True).date()
    if isinstance(lastDateTo, str):
        lastDateTo = dateutil.parser.parse(
            lastDateTo, dayfirst=True).date()
    if (firstDateTo is not None and
        lastDateTo is not None and
            firstDateTo > lastDateTo):
        raise ValueError("date error: The first date is later than the last date.")

    if takeHeadersFromLocalStorage:
        jsonHeaders = converters.load_json(PATH_TO_JSON_HEADERS)
    else:
        jsonHeaders = wc_interface.get_all_headers(sendRequestToUpdatingHeadersInBaseFromSite, whichSupertypeUpdateFromSite)  #TODO: using param 'whichSupertypeReloadFromSite' is not implemented
        #TODO: load and save same file from folder, commented while have no database
        #converters.save_json(jsonHeaders, PATH_TO_JSON_HEADERS)
   
    if not jsonHeaders:
        raise ValueError("Where's the document headers, Lebowski?")

    decisionsHeaders = converters.convert_to_class_format(jsonHeaders, models.DocumentHeader)
    converters.save_pickle(decisionsHeaders, PATH_TO_PICKLE_HEADERS)  #Not using, just backup. Maybe delete later

    hFilter = models.HeadersFilter(
        supertypesForProcessing,
        docTypesForProcessing,
        firstDateOfDocsForProcessing, lastDateOfDocsForProcessing)
    
    # filtered headers to processing
    usingHeaders = hFilter.get_filtered_headers(decisionsHeaders)

    roughLinksDict = \
        rough_analysis.get_rough_links_for_docs(usingHeaders)
    
    response = final_analysis.get_clean_links(roughLinksDict,
                                           decisionsHeaders)
    links, rejectedLinks = response[0], response[1]

    if MY_DEBUG:
        converters.save_pickle(links, os.path.join(RESULTS_FOLDER_NAME, 'сleanLinks.pickle'))
        converters.save_pickle(rejectedLinks, os.path.join(RESULTS_FOLDER_NAME, 'rejectedLinks.pickle'))
        jsonLinks = converters.convert_dict_list_cls_to_json_serializable_format(links)
        converters.save_json(jsonLinks, os.path.join(RESULTS_FOLDER_NAME, 'cleanLinks.json'))

    # got link graph
    linkGraph = final_analysis.get_link_graph(links)
    hash(linkGraph) #TODO: Delete
    
    
    if MY_DEBUG:
        converters.save_pickle(linkGraph, PATH_TO_PICKLE_GRAPH)

    nFilter = models.GraphNodesFilter(
        nodesTypes, firstDateForNodes, lastDateForNodes, nodesIndegreeRange,
        nodesOutdegreeRange)
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
        nodesIndegreeRange=None, nodesOutdegreeRange=None, nodesTypes=None,
        includeIsolatedNodes=True,
        firstDateFrom=None, lastDateFrom=None, docTypesFrom=None,
        supertypesFrom=None,
        firstDateTo=None, lastDateTo=None, docTypesTo=None,
        supertypesTo=None,
        weightsRange=None,
        graphOutputFilePath=PATH_TO_JSON_GRAPH,
        showPicture=True, takeHeadersFromLocalStorage=True, sendRequestToUpdatingHeadersInBaseFromSite=False, whichSupertypeUpdateFromSite=None,
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
        raise ValueError("date error: The first date is later than the last date.")

    if isinstance(firstDateFrom, str):
        firstDateFrom = dateutil.parser.parse(
            firstDateFrom, dayfirst=True).date()
    if isinstance(lastDateFrom, str):
        lastDateFrom = dateutil.parser.parse(
            lastDateFrom, dayfirst=True).date()
    if (firstDateFrom is not None and
        lastDateFrom is not None and
            firstDateFrom > lastDateFrom):
        raise ValueError("date error: The first date is later than the last date.")

    if isinstance(firstDateTo, str):
        firstDateTo = dateutil.parser.parse(
            firstDateTo, dayfirst=True).date()
    if isinstance(lastDateTo, str):
        lastDateTo = dateutil.parser.parse(
            lastDateTo, dayfirst=True).date()
    if (firstDateTo is not None and
        lastDateTo is not None and
            firstDateTo > lastDateTo):
        raise ValueError("date error: The first date is later than the last date.")
    
    if takeHeadersFromLocalStorage:
        jsonHeaders = converters.load_json(PATH_TO_JSON_HEADERS)
    else:
        jsonHeaders = wc_interface.get_all_headers(sendRequestToUpdatingHeadersInBaseFromSite, whichSupertypeUpdateFromSite)  #TODO: using param 'whichSupertypeReloadFromSite' is not implemented
        #TODO: load and save same file from folder, commented while have no database
        #converters.save_json(jsonHeaders, PATH_TO_JSON_HEADERS)
   
    if not jsonHeaders:
        raise ValueError("Where's the document headers, Lebowski?")



    decisionsHeaders = converters.convert_to_class_format(jsonHeaders, models.DocumentHeader)
    converters.save_pickle(decisionsHeaders, PATH_TO_PICKLE_HEADERS)  #Not using, just backup. Maybe delete later
     
    if (decisionID not in decisionsHeaders):
        raise ValueError("Unknown docID")

    toProcess = {decisionID: decisionsHeaders[decisionID]}
    processed = {}
    allLinks = {decisionsHeaders[decisionID]: []}
    while depth > 0 and len(toProcess) > 0:
        depth -= 1
        roughLinksDict = rough_analysis.get_rough_links_for_docs(
            toProcess)
        cleanLinks = final_analysis.get_clean_links(roughLinksDict, decisionsHeaders)[0]
        allLinks.update(cleanLinks)
        processed.update(toProcess)
        toProcess = {}
        for decID in cleanLinks:
            for cl in cleanLinks[decID]:
                docID = cl.header_to.doc_id
                if (docID not in processed):
                    toProcess[docID] = decisionsHeaders[docID]

    linkGraph = final_analysis.get_link_graph(allLinks)
    if MY_DEBUG:
        converters.save_pickle(allLinks, os.path.join(RESULTS_FOLDER_NAME, 'processedWithсleanLinks.pickle'))
        jsonLinks = converters.convert_dict_list_cls_to_json_serializable_format(allLinks)
        converters.save_json(jsonLinks, os.path.join(RESULTS_FOLDER_NAME, 'processedWithcleanLinks.json'))
        converters.save_pickle(linkGraph, os.path.join(RESULTS_FOLDER_NAME, 'processedlinkGraph.pickle'))

    nFilter = models.GraphNodesFilter(
        nodesTypes, firstDateForNodes, lastDateForNodes, nodesIndegreeRange,
        nodesOutdegreeRange)
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
    #                sendRequestToUpdatingHeadersInBaseFromSite=False, includeIsolatedNodes=True, takeHeadersFromLocalStorage=True)
    # process_period("18.06.1980", "18.07.2020", showPicture=False,
    #                sendRequestToUpdatingHeadersInBaseFromSite=False, includeIsolatedNodes=True, takeHeadersFromLocalStorage=True)
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
    #     showPicture=True, sendRequestToUpdatingHeadersInBaseFromSite=False, includeIsolatedNodes=True, takeHeadersFromLocalStorage=True)
    
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
    #     showPicture=True, sendRequestToUpdatingHeadersInBaseFromSite=False, includeIsolatedNodes=True, takeHeadersFromLocalStorage=True)

    # source = web_crawler.Crawler.get_data_source('LocalFileStorage')
    # text=source.get_data('КСРФ/19-П/2014', web_crawler.DataType.DOCUMENT_TEXT)
    # text = wc_interface.get_text('КСРФ/1010-О-О/2008')
    process_period("01.09.1985", "18.07.2020", showPicture=True,
                   sendRequestToUpdatingHeadersInBaseFromSite=False, includeIsolatedNodes=True, takeHeadersFromLocalStorage=True)
    print(f"Headers collection spent {time.time()-start_time} seconds.")
    input('press any key...')