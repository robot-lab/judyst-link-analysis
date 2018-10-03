# coding=utf-8
# Coded by Aleksandr Rodionov
# rexarrior@yandex.ru





# imports Core modules---------------------------------------------------------
import FinalAnalysis
import FirstAnalysis
import law
import visualizer


#other imports-----------------------------------------------------------------
import json
from datetime import date
from dateutil import parser
from os import path as path

#methods-----------------------------------------------------------------------



#internal methods--------------------------------------------------------------
decisionsFolderName = "Decision files"
headersFileName = path.join(decisionsFolderName, 'DecisionHeaders.json')


def SaveHeaders(headers):
    decisionsHeadersFile = open(headersFileName, 'w')
    decisionsHeadersFile.write(json.dumps(headers))
    decisionsHeadersFile.close()
    


def CollectHeaders():
    headers = law.GetResolutionHeaders(countOfPage=1569)
    SaveHeaders(headers)
    return headers



def LoadHeaders():
    headersFile = open(headersFileName, 'r')
    text = headersFile.read()
    headersFile.close()
    return json.loads(text)



def CheckFilesForHeaders(headers):
    for uid in headers:
        filename = law.GetdecisionFileNameByUid(uid, decisionsFolderName, ext='txt')
        if (path.exists(filename)):
            headers[uid]['url'] = filename



def LoadGraph(file_name):
    graphfile = open(file_name)
    graph = json.loads(graphfile.read())
    graphfile.close()
    return graph


def LoadAndVisualize(filename = 'graph.json'):
    graph = LoadGraph(filename)
    visualizer.VisualizeLinkGraph(graph, 20, 1, (20,20))


#api methods-------------------------------------------------------------------


def ProcessPeriod(firstDate, lastDate,
 graphOutFileName='graph.json', showPicture=True, isNeedReloadHeaders=False):
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
        decisionsHeaders = CollectHeaders()
    else:
        decisionsHeaders = LoadHeaders()
    
    usingHeaders = {}
    for key in decisionsHeaders:
        currdecisionDate = parser.parse(decisionsHeaders[key]['date']).date()
        if (currdecisionDate >= firstDate and currdecisionDate <= lastDate):
            usingHeaders[key] = decisionsHeaders[key] 
    CheckFilesForHeaders(usingHeaders)

    

    for key in usingHeaders:
        if (not path.exists(usingHeaders[key]['url'])):
            law.LoadResolutionTexts({key: usingHeaders[key]}, decisionsFolderName)

    decisionsHeaders.update(usingHeaders)
    
    SaveHeaders(decisionsHeaders)
    
    rudeLinksDict = FirstAnalysis.GetRudeLinksForMultipleDocuments(usingHeaders)
    
    #tmp1 = FirstAnalysis.GetRudeLinks(decisions['35-П/2018']['url'])
    #tmp2 = FinalAnalysis.GetCleanLinks({'35-П/2018' : tmp1}, decisions)

    commonGraph  = ([], [])

    for key in rudeLinksDict:        
        links, errLinks = FinalAnalysis.GetCleanLinks(
         {key : rudeLinksDict[key]}, decisionsHeaders)        

        graph = FinalAnalysis.GetLinkGraph(links)
        for node in graph[0]:
            if node in commonGraph[0]:
                continue
            commonGraph[0].append(node)
        for edge in graph[1]:
            commonGraph[1].append(edge)


    graphFile = open(graphOutFileName, 'w', encoding='utf-8')
    graphFile.write(json.dumps(commonGraph))
    graphFile.close()
    visualizer.VisualizeLinkGraph(commonGraph, 20, 1, (40,40))
#end of ProcessPeriod----------------------------------------------------------







def StartProcessWith(uid, depth):
    '''
    Start processing decisions from the decision which uid was given and repeat
    this behavior recursively for given depth.
    '''
    if (depth < 0):
        raise "argument error: depth of the recursion must be large than 0."


if __name__ == "__main__":
   # ProcessPeriod("01.07.2018", "30.12.2018")
    ProcessPeriod("17.07.2018", "17.07.2018")
  #  LoadAndVisualize()
    #CollectHeaders()
