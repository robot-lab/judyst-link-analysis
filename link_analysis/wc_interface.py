from web_crawler import Crawler, DataType, Init as web_crawler_init

isInitialized = False
FOLDER_FOR_HEADERS_AND_TEXTS = 'Decision files'
KSRFSOURCE = 'KSRFSource'
LOCAL_DATABASE = 'LocalFileStorage'

database_source_name = None


def init(folderName='', databaseSource=None):
    # tests
    global isInitialized
    global database_source_name
    if isInitialized:
        return
    print("web_crawler sources initialization was started, it may take some\
           time if headers is not downloaded.")
    if  __package__:
        if (databaseSource is None):
            raise RuntimeError(' DatabaseSource should be given')
        database_source_name = databaseSource.source_name
        web_crawler_init([KSRFSOURCE], databaseSource)
    else:
        local_base = Crawler.collected_sources[LOCAL_DATABASE]        
        local_base.folder_path = folderName
        local_base.prepare()
        Crawler.prepare_sources([KSRFSOURCE],
                                databaseSource=local_base)
    print("web_crawler sources initialization is finished.")
    isInitialized = True

def get_all_headers(sendRequestToUpdatingHeadersInBaseFromSite=False,
                    whichSupertypeUpdateFromSite=None):
    '''
    Get all headers which has given supertype.
    '''
    # TODO: using param 'whichSupertypeUpdateFromSite' not implemented
    headers = Crawler.get_data_source(KSRFSOURCE).\
        get_all_data(DataType.DOCUMENT_HEADER, whichSupertypeUpdateFromSite)
    return headers


def get_text(uid):
    text = Crawler.get_data_source(KSRFSOURCE).\
        get_data(uid, DataType.DOCUMENT_TEXT)
    return text


if __name__ == '__main__':
    print('hi')
    source = Crawler.collected_sources[LOCAL_DATABASE]
    source.folder_path = 'D:\\programming\\Judyst\\files'
    source.prepare()
    init('D:\\programming\\Judyst\\files', source)
    print(get_all_headers())
    print(get_text('КСРФ/35-П/2018'))


if not __package__:
    init('D:\\programming\\Judyst\\files')
    # init(FOLDER_FOR_HEADERS_AND_TEXTS)

