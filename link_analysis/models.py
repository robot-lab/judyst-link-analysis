import datetime
import collections
from typing import Type, Optional, Union, Dict

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
                          oldFormatHeader: Dict):# -> Type[DocumentHeader]:
        """
        Convert dict object to instance of subclass of class DocumentHeader.

        :param key: str.
            Key which related with oldFormatHeader.
        :param oldFormatHeader: dict.
            Dict object that stores data about document.

        :return: DocumentHeader.
            Instance of one of subclasses (Header or DuplicateHeader).
        """
        if 'not unique' in oldFormatHeader:
            raise TypeError("'class DuplicateHeader' is not supported anymore.")
        if not isinstance(key, str):
            raise TypeError(f"'key' must be instance of {str}")
        if not isinstance(oldFormatHeader, dict) :
            raise TypeError(f"'oldFormatHeader' must be instance of {dict}")
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
                 releaseDate: datetime.date, textSourceUrl: str) -> None:

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
            raise TypeError(f"'oldFormatHeader' must be instance of {dict}'")

        try:
            docID = key
            supertype = oldFormatHeader['supertype']
            docType = oldFormatHeader['doc_type']
            title = oldFormatHeader['title']
            releaseDate = dateutil.parser.parse(oldFormatHeader['release_date'],
                                         dayfirst=True).date()
            textSourceUrl = oldFormatHeader['text_source_url']
        except KeyError:
            raise KeyError("'doc_type', 'supertype', 'title', 'release_date', "
                           "'text_source_url' is required")
        return Header(docID, supertype, docType, title, releaseDate, textSourceUrl)


class Link:
    def __init__(self, headerFrom):
        """
        :param headerFrom: class Header
            Citing document
        """
        if not isinstance(headerFrom, Header):
            raise TypeError(f"'headerFrom' must be instance of {Header}")
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

class Positions:

    def __init__(self, contextStartPos, contextEndPos, linkStartPos, linkEndPos):
        if isinstance(contextStartPos, int):
            self.context_start = contextStartPos
        else:
            raise TypeError(f"'contextStartPos' must be {int}")
        if isinstance(contextEndPos, int):
            self.context_end = contextEndPos
        else:
            raise TypeError(f"'contextEndPos' must be {int}")
        if isinstance(linkStartPos, int):
            self.link_start = linkStartPos
        else:
            raise TypeError(f"'linkStartPos' must be {int}")
        if isinstance(linkEndPos, int):
            self.link_end = linkEndPos
        else:
            raise TypeError(f"'linkEndPos' must be {int}")

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(f"Compared objects must be of the same type:"
                            f"{type(self)} or {type(other)}")
        return (self.context_start == other.context_start and
                self.context_end == other.context_end and
                self.link_start == other.link_start and
                self.link_end == other.link_end)

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(tuple(hash(self.context_start),
                          hash(self.context_end),
                          hash(self.link_start),
                          hash(self.link_end)
                          ))

class RoughLink(Link):
    def __init__(self, headerFrom: Header, body: str, positions: Positions):
        """
        :param headerFrom: class Header
            Citing document
        """
        if not isinstance(headerFrom, Header):
            raise TypeError(f"'headerFrom' must be instance of {Header}")
        super().__init__(headerFrom)
        if isinstance(body, str):
            self.body = body
        else:
            raise TypeError(f"'body' must be instance of {str}")
        if isinstance(positions, Positions):
            self.positions = positions
        else:
            raise TypeError(f"'positions' must be instance of {Positions}")

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(f"Compared objects must be of the same type:"
                            f"{type(self)} or {type(other)}")
        return (super().__eq__(other) and
                self.body == other.body and
                self.positions == other.positions)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(tuple([super().__hash__(),
                    hash(self.body),
                    hash(self.positions)]))



