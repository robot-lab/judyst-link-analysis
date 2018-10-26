from web_crawler import Crawler, DataType
import converters
import models

SUPERTYPE = 'КСРФ'
KSRFSOURCE = 'KSRFSource'
DATABASESOURCE = 'LocalFileStorage'
isInitialized = False


def init(folderName):
    # tests    
    global isInitialized
    if (isInitialized):
        return
    Crawler.collected_sources[DATABASESOURCE].folder_path = folderName
    Crawler.prepare_sources([DATABASESOURCE, KSRFSOURCE])
    isInitialized = True


def get_all_headers(supertype='КСРФ'):
    '''
    Get all headers which has given supertype.
    '''
    headers = Crawler.get_data_source(KSRFSOURCE).\
        get_all_data(DataType.DOCUMENT_HEADER)
    correct_headers = {}
    for dataId in headers:
        header = headers[dataId]
        if header['supertype'] == supertype:
            correct_headers[dataId] = header
    return converters.convert_to_class_format(
           correct_headers, models.DocumentHeader)


def get_text(uid):
    return Crawler.get_data_source(DATABASESOURCE).\
        get_data(uid, DataType.DOCUMENT_TEXT)


if __name__ == '__main__':
    print('hi')
    init('D:\\programming\\Judyst\\files')
    print(get_all_headers())
    print(get_text('КСРФ/35-П/2018'))
