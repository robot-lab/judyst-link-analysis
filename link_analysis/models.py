import datetime
import collections
from typing import Type, Optional, Union

import dateutil.parser
# License: Apache Software Licenseid, BSD License (Dual License)


class DocumentHeader:

    """
    Base class for subclasses Header and DuplicateHeader.
    Instance stores data about document like court decision.

    :attribute doc_id: str.
        ID of document.

    :methods convert_from_dict: staticmethod.
        Interface method. Calls method with same name from subclasses
        and returns their response.
    """

    def __init__(self, docID: str) -> None:
        """
        Creates instance using document ID. Used at subclasses.

        :param docID: str.
            ID of document.
        """
        if isinstance(docID, str):
            self.doc_id = docID
        else:
            raise TypeError(f"'docID' must be instance of {str}")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            raise TypeError(f"Compared objects must be of the same type:"
                            f"{type(self)} or {type(other)}")
        return self.doc_id == other.doc_id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.doc_id)

    @staticmethod
    def convert_from_dict(key: str,
                          oldFormatHeader: dict):# -> Type[DocumentHeader]:
        """
        Convert dict object to instance of subclass of class DocumentHeader.

        :param key: str.
            Key which related with oldFormatHeader.
        :param oldFormatHeader: {dict}.
            Dict object that stores data about document.

        :return: DocumentHeader.
            Instance of one of subclasses (Header or DuplicateHeader).
        """

        if not isinstance(key, str):
            raise TypeError(f"'key' must be instance of {str}")
        if (not isinstance(oldFormatHeader, dict) and not isinstance(oldFormatHeader, tuple) and
                not isinstance(oldFormatHeader, list)):
            raise TypeError(f"'oldFormatHeader' must be instance of {dict} or {tuple} or {list}")

        if 'not unique' in oldFormatHeader:
            return DuplicateHeader.convert_from_dict(key, oldFormatHeader)
        else:
            return Header.convert_from_dict(key, oldFormatHeader)


class Header(DocumentHeader):

    """
    Subclass of DocumentHeader. Implements storage of data
    about document whose identifier is unique.

    :attribute doc_id: str.
        ID of document.
    :attribute supertype: str.
        Supertype of document.
    :attribute doc_type: str.
        Type of document.
    :attribute title: str.
        Title of document.
    :attribute release_date: datetime.date.
        Release date of document
    :attribute text_source_url: str.
        URL of document text source.
    :attribute text_location: str, optional (default=None).
        Location of text document.

    :method convert_to_dict: instancemethod.
        Convert instance to dict object.
    :method convert_from_dict: staticmethod.
        Convert dict object to instance of own class.
        Called from superclass by iterface method with same name.
    """

    def __init__(self, docID: str, supertype: str, docType: str, title: str,
                 releaseDate: datetime.date, textSourceUrl: str,
                 textLocation: Optional[str]=None) -> None:

        """
        Constructor which uses superclass constructor passing it an arg docID.

        :param docID: str.
            ID of document.
        :param supertype: str.
            Supertype of document.
        :param docType: str.
            Type of document.
        :param title: str.
            Title of document.
        :param releaseDate: datetime.date.
            Release date of document.
        :param textSourceUrl: str.
            URL of document text source.
        :param textLocation: str, optional (default=None).
            Location of text document.
        """
        super().__init__(docID)
        if isinstance(docType, str):
            self.supertype = supertype
        else:
            raise TypeError(f"'supertype' must be instance of {supertype}")
        if isinstance(docType, str):
            self.doc_type = docType
        else:
            raise TypeError(f"'docType' must be instance of {str}")
        if isinstance(title, str):
            self.title = title
        else:
            raise TypeError(f"'title' must be instance of {str}")
        if isinstance(releaseDate, datetime.date):
            self.release_date = releaseDate
        else:
            raise TypeError(f"'releaseDate' must be instance of {datetime.date}")
        if isinstance(textSourceUrl, str):
            self.text_source_url = textSourceUrl
        else:
            raise TypeError(f"'textSourceUrl' must be instance of {str}")
        if isinstance(textLocation, str) or textLocation is None:
            self.text_location = textLocation
        else:
            raise TypeError(f"'textLocation' must be instance of {str}")

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(f"Compared objects must be of the same type:"
                            f"{type(self)} or {type(other)}")
        return (super().__eq__(self) and
                self.supertype == other.supertype and
                self.doc_type == other.doc_type and
                self.title == other.title and
                self.release_date == other.release_date and
                self.text_source_url == other.text_source_url)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return super().__hash__()

    def convert_to_dict(self):
        """
        Convert instance to dict object that stores all values
        of attributes of instance.

        :return: dict.
            Dict object that stores values of attributes of instance.
        """
        dictFormatHeader = {
            'supertype': self.supertype,
            'doc_type': self.doc_type,
            'title': self.title,
            'release_date': self.release_date.strftime('%d.%m.%Y'),
            'text_source_url': self.text_source_url
            }
        if self.text_location is not None:
            dictFormatHeader['text_location'] = self.text_location
        return dictFormatHeader

    @staticmethod
    def convert_from_dict(key: str, oldFormatHeader: dict):
        """
        Convert dict object to instance of own class.
        Called from superclass by iterface method with same name.

        :param key: str.
            Key which related with oldFormatHeader.
        :param oldFormatHeader: dict.
            Dict object that stores data about document.

        :return: Header.
            Instance of own class.
        """

        if not isinstance(key, str):
            raise TypeError(f"'key' mus be instance of {str}")
        if not isinstance(oldFormatHeader, dict):
            raise TypeError("'oldFormatHeader' must be instance of 'dict'")

        try:
            docID = key
            supertype = oldFormatHeader['supertype']
            docType = oldFormatHeader['doc_type']
            title = oldFormatHeader['title']
            releaseDate = dateutil.parser.parse(oldFormatHeader['release_date'],
                                         dayfirst=True).date()
            textSourceUrl = oldFormatHeader['text_source_url']
            if 'text_location' in oldFormatHeader:
                textLocation = oldFormatHeader['text_location']
            else:
                textLocation = None
        except KeyError:
            raise KeyError("'doc_type', 'supertype', 'title', 'release_date', "
                           "'text_source_url' is required, "
                           "only 'path to file' is optional")
        return Header(docID, supertype, docType, title, releaseDate, textSourceUrl, textLocation)


