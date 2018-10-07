# coding=utf-8
# Coded by Aleksandr Rodionov
# rexarrior@yandex.ru


# imports Core modules--------------------------------------------------
import FinalAnalysis
import FirstAnalysis
import law
import visualizer


# other imports---------------------------------------------------------
import json
from datetime import date
from dateutil import parser
from os import path as path

# methods---------------------------------------------------------------


# internal methods------------------------------------------------------
decisionsFolderName = "Decision files"
headersFileName = path.join(decisionsFolderName, 'DecisionHeaders.json')


def SaveHeaders(headers, filename):
    '''
    Pack the heareds with json and store it to file of the filename
    '''
    decisionsHeadersFile = open(filename, 'w')
    decisionsHeadersFile.write(json.dumps(headers))
    decisionsHeadersFile.close()


def CollectHeaders(headersfilename, countOfPage=1569):
    headers = law.GetResolutionHeaders(countOfPage)
    SaveHeaders(headers, headersFileName)
    return headers


def LoadHeaders(filename):
    '''
    Load the stored earlier headers of the documents,
    unpack it with json and return as
    {uid:{'date':'date', title:'title', url:'web uri or filename'}}

    '''
    headersFile = open(filename, 'r')
    text = headersFile.read()
    headersFile.close()
    return json.loads(text)


def CheckFilesForHeaders(headers, folder):
    '''
    Find files of the documents of the given headers
    and replace the header 'url':'web uri' by 'url':'filename' when
    the file have finded.
    '''
    for uid in headers:
        filename = law.GetdecisionFileNameByUid(uid, folder, ext='txt')
        if (path.exists(filename)):
            headers[uid]['url'] = filename


def LoadFilesForHeaders(headers, folder):
    for key in headers:
        if (not path.exists(headers[key]['url'])):
            law.LoadResolutionTexts({key: headers[key]}, folder)


def LoadGraph(file_name):
    '''
    Load the stored earlier graph from the given filename,
    unpack it with JSON and return as
    [[nodes], [edges: [from, to]]
    '''
    graphfile = open(file_name)
    graph = json.loads(graphfile.read())
    graphfile.close()
    return graph


def LoadAndVisualize(filename='graph.json'):
    '''
    Load the stored earlier graph from the given filename and
    Visualize it with Visualizer module.
    '''
    graph = LoadGraph(filename)
    visualizer.VisualizeLinkGraph(graph, 20, 1, (20, 20))


def GetHeadersBetweenDates(headers, firstDate, lastDate):
    '''
    Do a selection from the headers for that whisch was publicated later,
    than the first date,
    And earlier than the last date.
    '''
    usingHeaders = {}
    for key in headers:
        currdecisionDate = parser.parse(headers[key]['date']).date()
        if (currdecisionDate >= firstDate and currdecisionDate <= lastDate):
            usingHeaders[key] = headers[key]
    return usingHeaders

# api methods-----------------------------------------------------------


def ProcessPeriod(firstDate, lastDate, graphOutFileName='graph.json',
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
    if (isNeedReloadHeaders or not path.exists(headersFileName)):
        decisionsHeaders = CollectHeaders(headersFileName)
    else:
        decisionsHeaders = LoadHeaders(headersFileName)

    usingHeaders = GetHeadersBetweenDates(decisionsHeaders, firstDate,
                                          lastDate)

    CheckFilesForHeaders(usingHeaders, decisionsFolderName)

    LoadFilesForHeaders(usingHeaders, decisionsFolderName)

    decisionsHeaders.update(usingHeaders)

    SaveHeaders(decisionsHeaders, headersFileName)

    rudeLinksDict = \
        FirstAnalysis.GetRudeLinksForMultipleDocuments(usingHeaders)
    (links, errLinks) = FinalAnalysis.GetCleanLinks(rudeLinksDict,
                                                    decisionsHeaders)
    commonGraph = FinalAnalysis.GetLinkGraph(links)

    graphFile = open(graphOutFileName, 'w', encoding='utf-8')
    graphFile.write(json.dumps(commonGraph))
    graphFile.close()

    visualizer.VisualizeLinkGraph(commonGraph, 20, 1, (40, 40))
# end of ProcessPeriod--------------------------------------------------


def StartProcessWith(uid, depth):
    '''
    Start processing decisions from the decision which uid was given and repeat
    this behavior recursively for given depth.
    '''
    if (depth < 0):
        raise "argument error: depth of the recursion must be large than 0."


if __name__ == "__main__":
    # ProcessPeriod("01.07.2018", "30.12.2018")
    # ProcessPeriod("17.07.2018", "17.07.2018", isNeedReloadHeaders=False)
    # LoadAndVisualize()
    # CollectHeaders()
    ProcessPeriod("18.07.2018", "23.07.2018", showPicture=False,
                  isNeedReloadHeaders=True)
