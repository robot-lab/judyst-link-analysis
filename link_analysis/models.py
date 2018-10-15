import datetime
from collections import Counter as cllctCntr


class DocumentHeader:
    def __init__(self, id):
        self.id = id

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self.id == other.id

    def __hash__(self):
        return hash(self.id)


class Header(DocumentHeader):
    def __init__(self, id, docType, title, date, sourceUrl,
                 textLocation=None):
        DocumentHeader.__init__(self, id)
        self.document_type = docType
        self.title = title
        if isinstance(date, datetime.date):
            self.date = date
        else:
            raise TypeError("Variable 'date' is not instance of datetime.date")
        self.source_url = sourceUrl
        self.text_location = textLocation

    def __eq__(self, other):
        return (DocumentHeader.__eq__(self, other) and
                self.document_type == other.document_type and
                self.title == other.title and
                self.date == other.date and
                self.source_url == other.source_url and
                self.text_location == other.text_location)

    def __ne__(self, other):
        return (not DocumentHeader.__eq__(self, other) or
                not self.document_type == other.document_type or
                not self.title == other.title or
                not self.date == other.date or
                not self.source_url == other.source_url or
                not self.text_location == other.text_location)

    def __hash__(self):
        return DocumentHeader.__hash__(self)


class DuplicateHeader(DocumentHeader):
    def __init__(self, id, docType, title, date, sourceUrl,
                 textLocation=None):
        DocumentHeader.__init__(self, id)
        self.header_list = [Header(id, docType, title,
                            date, sourceUrl, textLocation=None)]

    def __eq__(self, other):
        return (
            DocumentHeader.__eq__(self, other) and
            cllctCntr(self.header_list) == cllctCntr(other.header_list))

    def __ne__(self, other):
        return (
            not DocumentHeader.__eq__(self, other) or
            not cllctCntr(self.header_list) == cllctCntr(other.header_list))

    def __hash__(self):
        return DocumentHeader.__hash__(self)

    def append(self, docType, title, date, sourceUrl,
               textLocation=None):
        h = Header(self.id, docType, title, date, sourceUrl,
                   textLocation)
        if h not in self.header_list:
            self.header_list.append(h)


class Link:  # stub
    def __init__(self, fromID):
        self.from_id = fromID


class RoughLink(Link):  # stub
    pass


class CleanLink(Link):  # stub
    def __init__(self, headerFrom, headerTo, citationsNumber):
        self.header_from = headerFrom
        self.header_to = headerTo
        self.citations_number = citationsNumber

    def __hash__(self):
        return hash(tuple(hash(self.header_from), hash(self.header_to)))


class HeadersFilter():
    """
    Arguments contains conditions for which headers will be selected.\n
    firstDate and lastDate: ints that together implements
    line segment [int, int]\n
    """
    def __init__(self, docTypes=None, firstDate=None, lastDate=None):

        if docTypes is not None:
            if isinstance(docTypes, set):
                self.doc_types = docTypes
            elif isinstance(docTypes, list):
                self.doc_types = set(docTypes)
            else:
                self.doc_types = {docTypes}

        if firstDate is not None:
            if isinstance(firstDate, datetime.date):
                self.first_date = firstDate
            else:
                raise TypeError("Variable 'firstDate' is not instance "
                                "of datetime.date")
        else:
            self.first_date = datetime.date.min

        if lastDate is not None:
            if isinstance(lastDate, datetime.date):
                self.last_date = lastDate
            else:
                raise TypeError("Variable 'lastDate' is not instance "
                                "of datetime.date")
        else:
            self.last_date = datetime.date.max

    def check_header(self, header):
        if ((self.doc_types is None or
             header.document_type in self.doc_types) and
                self.first_date <= header.date <= self.last_date):
            return True
        else:
            return False

    def get_filtered_headers(self, headersDic):
        resultDict = {}
        for key in headersDic:
            if self.check_header(headersDic[key]):
                resultDict[key] = headersDic[key]
        return resultDict


class GraphVerticesFilter(HeadersFilter):
    """
    Arguments contains conditions for which vertices will be selected.\n
    firstDate and lastDate: ints that together implements
    line segment [int, int]\n
    indegreeBetweenNums and outdegreeBetweenNums: tuples that implements
    own line segment [int, int]
    """
    def __init__(self, docTypes=None, firstDate=None, lastDate=None,
                 indegreeBetweenNums=None, outdegreeBetweenNums=None):
        HeadersFilter.__init__(self, docTypes, firstDate, lastDate)
        self.indegree_between_nums = indegreeBetweenNums
        self.outdegree_between_nums = outdegreeBetweenNums