class DuplicateHeader(DocumentHeader):

    """
    Subclass of DocumentHeader. Implements storage of data
    about document whose identifier is not unique.

    :attribute doc_id: str.
        Common ID of duplicated documents.
    :attribute header_list: list.
        List with instances of class Header.
        Any of them stores data about one of the duplicated documents.

    :method append: instancemethod.
        Append instance of class Header that contains data
        about duplicated document at self.header_list.
    :method convert_to_dict: instancemethod.
        Convert instance to dict object.
    :method convert_from_dict: staticmethod.
        Convert dict object to instance of own class.
        Called from superclass by iterface method with same name.
    """

    def __init__(self, docID, supertype=None, docType=None, title=None, releaseDate=None,
                 textSourceUrl=None, textLocation=None):
        """
        Constructor with optinal arguments. You must specify either
        argument 'docID' only to create empty list that ready to append
        new elements or all arguments except optional 'textLocation' to create
        list with first element.

        :param docID: str.
            Common ID of duplicated documents.
        :param supertype: str.
            Supertype of first duplicated document that be added at list.
        :param docType: str.
            Type of first duplicated document that be added at list.
        :param title: str.
            Title of first duplicated document that be added at list.
        :param releaseDate: datetime.date.
            Release date of first duplicated document that be added at list.
        :param textSourceUrl: str.
            URL of text source of first duplicated document that be added at list.
        :param textLocation: str, optional (default=None).
            Text location of first duplicated document that be added at list.
        """
        if isinstance(docID, str):
            super().__init__(docID)
        else:
            raise TypeError(f"'docID' must be instance of {str}")
        if isinstance(supertype, str) or supertype is None:
            self.supertype = supertype
        else:
            raise TypeError(f"'supertype' must be instance of {str}")
        if isinstance(docType, str) or docType is None:
            self.doc_type = docType
        else:
            raise TypeError(f"'docType' must be instance of {str}")
        if isinstance(title, str) or title is None:
            self.title = title
        else:
            raise TypeError(f"'title' must be instance of {str}")
        if isinstance(releaseDate, datetime.date) or releaseDate is None:
            self.release_date = releaseDate
        else:
            raise TypeError(f"'release_date' must be instance of {datetime.date}")
        if isinstance(textSourceUrl, str) or textSourceUrl is None:
            self.text_source_url = textSourceUrl
        else:
            raise TypeError(f"'textSourceUrl' must be instance of {str}")
        if isinstance(textLocation, str) or textLocation is None:
            self.text_location = textLocation
        else:
            raise TypeError(f"'textLocation' must be instance of {str}")

        if (supertype is None and docType is None and title is None and
            releaseDate is None and  textSourceUrl is None and
                textLocation is None):
            self.header_list = []
        elif (supertype is not None and docType is not None and
              title is not None and releaseDate is not None and
                textSourceUrl is not None):
            self.header_list = [Header(docID, supertype, docType, title,
                                releaseDate, textSourceUrl, textLocation)]
        else:
            raise ValueError("You must specify either argument 'docID' only or"
                             " all arguments except optional 'textLocation'")

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(f"Compared objects must be of the same type:"
                            f"{type(self)} or {type(other)}")
        return (super().__eq__(other) and
                (collections.Counter(self.header_list) ==
                collections.Counter(other.header_list)))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return super().__hash__()

    def append(self, supertype, docType, title, releaseDate, textSourceUrl,
               textLocation=None):
        """
        Append instance of class Header that contains data
        about duplicated document at self.header_list.

        :param supertype: str.
            Supertype of document that be added at list.
        :param docType: str.
            Type of document that be added at list.
        :param title: str.
            Title of document that be added at list.
        :param releaseDate: datetime.date.
            Release date of document that be added at list.
        :param textSourceUrl: str.
            URL of text source of document that be added at list.
        :param textLocation: str, optional (default=None).
            Text location of document that be added at list.
        """
        if isinstance(supertype, str) or supertype is None:
            self.supertype = supertype
        else:
            raise TypeError(f"'supertype' must be instance of {str}")
        if isinstance(docType, str) or docType is None:
            self.doc_type = docType
        else:
            raise TypeError(f"'docType' must be instance of {str}")
        if isinstance(title, str) or title is None:
            self.title = title
        else:
            raise TypeError(f"'title' must be instance of {str}")
        if isinstance(releaseDate, datetime.date) or releaseDate is None:
            self.release_date = releaseDate
        else:
            raise TypeError(f"'releaseDate' must be instance of {datetime.date}")
        if isinstance(textSourceUrl, str) or textSourceUrl is None:
            self.text_source_url = textSourceUrl
        else:
            raise TypeError(f"'textSourceUrl' must be instance of {str}")
        if isinstance(textLocation, str) or textLocation is None:
            self.text_location = textLocation
        else:
            raise TypeError(f"'textLocation' must be instance of {str}")

        h = Header(self.doc_id, supertype, docType, title, releaseDate, textSourceUrl,
                   textLocation)
        if h not in self.header_list:
            self.header_list.append(h)

    def convert_to_dict(self):
        """
        Convert instance to dict object that stores all values of attributes of instance.

        :return: dict.
            Dict object that stores values of attributes of instance.
        """
        dhList = []
        for dupHeader in self.header_list:
            dh = {
                'supertype': dupHeader.supertype,
                'doc_type':  dupHeader.doc_type,
                'title':  dupHeader.title,
                'release_date':  dupHeader.release_date.strftime('%d.%m.%Y'),
                'text_source_url':  dupHeader.text_source_url
                }
            if dupHeader.text_location is not None:
                dh['text_location'] = dupHeader.text_location
            dhList.append(dh)
        return ('not unique', dhList)

    @staticmethod
    def convert_from_dict(key: str, oldFormatHeader: dict):
        """
        Convert dict object to instance of own class.
        Called from superclass by iterface method with same name.

        :param key: str.
            Key which related with oldFormatHeader.
        :param oldFormatHeader: dict.
            Dict object that stores data about document.

        :return: DuplicateHeader.
            Instance of own class.
        """
        if not isinstance(key, str):
            raise TypeError(f"'key' mus be instance of {str}")
        if (not isinstance(oldFormatHeader, dict) and not isinstance(oldFormatHeader, tuple) and
                not isinstance(oldFormatHeader, list)):
            raise TypeError(f"'oldFormatHeader' must be instance of {dict} or {tuple} or {list}")
        docID = key
        duplicateHeader = DuplicateHeader(docID)
        try:
            for dh in oldFormatHeader[1]:
                supertype = dh['supertype']
                docType = dh['doc_type']
                title = dh['title']
                releaseDate = dateutil.parser.parse(dh['release_date'],
                                             dayfirst=True).date()
                textSourceUrl = dh['text_source_url']
                if 'text_location' in dh:
                    textLocation = dh['text_location']
                else:
                    textLocation = None
                duplicateHeader.append(supertype, docType, title, releaseDate,
                                       textSourceUrl, textLocation)
        except KeyError:
            raise KeyError(
                "'supertype', 'doc_type', 'title', 'release_date', "
                "'text_source_url' is required, only 'text_location' "
                "is optional")
        return duplicateHeader


