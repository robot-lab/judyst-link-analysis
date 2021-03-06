import json
import pickle
import os
from typing import Dict, Iterable, TypeVar, Type, List, Union, Any

if __package__:
    from link_analysis.models import Header, DocumentHeader, CleanLink
else:
    from models import Header, DocumentHeader, CleanLink  # type: ignore

# Don't forget to add to this place new classes which contains implementation
# method convert_to_class_format()
classname = Union[Type[DocumentHeader], Type[CleanLink]]
classobjects = Union[DocumentHeader, CleanLink]


def convert_to_class_format(
        data: Iterable[Dict[str, str]],
        className: classname) -> Union[Dict[str, classobjects],
                                       List[classobjects]]:
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
        convertedDataDict = {}  # type: Dict[str, classobjects]
        for key in data:
            convertedDataDict[key] = \
                className.convert_from_dict(key, data[key])  # type: ignore
        return convertedDataDict
    else:
        convertedDataList = []  # type: List[classobjects]
        for el in data:
            convertedDataList.append(
                className.convert_from_dict(el))  # type: ignore
        return convertedDataList


def convert_to_json_serializable_format(
        data: Iterable[classobjects]) -> Union[Dict[str, Dict[str, str]],
                                               List[Dict[str, str]]]:
    '''
    argument data: iterable stadard python object like dictionary or list
    if data is dictionary, data's keys must be standard python objects
    with instances of classes which has method 'convert_to_dict';\n
    returns dictionary or list with dictionary elements
    '''
    if not hasattr(data, '__iter__'):
        raise ValueError("'data' is not iterable object")
    if isinstance(data, dict):
        convertedDataDict = {}  # type: Dict[str, Dict[str, str]]
        for key in data:
            convertedDataDict[key] = data[key].convert_to_dict()
        return convertedDataDict
    else:
        convertedDataList = []  # type: List[Dict[str, str]]
        for el in data:
            convertedDataList.append(el.convert_to_dict())  # type: ignore
        return convertedDataList


def convert_dict_list_cls_to_json_serializable_format(data):
    dataLists = list(data[key] for key in data if data[key])
    resultList = []
    for L in dataLists:
        resultList.extend(L)
    JSONcleanLinks = convert_to_json_serializable_format(resultList)
    return JSONcleanLinks


def save_json(jsonSerializableData: object, pathToFile: str) -> bool:
    try:
        dirname = os.path.dirname(pathToFile)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(pathToFile, 'w', encoding='utf-8') as jsonFile:
            json.dump(jsonSerializableData, jsonFile, ensure_ascii=False)
    except FileExistsError:
        return False
    return True


def load_json(pathToFile: str) -> Union[object, None]:
    try:
        with open(pathToFile, encoding='utf-8') as jsonFile:
            data = json.load(jsonFile)
    except FileNotFoundError:
        return None
    return data


def save_pickle(anyData: Any, pathToFile: str) -> bool:
    try:
        dirname = os.path.dirname(pathToFile)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(pathToFile, 'wb') as pickleFile:
            pickle.dump(anyData, pickleFile)
    except FileExistsError:
        return False
    return True


def load_pickle(pathToFile: str) -> Any:
    try:
        with open(pathToFile, 'rb') as pickleFile:
            data = pickle.load(pickleFile, encoding='UTF-8')
    except FileNotFoundError:
        return None
    return data
