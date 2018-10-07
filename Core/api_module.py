# coding=utf-8
# Coded by Aleksandr Rodionov
# rexarrior@yandex.ru


# imports Core modules--------------------------------------------------
import final_analysis
import rough_analysis
import web_crawler
import visualizer


# other imports---------------------------------------------------------
import json
from datetime import date
from dateutil import parser
import os.path
# methods---------------------------------------------------------------


# internal methods------------------------------------------------------
decisionsFolderName = "Decision files"
headersFileName = os.path.join(decisionsFolderName, 'DecisionHeaders.json')


def save_headers(headers, filename):
    '''
    Pack the heareds with json and store it to file of the filename
    '''
    if not os.path.exists(os.path.dirname(filename)):
        os.mkdir(os.path.dirname(filename))
    decisionsHeadersFile = open(filename, 'w')
    decisionsHeadersFile.write(json.dumps(headers))
    decisionsHeadersFile.close()


def collect_headers(headersfilename, countOfPage=1570):
    headers = web_crawler.get_resolution_headers(countOfPage)
    save_headers(headers, headersFileName)
    return headers


def load_headers(filename):
    '''
    Load the stored earlier headers of the documents,
    unpack it with json and return as
    {uid:{'date':'date', title:'title', url:'web uri or filename'}}

    '''
    headersFile = open(filename, 'r')
    text = headersFile.read()
    headersFile.close()
    return json.loads(text)


def check_files_for_headers(headers, folder):
    '''
    Find files of the documents of the given headers
    and replace the header 'url':'web uri' by 'url':'filename' when
    the file have finded.
    '''
    for uid in headers:
        filename = web_crawler.get_decision_filename_by_uid(uid, folder,
                                                            ext='txt')
        if (os.path.exists(filename)):
            headers[uid]['path to text file'] = filename


def load_files_for_headers(headers, folder):
    for key in headers:
        if 'path to text file' not in headers[key] \
                or not os.path.exists(headers[key]['path to text file']):
            web_crawler.load_resolution_texts({key: headers[key]}, folder)


def load_graph(file_name):
    '''
    Load the stored earlier graph from the given filename,
    unpack it with JSON and return as
    [[nodes], [edges: [from, to]]
    '''
    graphfile = open(file_name)
    graph = json.loads(graphfile.read())
    graphfile.close()
    return graph


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
    for key in headers:
        if 'not unique' in headers[key]:
            continue
        currdecisionDate = parser.parse(headers[key]['date']).date()
        if (currdecisionDate >= firstDate and currdecisionDate <= lastDate):
            usingHeaders[key] = headers[key]
    return usingHeaders

# api methods-----------------------------------------------------------


def process_period(firstDate, lastDate, graphOutFileName='graph.json',
                   showPicture=True, isNeedReloadHeaders=False):
    '''
    Process decisions from the date specified as firstDate to
    the date specified as lastDate.
    Write a graph of result of the processing and, if it was specified,
    draw graph and show it to user.
    '''

    if not(firstDate is date):
        firstDate = parser.parse(firstDate).date()

    if not(lastDate is date):
        lastDate = parser.parse(lastDate).date()

    if (firstDate > lastDate):
        raise "date error: The first date is later than the last date. "

    decisionsHeaders = {}
    if (isNeedReloadHeaders or not os.path.exists(headersFileName)):
        decisionsHeaders = collect_headers(headersFileName)
    else:
        decisionsHeaders = load_headers(headersFileName)

    usingHeaders = get_headers_between_dates(decisionsHeaders, firstDate,
                                             lastDate)

    check_files_for_headers(usingHeaders, decisionsFolderName)

    load_files_for_headers(usingHeaders, decisionsFolderName)

    decisionsHeaders.update(usingHeaders)

    save_headers(decisionsHeaders, headersFileName)

    rudeLinksDict = \
        rough_analysis.get_rude_links_for_multiple_docs(usingHeaders)

    links = final_analysis.get_clean_links(rudeLinksDict,
                                           decisionsHeaders)[0]

    commonGraph = final_analysis.get_link_graph(links)

    graphFile = open(graphOutFileName, 'w', encoding='utf-8')
    graphFile.write(json.dumps(commonGraph))
    graphFile.close()

    visualizer.visualize_link_graph(commonGraph, 20, 1, (40, 40))
# end of ProcessPeriod--------------------------------------------------


def start_process_with(uid, depth):
    '''
    Start processing decisions from the decision which uid was given and repeat
    this behavior recursively for given depth.
    '''
    if (depth < 0):
        raise "argument error: depth of the recursion must be large than 0."


if __name__ == "__main__":
    import time
    # ProcessPeriod("01.07.2018", "30.12.2018")
    # ProcessPeriod("17.07.2018", "17.07.2018", isNeedReloadHeaders=False)
    # LoadAndVisualize()
    # CollectHeaders()
    start_time = time.time()
    process_period("18.07.2018", "18.07.2018", showPicture=False,
                   isNeedReloadHeaders=False)
    print("--- {0} seconds ---".format(time.time() - start_time))
