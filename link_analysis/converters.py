import json
import pickle
import os

from models import Header, DuplicateHeader, DocumentHeader


def convert_to_class_format(data, className):
    '''
    argument data: iterable stadard python object like dictionary or list
    with dictionary elements for that class format exist\n
    if data is dictionary, data's keys must be standard python objects\n
    argument className: name of class that contains static method
    'convert_from_dict'. This class is format for element of data argument\n
    returns dictionary or list with instances of class className
    '''
    if not hasattr(data, '__iter__'):
        raise ValueError("'data' is not iterable object")
    if isinstance(data, dict):
        convertedData = {}
        for key in data:
            convertedData[key] = className.convert_from_dict(key, data[key])
    else:
        convertedData = []
        for el in data:
            convertedData.append(className.convert_from_dict(el))
    return convertedData


def convert_to_json_serializable_format(data):
    '''
    argument data: iterable stadard python object like dictionary or list
    if data is dictionary, data's keys must be standard python objects
    with instances of classes which has method 'convert_to_dict';\n
    returns dictionary or list with dictionary elements
    '''
    if not hasattr(data, '__iter__'):
        raise ValueError("'data' is not iterable object")
    if isinstance(data, dict):
        convertedData = {}
        for key in data:
            convertedData[key] = data[key].convert_to_dict()
    else:
        convertedData = []
        for el in data:
            convertedData.append(el.convert_to_dict())
    return convertedData


def save_json(jsonSerializableData, pathToFile):
    try:
        dirname = os.path.dirname(pathToFile)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
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


def save_pickle(anyData, pathToFile):
    try:
        dirname = os.path.dirname(pathToFile)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
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

if __name__ == '__main__':
    pickle1 = load_pickle('Decision files0\\DecisionHeaders.pickle')
    json1 = convert_to_json_serializable_format(pickle1)
    save_json(json1, 'Decision files0\\DecisionHeaders.json')
    json2 = load_json('Decision files0\\DecisionHeaders.json')
    pickle2 = convert_to_class_format(json2, className=DocumentHeader)
    save_pickle(pickle2, 'Decision files0\\DecisionHeaders1.pickle')
    pickle3 = load_pickle('Decision files0\\DecisionHeaders1.pickle')
    json3 = convert_to_json_serializable_format(pickle3)
    save_json(json3, 'Decision files0\\DecisionHeaders3.json')

    json3file = open('Decision files0\\DecisionHeaders3.json', 'r')
    json3text = json3file.read()
    json1file = open('Decision files0\\DecisionHeaders.json', 'r')
    json1text = json1file.read()
    for i in range(len(json1text)):
        if json1text[i] != json3text[i]:
            repr(json1text[i])
            print(json1text[i])
            break
    print('all done')
