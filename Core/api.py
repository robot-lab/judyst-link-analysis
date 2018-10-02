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
decitionsFolderName = "Decition files"
headersFileName = path.join(decitionsFolderName, 'DecitionHeaders.json')

def CollectHeaders():
    headers = law.GetResolutionHeaders(countOfPage=100)
    decitionsHeadersFile = open(headersFileName, 'w')
    decitionsHeadersFile.write(json.dumps(headers))
    decitionsHeadersFile.close()
    return headers



def LoadHeaders():
    headersFile = open(headersFileName, 'r')
    text = headersFile.read()
    headersFile.close()
    return json.loads(text)







#api methods-------------------------------------------------------------------


def ProcessPeriod(firstDate, lastDate,
 graphOutFileName='graph.json', showPicture=True, isNeedReloadHeaders=False):
    '''
    Process decitions from the date specified as firstDate to
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

   
    decitionsHeaders = {}
    if (isNeedReloadHeaders or not path.exists(headersFileName)):
       decitionsHeaders = CollectHeaders()
    else:
        decitionsHeaders = LoadHeaders()
    
    usingHeaders = {}
    for key in decitionsHeaders:
        currDecitionDate = parser.parse(decitionsHeaders[key]['date']).date()
        if (currDecitionDate > firstDate and currDecitionDate < lastDate):
            usingHeaders[key] = decitionsHeaders[key] 

    

    for key in usingHeaders:
        if (not path.exists(usingHeaders[key]['url'])):
            law.LoadResolutionTexts({key: usingHeaders[key]})
    
    
    rudeLinksDict = FirstAnalysis.GetRudeLinksForMultipleDocuments(usingHeaders)
    
    #tmp1 = FirstAnalysis.GetRudeLinks(decitions['35-П/2018']['url'])
    #tmp2 = FinalAnalysis.GetCleanLinks({'35-П/2018' : tmp1}, decitions)

    commonGraph  = ([], [])

    for key in rudeLinksDict:        
        links, errLinks = FinalAnalysis.GetCleanLinks(
         {key : rudeLinksDict[key]}, decitionsHeaders)        

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
    visualizer.VisualizeLinkGraph(commonGraph)
#end of ProcessPeriod----------------------------------------------------------


def StartProcessWith(uid, depth):
    '''
    Start processing decitions from the decition which uid was given and repeat
    this behavior recursively for given depth.
    '''
    if (depth < 0):
        raise "argument error: depth of the recursion must be large than 0."


if __name__ == "__main__":
    ProcessPeriod("01.01.2018", "31.12.2018")
    #print(CollectHeaders()   )


