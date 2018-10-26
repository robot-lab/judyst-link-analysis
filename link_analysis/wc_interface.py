from web_crawler import Crawler, DataType

isInitialized = False
FOLDER_FOR_HEADERS_AND_TEXTS = 'Decision files'
KSRFSOURCE = 'KSRFSource'
DATABASESOURCE = 'LocalFileStorage'



def init(folderName):
    # tests
    global isInitialized
    if isInitialized:
        return
    print("web_crawler sources initialization was started, it may take some time if headers is not downloaded.")
    Crawler.collected_sources[DATABASESOURCE].folder_path = folderName
    Crawler.prepare_sources([DATABASESOURCE, KSRFSOURCE])
    print("web_crawler sources initialization is finished.")
    isInitialized = True

init(FOLDER_FOR_HEADERS_AND_TEXTS)

def get_all_headers(sendRequestToUpdatingHeadersInBaseFromSite=False, whichSupertypeUpdateFromSite=None):
    '''
    Get all headers which has given supertype.
    '''
    headers = Crawler.get_data_source(KSRFSOURCE).\
        get_all_data(DataType.DOCUMENT_HEADER, whichSupertypeUpdateFromSite)   #TODO: using param 'whichSupertypeUpdateFromSite' not implemented
    return headers


def get_text(uid):
    text = Crawler.get_data_source(DATABASESOURCE).\
        get_data(uid, DataType.DOCUMENT_TEXT)
    return text


if __name__ == '__main__':
    print('hi')
    init('D:\\programming\\Judyst\\files')
    print(get_all_headers())
    print(get_text('КСРФ/35-П/2018'))