class Link:
    def __init__(self, headerFrom):
        """
        :param headerFrom: class Header
            Citing document
        """
        if not isinstance(headerFrom, Header):
            raise TypeError("Variable 'headerFrom' is not instance "
                            "of class Header")
        self.header_from = headerFrom

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(f"Compared objects must be of the same type:"
                            f"{type(self)} or {type(other)}")
        return self.header_from == other.header_from

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.header_from)


class RoughLink(Link):
    def __init__(self, headerFrom, body, context, position):
        """
        :param headerFrom: class Header
            Citing document
        """
        if not isinstance(headerFrom, Header):
            raise TypeError("Variable 'headerFrom' is not instance "
                            "of class Header")
        super().__init__(headerFrom)
        self.body = body
        self.context = context
        self.position = position

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(f"Compared objects must be of the same type:"
                            f"{type(self)} or {type(other)}")
        return (super().__eq__(other) and
                self.context == other.context and
                self.body == other.body and
                self.position == other.position)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(tuple([super().__hash__(),
                    hash(self.context),
                    hash(self.body),
                    hash(self.position)]))


class CleanLink(Link):
    """
    class member: positionsAndContexts: list of tuple(int, str)
    where int variable (position) is start position of str variable
    (contex) in text
    """
    def __init__(self, headerFrom, headerTo, citationsNumber,
                 positionsAndContexts):
        """
        positionsAndContexts: tuple or list of tuples, "
        or set of tuples(int, str)
        """
        super().__init__(headerFrom)
        self.header_to = headerTo
        self.citations_number = citationsNumber
        if isinstance(positionsAndContexts, tuple):
            self.positions_and_contexts = [positionsAndContexts]
        else:
            self.positions_and_contexts = list(positionsAndContexts)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(f"Compared objects must be of the same type:"
                            f"{type(self)} or {type(other)}")
        return (super().__eq__(other) and
                self.header_to == other.header_to and
                self.citations_number == other.citations_number and
                (collections.Counter(self.positions_and_contexts) ==
                 collections.Counter(other.positions_and_contexts)))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(tuple([super().__hash__(), hash(self.header_to)]))

    def append(self, positionAndContext: tuple):
        self.positions_and_contexts.append(positionAndContext)
    
    def convert_to_dict(self):
        cleanLinkDict = {
            'doc_id_from': self.header_from.doc_id,
            'doc_id_to': self.header_to.doc_id,
            'to_doc_title': self.header_to.title,
            'citations_number': self.citations_number,
            'contexts_list': [pac[1] for pac in self.positions_and_contexts],
            'positions_list': [pac[0] for pac in self.positions_and_contexts]
        }
        return cleanLinkDict


