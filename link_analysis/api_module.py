# coding=utf-8
# Coded by Aleksandr Rodionov
# rexarrior@yandex.ru


# imports Core modules--------------------------------------------------
import link_analysis.final_analysis as final_analysis
import link_analysis.rough_analysis as rough_analysis
import link_analysis.visualizer as visualizer
import web_crawler.ksrf as web_crawler
from link_analysis.models import Header, HeadersFilter

# other imports---------------------------------------------------------
import os.path
import json
import pickle
from datetime import date

from dateutil import parser
# License: Apache Software License, BSD License (Dual License)

# methods---------------------------------------------------------------


# internal methods------------------------------------------------------
DECISIONS_FOLDER_NAME = "Decision files"
HEADERS_FILE_NAME = os.path.join(DECISIONS_FOLDER_NAME,
                                 'DecisionHeaders.pickle')


def save_headers(headers, filename):
    '''
    Pack the headers with pickle and store it to file of the filename
    '''
    if not os.path.exists(os.path.dirname(filename)):
        os.mkdir(os.path.dirname(filename))
    with open(filename, 'wb') as decisionsHeadersFile:
        pickle.dump(headers, decisionsHeadersFile)


# TO DO: remake format returning by web_crawler
def collect_headers(HEADERS_FILE_NAME, countOfPage=3):
    headers = web_crawler.get_resolution_headers(countOfPage)
    save_headers(headers, HEADERS_FILE_NAME)
    return headers


def load_headers(filename):
    '''
    Load the stored earlier headers of the documents,
    unpack it with pickle and return as
    {uid: class Header, uid: class DuplicateHeader, ...}

    '''
    with open(filename, 'rb') as decisionsHeadersFile:
        headersDict = pickle.load(decisionsHeadersFile, encoding='UTF-8')
    return headersDict


def check_files_for_headers(headers, folder):
    '''
    Find files of the documents of the given headers
    and add path to file in Header.text_location if file was found
    '''
    for uid in headers:
        filename = web_crawler.get_decision_filename_by_uid(uid, folder,
                                                            ext='txt')
        if (os.path.exists(filename)):
            headers[uid].text_location = filename


def load_files_for_headers(headers, folder):
    for key in headers:
        if (isinstance(headers[key], Header) and
            (headers[key].text_location is None or
                not os.path.exists(headers[key].text_location))):

            # TO DO: remake loading by web_crawler
            web_crawler.load_resolution_texts({key: headers[key]}, folder)


# TO DO: Rewrite function after rewriting final_analysis module
def load_graph(file_name):
    '''
    Load the stored earlier graph from the given filename,
    unpack it with JSON and return as
    [[nodes], [edges: [from, to, weight]]
    '''
    graphfile = open(file_name)
    graph = json.loads(graphfile.read())
    graphfile.close()
    return graph


# TO DO: Rewrite function after rewriting final_analysis module
def load_and_visualize(filename='graph.json'):
    '''
    Load the stored earlier graph from the given filename and
    Visualize it with Visualizer module.
    '''
    graph = load_graph(filename)
    visualizer.visualize_link_graph(graph, 20, 1, (20, 20))


def get_headers_between_dates(headers, firstDate, lastDate):
    '''
    Do a selection from the headers for that whisch was publicated later,
    than the first date,
    And earlier than the last date.
    '''
    usingHeaders = {}
    hFilter = HeadersFilter(firstDate=firstDate, lastDate=lastDate)
    for key in headers:
        if (isinstance(headers[key], Header) and
                hFilter.check_header(headers[key])):
            usingHeaders[key] = headers[key]
    return usingHeaders

# api methods-----------------------------------------------------------


# TO DO: Rewrite all functions below this line.
def process_period(firstDate, lastDate, graphOutFileName='graph.json',
                   showPicture=True, isNeedReloadHeaders=False):
    '''
    Process decisions from the date specified as firstDate to
    the date specified as lastDate.
    Write a graph of result of the processing and, if it was specified,
    draw graph and show it to user.
    '''

    if not isinstance(firstDate, date):
        firstDate = parser.parse(firstDate, dayfirst=True).date()

    if not isinstance(lastDate, date):
        lastDate = parser.parse(lastDate, dayfirst=True).date()

    if (firstDate > lastDate):
        raise "date error: The first date is later than the last date. "

    decisionsHeaders = {}
    if (isNeedReloadHeaders or not os.path.exists(HEADERS_FILE_NAME)):
        decisionsHeaders = collect_headers(HEADERS_FILE_NAME)
    else:
        decisionsHeaders = load_headers(HEADERS_FILE_NAME)

    usingHeaders = get_headers_between_dates(decisionsHeaders, firstDate,
                                             lastDate)

    check_files_for_headers(usingHeaders, DECISIONS_FOLDER_NAME)

    load_files_for_headers(usingHeaders, DECISIONS_FOLDER_NAME)

    decisionsHeaders.update(usingHeaders)

    save_headers(decisionsHeaders, HEADERS_FILE_NAME)

    roughLinksDict = \
        rough_analysis.get_rough_links_for_multiple_docs(usingHeaders)

    # CONTINUE FROM THIS
    links = final_analysis.get_clean_links(roughLinksDict,
                                           decisionsHeaders)[0]

    commonGraph = final_analysis.get_link_graph(links)

    graphFile = open(graphOutFileName, 'w', encoding='utf-8')
    graphFile.write(json.dumps(commonGraph))
    graphFile.close()
    if showPicture:
        visualizer.visualize_link_graph(commonGraph, 20, 1, (40, 40))
# end of ProcessPeriod--------------------------------------------------


def start_process_with(uid, depth, headers=None,
                       graphOutFileName='graph.json',
                       isShowPicture=True, isNeedReloadHeaders=False,
                       visualizerParameters=(20, 1, (40, 40))):
    '''
    Start processing decisions from the decision which uid was given and repeat
    this behavior recursively for given depth.
    '''
    if (depth < 0):
        raise "argument error: depth of the recursion must be large than 0."

    if (isNeedReloadHeaders or
       (not os.path.exists(HEADERS_FILE_NAME) and headers is None)):
        headers = collect_headers(HEADERS_FILE_NAME)
    else:
        headers = load_headers(HEADERS_FILE_NAME)
    if (uid not in headers):
        raise "Unknown uid"
    check_files_for_headers(headers, DECISIONS_FOLDER_NAME)
    load_files_for_headers(headers, DECISIONS_FOLDER_NAME)

    toProcess = {uid: headers[uid]}
    processed = {}
    allLinks = {uid: []}
    while depth > 0 and len(toProcess) > 0:
        depth -= 1
        rude = rough_analysis.get_rough_links_for_multiple_docs(toProcess)
        clean = final_analysis.get_clean_links(rude, headers)[0]
        allLinks.update(clean)
        processed.update(toProcess)
        toProcess = {}
        for uid in clean:
            for uid2 in clean[uid]:
                if (uid2 not in processed):
                    toProcess[uid2] = headers[uid2]
    graph = final_analysis.get_link_graph(allLinks)
    graphFile = open(graphOutFileName, 'w')
    graphFile.write(json.dumps(graph))
    graphFile.close()
    if (isShowPicture):
        visualizer.visualize_link_graph(graph,
                                        visualizerParameters[0],
                                        visualizerParameters[1],
                                        visualizerParameters[2])
# end of start_process_with---------------------------------------------

if __name__ == "__main__":
    process_period("18.06.1980", "18.07.2020", showPicture=False,
                   isNeedReloadHeaders=False)
