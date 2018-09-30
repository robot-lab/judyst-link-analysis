# Coded by Aleksandr Rodionov
# rexarrior@yandex.ru





# imports Core modules---------------------------------------------------------
import FinalAnalysis
import FirstAnalysis
#import law
import visualizer


#other imports-----------------------------------------------------------------
import json
from datetime import date
from dateutil import parser


#methods-----------------------------------------------------------------------



#internal methods--------------------------------------------------------------




#api methods-------------------------------------------------------------------




def ProcessPeriod(firstDate, lastDate,
 graphOutFileName = 'graph.json', showPicture = True):
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
    


    links, errLinks = FinalAnalysis.GetCleanLinks(
         FinalAnalysis.collectedLinks,
         FinalAnalysis.courtSiteContent)

    graph = FinalAnalysis.GetLinkGraph(links)
    graphFile = open(graphOutFileName, 'w', encoding='utf-8')
    graphFile.write(json.dumps(graph))
    graphFile.close()
    visualizer.VisualizeLinkGraph(graph)
#end of ProcessPeriod----------------------------------------------------------


def StartProcessWith(uid, depth):
    '''
    Start processing decitions from the decition which uid was given and repeat
    this behavior recursively for given depth.
    '''
    if (depth < 0):
        raise "argument error: depth of the recursion must be large than 0."


if __name__ == "__main__":
    ProcessPeriod("01.01.2000", "10.01.2000")
        