class HeadersFilter():
    """
    Arguments contains conditions for which headers will be selected.\n
    firstDate and lastDate: instances of datetime.date
    """
    def __init__(self, supertypes=None, docTypes=None, firstDate=None,
                 lastDate=None):
        if hasattr(supertypes, '__iter__'):
            self.supertypes = set(supertypes)
        else:
            self.supertypes = None
        if hasattr(docTypes, '__iter__'):
            self.doc_types = set(docTypes)
        else:
            self.doc_types = None
        if firstDate is None:
            self.first_date = datetime.date.min
        elif isinstance(firstDate, datetime.date):
            self.first_date = firstDate
        else:
            raise TypeError("Variable 'firstDate' is not instance "
                            "of datetime.date")

        if lastDate is None:
            self.last_date = datetime.date.max
        elif isinstance(lastDate, datetime.date):
            self.last_date = lastDate
        else:
            raise TypeError("Variable 'lastDate' is not instance "
                            "of datetime.date")

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(f"Compared objects must be of the same type:"
                            f"{type(self)} or {type(other)}")
        return (self.supertypes == other.supertypes and
                self.doc_types == other.doc_types and
                self.first_date == other.first_date and
                self.last_date == other.last_date)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(tuple([hash(tuple(self.supertypes)),
                           hash(tuple(self.doc_types)),
                           hash(self.first_date),
                           hash(self.last_date)]))

    def check_header(self, header):
        if ((self.supertypes is None or
            header.supertype in self.supertypes) and
            (self.doc_types is None or
            header.doc_type in self.doc_types) and
                self.first_date <= header.release_date <= self.last_date):
            return True
        else:
            return False

    def get_filtered_headers(self, headersDict):
        resultDict = {}
        for key in headersDict:
            if (isinstance(headersDict[key], Header) and
                    self.check_header(headersDict[key])):
                resultDict[key] = headersDict[key]
        return resultDict


