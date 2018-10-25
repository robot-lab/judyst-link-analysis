from web_crawler import Crawler, DataType
import converters
import models

SUPERTYPE = 'КСРФ'
KSRFSOURCE = 'KSRFSource'
DATABASESOURCE = 'LocalFileStorage'
isInitialized = False


def init():
    Crawler.prepare_sources([DATABASESOURCE, KSRFSOURCE])
    isInitialized = True


def get_all_headers(supertype='КСРФ'):
    '''
    Get all headers which has given supertype. 
    '''
    headers = Crawler.get_data_source(KSRFSOURCE).\
        get_all_data(DataType.DOCUMENT_HEADER)
    correct_headers = {uid: headers[uid] for uid in headers
                       if headers[uid]['supertype'] == supertype} 
    return converters.convert_to_class_format(
           correct_headers, models.DocumentHeader)


def get_text(uid):
    return Crawler.get_data_source(DATABASESOURCE).\
        get_data(uid, DataType.DOCUMENT_TEXT)