class GraphEdgesFilter():
    """
    Arguments contains conditions for which edges will be selected.\n
    weightsBetween: tuple that implements line segment [int, int]
    """
    def __init__(self, headersFilterFrom=None, headerFilterTo=None,
                 weightsBetween=None):
        self.headers_filter_from = headersFilterFrom
        self.headers_filter_to = headerFilterTo
        self.weights_between = weightsBetween

    def check_edge(self, edge):
        """edge: class CleanLink"""
        if ((self.headers_filter_from is None or
             self.headers_filter_from.check_header(edge.header_from)
             ) and
            (self.headers_filter_to is None or
             self.headers_filter_to.check_header(edge.header_to)
             ) and
            (self.weights_between is None or (self.weights_between[0] <=
             edge.citations_number <= self.weights_between[1]))):
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
    self.vertices: set of Header class instances\n
    self.edges: set of CleanLink class instances
    """
    def __init__(self):
        self.vertices = set()
        self.edges = set()

    def __eq__(self, other):
        return (self.vertices == other.vertices and
                self.edges == other.edges)

    def __ne__(self, other):
        return (not self.vertices == other.vertices or
                not self.edges == other.edges)

    def __hash__(self):
        import time  # DEBUG
        start_time = time.time()  # DEBUG
        vHash = hash(tuple(sorted(self.vertices, key=lambda h: hash(h))))
        eHash = hash(tuple(sorted(self.edges, key=lambda e: hash(e))))
        # It will be interesting to know:
        if True:  # DEBUG
            raise Exception('We finally needed the graph hash. It takes '
                            f'{time.time()-start_time} seconds')  # DEBUG
        return hash(tuple(vHash, eHash))

    def add_vertex(self, vertex):
        if not isinstance(vertex, Header):
            raise TypeError("Variable 'vertex' is not instance "
                            "of class Header")
        self.vertices.add(vertex)

    def add_edge(self, edge):
        if not isinstance(edge, CleanLink):
            raise TypeError("Variable 'edge' is not instance "
                            "of class CleanLink")
        self.edges.add(edge)

    def get_vertex_degrees(self, vertex):
        """
        vertex: class Header\n
        returns tuple degrees=(indegree, outdegree)
        """
        indegree = 0
        outdegree = 0
        for edge in self.edges:
            if hash(edge.header_from) == hash(vertex):
                outdegree += 1
            if hash(edge.header_to) == hash(vertex):
                indegree += 1
        return (indegree, outdegree)

    def get_subgraph(self, verticesFilter=None, edgesFilter=None):  # stub
        subgraph = LinkGraph()
        if verticesFilter is not None:
            if not isinstance(verticesFilter, GraphVerticesFilter):
                raise TypeError("Variable 'verticesFilter' is not instance "
                                "of class GraphVerticesFilter")
            for vertex in self.vertices:
                indegreeEggs = False
                outdegreeEggs = False
                restEggs = False
                if (verticesFilter.indegree_between_nums is not None or
                        verticesFilter.outdegree_between_nums is not None):
                    degrees = self.get_vertex_degrees(vertex)
                if (verticesFilter.indegree_between_nums is None or
                   (verticesFilter.indegree_between_nums[0] <= degrees[0] <=
                        verticesFilter.indegree_between_nums[1])):
                    indegreeEggs = True
                if (verticesFilter.outdegree_between_nums is None or
                   (verticesFilter.outdegree_between_nums[0] <= degrees[1] <=
                        verticesFilter.outdegree_between_nums[1])):
                    outdegreeEggs = True
                if verticesFilter.check_header(vertex):
                    restEggs = True
                if (indegreeEggs and outdegreeEggs and restEggs):
                    subgraph.vertices.add(vertex)
        else:
            subgraph.vertices = self.vertices.copy()
        if edgesFilter is not None:
            if not isinstance(edgesFilter, GraphEdgesFilter):
                raise TypeError("Variable 'edgesFilter' is not instance "
                                "of class GraphEdgesFilter")
            for edge in self.edges:
                if (edge.header_from in subgraph.vertices and
                    edge.header_to in subgraph.vertices and
                        edgesFilter.check_edge(edge)):
                    subgraph.edges.add(edge)
        else:
            for edge in self.edges:
                if (edge.header_from in subgraph.vertices and
                        edge.header_to in subgraph.vertices):
                    subgraph.edges.add(edge)
        return subgraph

    def get_itearable_link_graph(self):  # stub
        pass


class IterableLinkGraph(LinkGraph):  # stub
    pass


if __name__ == "__main__":
    # date = datetime.date(2018, 12, 11)
    # h1 = Header("456-О-О/2018", "КСРФ/О-О", "Заголовк", date,
    #             "https://goto.ru", "path-to")
    # h2 = Header("456-О-О/2018", "КСРФ/О-О", "Заголовк", date,
    #             "https://goto.ru")
    # h3 = Header("456-О-О/2018", "КСРФ/О-О", "Заголовк", date,
    #             "https://goto.ru")
    # h4 = Header("456-О-О/2018", "КСРФ/О-О", "Заголовк", date,
    #             "https://goto.ru")
    # h5 = DuplicateHeader("456-О-О/2018", "КСРФ/О-О", "Заголовк", date,
    #                      "https://goto.ru")
    # h5.append("КСРФ/О-О", "Заголовк", datetime.date(1990, 1, 2),
    #           "https://goto.ru")
    # h6 = DuplicateHeader("456-О-О/2018", "КСРФ/О-О", "Заголовк", date,
    #                      "https://goto.ru")
    # a = LinkGraph()
    # b = LinkGraph()
    # a.add_vertex(h2)
    # b.add_vertex(h3)
    A = LinkGraph()
    # B = {A:1}
    input('press any key...')