class GraphNodesFilter(HeadersFilter):
    """
    Arguments contains conditions for which nodes will be selected.\n
    firstDate and lastDate: instances of datetime.date\n
    indegreeRange and outdegreeRange: tuples that implements
    own line segment [int, int]
    """
    def __init__(self, supertype=None, docTypes=None, firstDate=None,
                 lastDate=None, indegreeRange=None,
                 outdegreeRange=None):
        super().__init__(supertype, docTypes, firstDate, lastDate)
        self.indegree_range = indegreeRange
        self.outdegree_range = outdegreeRange

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(f"Compared objects must be of the same type:"
                            f"{type(self)} or {type(other)}")
        return (super().__eq__(other) and
                self.indegree_range == other.indegree_range and
                self.outdegree_range == other.outdegree_range)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(tuple([super().__hash__(),
                    hash(self.indegree_range),
                    hash(self.outdegree_range)]))


class GraphEdgesFilter():
    """
    Arguments contains conditions for which edges will be selected.\n
    weightsRange: tuple that implements line segment [int, int]
    """
    def __init__(self, headersFilterFrom=None, headerFilterTo=None,
                 weightsRange=None):

        self.headers_filter_from = headersFilterFrom
        self.headers_filter_to = headerFilterTo
        self.weights_range = weightsRange

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(f"Compared objects must be of the same type:"
                            f"{type(self)} or {type(other)}")
        return (self.headers_filter_from == other.headers_filter_from and
                self.headers_filter_to == other.headers_filter_to and
                self.weights_range == other.weights_range)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(tuple([hash(self.headers_filter_from),
                    hash(self.headers_filter_to),
                    hash(self.weights_range)]))

    def check_edge(self, edge: CleanLink):
        """edge: class CleanLink"""
        if ((self.headers_filter_from is None or
             self.headers_filter_from.check_header(edge.header_from)
             ) and
            (self.headers_filter_to is None or
             self.headers_filter_to.check_header(edge.header_to)
             ) and
            (self.weights_range is None or (self.weights_range[0] <=
             edge.citations_number <= self.weights_range[1]))):
            return True
        else:
            return False

    def get_filtered_edges(self, edges):
        """
        edges: list or set of instances of class CleanLink\n
        returns set of instances of class CleanLink
        """
        result = {edge for edge in edges if self.check_edge(edge)}
        return result


