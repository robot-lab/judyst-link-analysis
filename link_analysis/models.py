import datetime
import collections
import dateutil.parser
# License: Apache Software License, BSD License (Dual License)


class DocumentHeader:
    def __init__(self, id_):
        self.id = id_

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    @staticmethod
    def convert_from_dict(key: str, oldFormatHeader: dict):
        if 'not unique' in oldFormatHeader:
            return DuplicateHeader.convert_from_dict(key, oldFormatHeader)
        else:
            return Header.convert_from_dict(key, oldFormatHeader)


class Header(DocumentHeader):
    def __init__(self, id, docType, title, date, sourceUrl,
                 textLocation=None):
        super().__init__(id)
        self.document_type = docType
        self.title = title
        if isinstance(date, datetime.date):
            self.date = date
        else:
            raise TypeError("Variable 'date' is not instance of datetime.date")
        self.source_url = sourceUrl
        self.text_location = textLocation

    def __eq__(self, other):
        return (super().__eq__(self) and
                self.document_type == other.document_type and
                self.title == other.title and
                self.date == other.date and
                self.source_url == other.source_url)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return super().__hash__()

    def convert_to_dict(self):
        dictFormatHeader = {
            'type': self.document_type,
            'title': self.title,
            'date': self.date.strftime('%d.%m.%Y'),
            'url': self.source_url
            }
        if self.text_location is not None:
            dictFormatHeader['path to text file'] = self.text_location
        return dictFormatHeader

    @staticmethod
    def convert_from_dict(key: str, oldFormatHeader: dict):
        try:
            docID = key
            docType = oldFormatHeader['type']
            title = oldFormatHeader['title']
            date = dateutil.parser.parse(oldFormatHeader['date'],
                                         dayfirst=True).date()
            sourceUrl = oldFormatHeader['url']
            if 'path to text file' in oldFormatHeader:
                textLocation = oldFormatHeader['path to text file']
            else:
                textLocation = None
        except KeyError:
            raise KeyError("'type', 'title', 'date', 'url' is required, "
                           "only 'path to file' is optional")
        return Header(docID, docType, title, date, sourceUrl, textLocation)


class DuplicateHeader(DocumentHeader):
    """
    You must specify either argument 'id' only or
    all arguments except optional 'textLocation'
    """
    def __init__(self, id, docType=None, title=None, date=None, sourceUrl=None,
                 textLocation=None):
        super().__init__(id)
        if (docType is None and title is None and date is None and
                sourceUrl is None and textLocation is None):
            self.header_list = []
        elif (docType is not None and title is not None and
              date is not None and sourceUrl is not None):
            self.header_list = [Header(id, docType, title,
                                date, sourceUrl, textLocation)]
        else:
            raise ValueError("You must specify either argument 'id' only or "
                             "all arguments except optional 'textLocation'")

    def __eq__(self, other):
        return (super().__eq__(other) and
                (collections.Counter(self.header_list) ==
                collections.Counter(other.header_list)))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return super().__hash__()

    def append(self, docType, title, date, sourceUrl,
               textLocation=None):
        h = Header(self.id, docType, title, date, sourceUrl,
                   textLocation)
        if h not in self.header_list:
            self.header_list.append(h)

    def convert_to_dict(self):
        dhList = []
        for dupHeader in self.header_list:
            dh = {
                'type':  dupHeader.document_type,
                'title':  dupHeader.title,
                'date':  dupHeader.date.strftime('%d.%m.%Y'),
                'url':  dupHeader.source_url
                }
            if dupHeader.text_location is not None:
                dh['path to text file'] = dupHeader.text_location
            dhList.append(dh)
        return ('not unique', dhList)

    @staticmethod
    def convert_from_dict(key: str, oldFormatHeader: dict):
        docID = key
        duplicateHeader = DuplicateHeader(docID)
        try:
            for dh in oldFormatHeader[1]:
                docType = dh['type']
                title = dh['title']
                date = dateutil.parser.parse(dh['date'],
                                             dayfirst=True).date()
                sourceUrl = dh['url']
                if 'path to text file' in dh:
                    textLocation = dh['path to text file']
                else:
                    textLocation = None
                duplicateHeader.append(docType, title, date,
                                       sourceUrl, textLocation)
        except KeyError:
            raise KeyError("'type', 'title', 'date', 'url' is required, "
                           "only 'path to file' is optional")
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


class HeadersFilter():
    """
    Arguments contains conditions for which headers will be selected.\n
    firstDate and lastDate: instances of datetime.date
    """
    def __init__(self, docTypes=None, firstDate=datetime.date.min,
                 lastDate=datetime.date.max):

        if hasattr(docTypes, '__iter__'):
            self.doc_types = set(docTypes)
        else:
            self.doc_types = None
        if isinstance(firstDate, datetime.date):
            self.first_date = firstDate
        else:
            raise TypeError("Variable 'firstDate' is not instance "
                            "of datetime.date")

        if isinstance(lastDate, datetime.date):
            self.last_date = lastDate
        else:
            raise TypeError("Variable 'lastDate' is not instance "
                            "of datetime.date")

    def __eq__(self, other):
        return (self.doc_types == other.doc_types and
                self.first_date == other.first_date and
                self.last_date == other.last_date)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(tuple([hash(tuple(self.doc_types)),
                           hash(self.first_date),
                           hash(self.last_date)]))

    def check_header(self, header):
        if ((self.doc_types is None or
             header.document_type in self.doc_types) and
                self.first_date <= header.date <= self.last_date):
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
    def __init__(self, docTypes=None, firstDate=datetime.date.min,
                 lastDate=datetime.date.max, indegreeRange=None,
                 outdegreeRange=None):
        super().__init__(docTypes, firstDate, lastDate)
        self.indegree_range = indegreeRange
        self.outdegree_range = outdegreeRange

    def __eq__(self, other):
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
        if True:  # DEBUG
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
            i = 0  # debug
            L = len(self.nodes)  # debug
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
                i += 1  # debug
                print(f'Проверили вершину {i}/{L}')  # debug
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
        return list(v.id for v in self.nodes)

    def get_edges_as_list_of_tuples(self):
        return list((e.header_from.id, e.header_to.id, e.citations_number)
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
