import json
import pickle
import os
import datetime
import dateutil.parser
from link_analysis.models import Header, DuplicateHeader


def convert_dictDict_to_dictDocumentHeader(headersOldFormat):
    headersNewFormat = {}
    try:
        for key in headersOldFormat:
            docID = key
            if 'not unique' not in headersOldFormat[key]:
                docType = headersOldFormat[key]['type']
                title = headersOldFormat[key]['title']
                date = dateutil.parser.parse(headersOldFormat[key]['date'],
                                             dayfirst=True).date()
                sourceUrl = headersOldFormat[key]['url']
                if 'path to text file' in headersOldFormat[key]:
                    textLocation = headersOldFormat[key]['path to text file']
                else:
                    textLocation = None
                headersNewFormat[key] = Header(
                    docID, docType, title, date, sourceUrl, textLocation)
            else:
                duplicateHeader = DuplicateHeader(docID)
                for dh in headersOldFormat[key][1]:
                    title = dh['title']
                    date = dateutil.parser.parse(dh['date'],
                                                 dayfirst=True).date()
                    sourceUrl = dh['url']
                    if 'path to text file' in dh:
                        textLocation = dh[key]['path to text file']
                    else:
                        textLocation = None
                    duplicateHeader.append(docType, title, date,
                                           sourceUrl, textLocation)
                headersNewFormat[key] = duplicateHeader
    except KeyError:
        raise KeyError("'type', 'title', 'date', 'url' is required, "
                       "only 'path to file' is optional")
    return headersNewFormat


def convert_dictDocumentHeader_to_dicDict(headersNewFormat):
    headersOldFormat = {}
    for key in headersNewFormat:
        if isinstance(headersNewFormat[key], Header):
            headersOldFormat[key] = {}
            headersOldFormat[key]['type'] = headersNewFormat[key].document_type
            headersOldFormat[key]['title'] = headersNewFormat[key].title
            headersOldFormat[key]['date'] = \
                headersNewFormat[key].date.strftime('%d.%m.%Y')
            headersOldFormat[key]['url'] = headersNewFormat[key].source_url
            if headersNewFormat[key].text_location is not None:
                headersOldFormat[key]['path to text file'] = \
                    headersNewFormat[key].text_location
        elif isinstance(headersNewFormat[key], DuplicateHeader):
            dhList = []
            for dupHeader in headersNewFormat[key].header_list:
                dh = {}
                dh['type'] = dupHeader.document_type
                dh['title'] = dupHeader.title
                dh['date'] = dupHeader.date.strftime('%d.%m.%Y')
                dh['url'] = dupHeader.source_url
                if dupHeader.text_location is not None:
                    dh['path to text file'] = dupHeader.text_location
                dhList.append(dh)
            headersOldFormat[key] = ('not unique', dhList)
        else:
            raise TypeError("Variable 'headersNewFormat' is not instance of "
                            "class Header or class DuplicateHeader")
    return headersOldFormat


def save_json(jsonSerializableData, pathToFile):
    try:
        os.makedirs(os.path.dirname(pathToFile), exist_ok=True)
        with open(pathToFile, 'w') as jsonFile:
            json.dump(jsonSerializableData, jsonFile)
    except OSError:
        return False
    return True


def load_json(pathToFile):
    try:
        with open(pathToFile) as jsonFile:
            data = json.load(jsonFile)
    except OSError:
        return None
    return data


def save_pickle(anyData, pathToFile, exist_ok=True):
    try:
        os.makedirs(os.path.dirname(pathToFile))
        with open(pathToFile, 'wb') as pickleFile:
            pickle.dump(anyData, pickleFile)
    except OSError:
        return False
    return True


def load_pickle(pathToFile):
    try:
        with open(pathToFile, 'rb') as pickleFile:
            data = pickle.load(pickleFile, encoding='UTF-8')
    except OSError:
        return None
    return data