class LinkGraph:
    """
    nodes: set of class Header instances\n
    edges: set of class CleanLink  instances
    """
    def __init__(self):
        self.nodes = set()
        self.edges = set()

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(f"Compared objects must be of the same type:"
                            f"{type(self)} or {type(other)}")
        return (self.nodes == other.nodes and
                self.edges == other.edges)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        import time  # DEBUG
        start_time = time.time()  # DEBUG
        vHash = hash(tuple(sorted(self.nodes, key=lambda h: hash(h))))
        eHash = hash(tuple(sorted(self.edges, key=lambda e: hash(e))))
        # It will be interesting to know:
        if False:  # DEBUG
            raise Exception('We finally needed the graph hash. It takes '
                            f'{time.time()-start_time} seconds')  # DEBUG
        return hash(tuple([vHash, eHash]))

    def add_node(self, node):
        if not isinstance(node, Header):
            raise TypeError("Variable 'node' is not instance "
                            "of class Header")
        self.nodes.add(node)

    def add_edge(self, edge):
        if not isinstance(edge, CleanLink):
            raise TypeError("Variable 'edge' is not instance "
                            "of class CleanLink")
        self.edges.add(edge)

    def get_all_nodes_degrees(self):
        nodes_i = []
        nodes_o = []
        for edge in self.edges:
            nodes_i.append(edge.header_from)
            nodes_o.append(edge.header_to)
        indegree = collections.Counter(nodes_i)
        outdegree = collections.Counter(nodes_o)
        return (indegree, outdegree)

    def get_subgraph(self, nodesFilter=None, edgesFilter=None,
                     includeIsolatedNodes=True):

        if (nodesFilter is None and edgesFilter is None):
            return self

        subgraph = LinkGraph()
        # filters nodes
        if nodesFilter is not None:
            if not isinstance(nodesFilter, GraphNodesFilter):
                raise TypeError("Variable 'nodesFilter' is not instance "
                                "of class GraphNodesFilter")
            if (nodesFilter.indegree_range is not None or
                    nodesFilter.outdegree_range is not None):
                indegrees, outdegrees = self.get_all_nodes_degrees()
            for node in self.nodes:
                indegreeEggs = False
                outdegreeEggs = False
                restEggs = False
                if (nodesFilter.indegree_range is None or
                   (nodesFilter.indegree_range[0] <= indegrees[node] <=
                        nodesFilter.indegree_range[1])):
                    indegreeEggs = True
                if (nodesFilter.outdegree_range is None or
                   (nodesFilter.outdegree_range[0] <= outdegrees[node] <=
                        nodesFilter.outdegree_range[1])):
                    outdegreeEggs = True
                if nodesFilter.check_header(node):
                    restEggs = True
                if (indegreeEggs and outdegreeEggs and restEggs):
                    subgraph.nodes.add(node)
        else:
            subgraph.nodes = self.nodes

        # filters edges
        if edgesFilter is not None:
            if not isinstance(edgesFilter, GraphEdgesFilter):
                raise TypeError("Variable 'edgesFilter' is not instance "
                                "of class GraphEdgesFilter")

            # If nodes are filtered, we must check the edges
            # associated with them and then filter them,
            if nodesFilter is not None:
                for edge in self.edges:
                    if (edge.header_from in subgraph.nodes and
                        edge.header_to in subgraph.nodes and
                            edgesFilter.check_edge(edge)):
                        subgraph.edges.add(edge)

            # else just filter the edges
            else:
                for edge in self.edges:
                    if edgesFilter.check_edge(edge):
                        subgraph.edges.add(edge)

        # We need to check edges after filtering of nodes
        # even if edges are not filtered
        else:
            for edge in self.edges:
                if (edge.header_from in subgraph.nodes and
                        edge.header_to in subgraph.nodes):
                    subgraph.edges.add(edge)
        if not includeIsolatedNodes:
            subgraph.nodes = set()
            for edge in subgraph.edges:
                subgraph.add_node(edge.header_from)
                subgraph.add_node(edge.header_to)
        return subgraph

    def get_nodes_as_IDs_list(self):
        return list(v.doc_id for v in self.nodes)

    def get_edges_as_list_of_tuples(self):
        return list((e.header_from.doc_id, e.header_to.doc_id, e.citations_number)
                    for e in self.edges)

    def get_itearable_link_graph(self):  # stub
        pass


class IterableLinkGraph(LinkGraph):  # stub
    pass


if __name__ == "__main__":
    date = datetime.date(2018, 12, 11)
    # h1 = Header("456-О-О/2018", "КСРФ/О-О", "Заголовк", date,
    #             "https://goto.ru", "path-to")
    # h2 = Header("456-О-О/2018", "КСРФ/О-О", "Заголовк", date,
    #             "https://goto.ru")
    # h3 = Header("456-О-О/2018", "КСРФ/О-О", "Заголовк", date,
    #             "https://goto.ru")
    # h4 = Header("456-О-О/2018", "КСРФ/О-О", "Заголовк", date,
    #             "https://goto.ru")
    h5 = DuplicateHeader("456-О-О/2018", "КСРФ/О-О", "Заголовк", date,
                         "https://goto.ru")
    h6 = DuplicateHeader("426-О-О/2018", "КСРФ/О-О", "Заголовк", date,
                         "https://goto.ru")
    print(hash(h5))
    h5 == h6
    # h5.append("КСРФ/О-О", "Заголовк", datetime.date(1990, 1, 2),
    #           "https://goto.ru")
    # h6 = DuplicateHeader("456-О-О/2018", "КСРФ/О-О", "Заголовк", date,
    #                      "https://goto.ru")
    # a = LinkGraph()
    # b = LinkGraph()
    # a.add_node(h2)
    # b.add_node(h3)
    A = LinkGraph()
    # B = {A:1}
    input('press any key...')