class CleanLink(Link):
    """
    class member: positionsAndContexts: list of tuple(int, str)
    where int variable (position) is start position of str variable
    (contex) in text
    """

    def __init__(self, headerFrom, headerTo, citationsNumber,
                 positionsList):
        """
        positionsAndContexts: tuple or list of tuples, "
        or set of tuples(int, str)
        """
        super().__init__(headerFrom)
        if isinstance(headerTo, Header):
            self.header_to = headerTo
        else:
            raise TypeError(f"'headerTo' must be instance of {Header}")

        if isinstance(citationsNumber, int):
            self.citations_number = citationsNumber
        else:
            raise TypeError(f"'citationsNumber' must be instance of {int}")
        if isinstance(positionsList, Positions):
            self.positions_list = [positionsList]
        elif (isinstance(positionsList, list) or
              isinstance(positionsList, set) or
              isinstance(positionsList, tuple)):
            self.positions_list = list(positionsList)
        else:
            raise TypeError(f"'positionsList' must be instance of {list} or {tuple} or {set}")

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(f"Compared objects must be of the same type:"
                            f"{type(self)} or {type(other)}")
        return (super().__eq__(other) and
                self.header_to == other.header_to and
                self.citations_number == other.citations_number and
                (collections.Counter(self.positions_list) ==
                 collections.Counter(other.positions_list)))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(tuple([super().__hash__(), hash(self.header_to)]))

    def append(self, positionAndContext: tuple):
        self.positions_list.append(positionAndContext)
    
    def convert_to_dict(self):
        cleanLinkDict = {
            'doc_id_from': self.header_from.doc_id,
            'doc_id_to': self.header_to.doc_id
        }
        positionsDictList = [pos.__dict__ for pos in self.positions_list]
        cleanLinkDict['positions_list'] = positionsDictList
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
            for st in supertypes:
                if not isinstance(st, str):
                    raise TypeError(f"any element from 'supertypes' must be instance of {str}")
        elif supertypes is None:
            self.supertypes = supertypes
        else:
            raise TypeError(f"'supertypes' must be iterable structure: {list}, {set}, {tuple}")

        if hasattr(docTypes, '__iter__'):
            self.doc_types = set(docTypes)
            for st in docTypes:
                if not isinstance(st, str):
                    raise TypeError(f"any element from 'docTypes' must be instance of {str}")
        elif docTypes is None:
            self.doc_types = docTypes
        else:
            raise TypeError(f"'docTypes' must be iterable structure: {list}, {set}, {tuple}")
        if firstDate is None:
            self.first_date = datetime.date.min
        elif isinstance(firstDate, datetime.date):
            self.first_date = firstDate
        else:
            raise TypeError(f"'firstDate' must be instance of {datetime.date}")

        if lastDate is None:
            self.last_date = datetime.date.max
        elif isinstance(lastDate, datetime.date):
            self.last_date = lastDate
        else:
            raise TypeError(f"'lastDate' must be instance of {datetime.date}")

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
        if not isinstance(header, Header):
            raise TypeError(f"'header' must be instance of {Header}")
        if ((self.supertypes is None or
            header.supertype in self.supertypes) and
            (self.doc_types is None or
            header.doc_type in self.doc_types) and
                self.first_date <= header.release_date <= self.last_date):
            return True
        else:
            return False

    def get_filtered_headers(self, headersDict: Dict[str, Header]) -> Dict[str, Header]:
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
        if (isinstance(indegreeRange, tuple) or isinstance(indegreeRange, list)):
            self.indegree_range = tuple(indegreeRange)
        elif indegreeRange is None:
            self.indegree_range = indegreeRange
        else:
            raise TypeError(f"'indegreeRange' must be instance of {tuple} or {list}")
        if (isinstance(outdegreeRange, tuple) or isinstance(outdegreeRange, list)):
            self.outdegree_range = tuple(outdegreeRange)
        elif outdegreeRange is None:
            self.outdegree_range = outdegreeRange
        else:
            raise TypeError(f"'outdegreeRange' must be instance of {tuple} or {list}")
        

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
    def __init__(self, headersFilterFrom=None, headersFilterTo=None,
                 weightsRange=None):
        if (isinstance(headersFilterFrom, HeadersFilter) or
                headersFilterFrom is None):
            self.headers_filter_from = headersFilterFrom
        else:
            raise TypeError(f"'headersFilterFrom' must be instance of {HeadersFilter}")
        if (isinstance(headersFilterTo, HeadersFilter) or
                headersFilterTo is None):
            self.headers_filter_to = headersFilterTo
        else:
            raise TypeError(f"'headersFilterTo' must be instance of {HeadersFilter}")
        if (isinstance(weightsRange, tuple) or isinstance(weightsRange, list)):
            self.weights_range = tuple(weightsRange)
        elif weightsRange is None:
            self.weights_range = weightsRange
        else:
            raise TypeError(f"'weightsRange' must be instance of {tuple} or {list}")


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
        if not isinstance(edge, CleanLink):
            raise TypeError(f"'edge' must be instance of {CleanLink}")

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
        if not (isinstance(edges, set) or isinstance(edges, list) or isinstance(edges, tuple)):
            raise TypeError(f"'edge' must be of instance of {set} or {list} or {tuple}")
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
        # import time  # DEBUG
        # start_time = time.time()  # DEBUG
        vHash = hash(tuple(sorted(self.nodes, key=lambda h: hash(h))))
        eHash = hash(tuple(sorted(self.edges, key=lambda e: hash(e))))
        # It will be interesting to know:
        # if False:  # DEBUG
        #     raise Exception('We finally needed the graph hash. It takes '
        #                     f'{time.time()-start_time} seconds')  # DEBUG
        # print(f'Edge number: {len(self.edges)}')
        # print(f'hash spent {time.time()-start_time} seconds')  # DEBUG
        return hash(tuple([vHash, eHash]))

    def add_node(self, node):
        if not isinstance(node, Header):
            raise TypeError(f"'node is not instance "
                            "of {Header}")
        self.nodes.add(node)

    def add_edge(self, edge):
        if not isinstance(edge, CleanLink):
            raise TypeError(f"'edge' is not instance "
                            "of {CleanLink}")
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

        if not isinstance(includeIsolatedNodes, bool):
            raise TypeError("'includeIsolatedNodes' must be instance of {bool}")

        subgraph = LinkGraph()
        # filters nodes
        if nodesFilter is not None:
            if not isinstance(nodesFilter, GraphNodesFilter):
                raise TypeError(f"Variable 'nodesFilter' is not instance "
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
                raise TypeError(f"Variable 'edgesFilter' is not instance "
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