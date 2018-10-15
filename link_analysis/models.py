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
    pass


class HeadersFilter():
    """
    Arguments contains conditions for which headers will be selected.
    """
    def __init__(self, docTypes, firstDate, lastDate):
        if isinstance(docTypes, set):
            self.doc_types = docTypes
        elif isinstance(docTypes, list):
            self.doc_types = set(docTypes)
        else:
            self.doc_types = {docTypes}
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

    def check_header(self, header):
        if (header.document_type in self.doc_types and
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


class LinkGraph:
    def __init__(self):
        self.vertices = []  # list of Header class instances
        self.edges = []  # list of CleaLink class instances

    def __eq__(self, other):
        return (cllctCntr(self.edges) == cllctCntr(other.edges) and
                cllctCntr(self.vertices) == cllctCntr(other.vertices))

    def __ne__(self, other):
        return (
            not cllctCntr(self.edges) == cllctCntr(other.edges) or
            not cllctCntr(self.vertices) == cllctCntr(other.vertices))

    def __hash__(self):
        sHash = hash(tuple(hash(h) for h in sorted(self.vertices,
                                                   key=lambda x: x.id)))
        sHash += hash(tuple(hash(cl) for cl in sorted(
                                                    self.edges,
                                                    key=lambda x: x.from_id)))
        return sHash

    def add_vertex(self, vertex):
        if not isinstance(vertex, Header):
            raise TypeError("Variable 'vertex' is not instance "
                            "of class Header")
        if vertex not in self.vertices:
            self.vertices.append(vertex)

    def add_edge(self, edge):
        if not isinstance(edge, CleanLink):
            raise TypeError("Variable 'edge' is not instance "
                            "of class CleanLink")
        if edge not in self.edges:
            self.edges.append(edge)

    def get_subgraph(self, headerFilter, edgeFilter):  # stub
        pass

    def get_itearable_lin_graph(self):  # stub
        pass


class IterableLinkGraph(LinkGraph):  # stub
    pass


if __name__ == "__main__":
    date = datetime.date(2018, 12, 11)
    h1 = Header("456-О-О/2018", "КСРФ/О-О", "Заголовк", date,
                "https://goto.ru", "path-to")
    h2 = Header("456-О-О/2018", "КСРФ/О-О", "Заголовк", date,
                "https://goto.ru")
    h3 = Header("456-О-О/2018", "КСРФ/О-О", "Заголовк", date,
                "https://goto.ru")
    h4 = Header("456-О-О/2018", "КСРФ/О-О", "Заголовк", date,
                "https://goto.ru")
    h5 = DuplicateHeader("456-О-О/2018", "КСРФ/О-О", "Заголовк", date,
                         "https://goto.ru")
    h5.append("КСРФ/О-О", "Заголовк", datetime.date(1990, 1, 2),
              "https://goto.ru")
    h6 = DuplicateHeader("456-О-О/2018", "КСРФ/О-О", "Заголовк", date,
                         "https://goto.ru")
    a = LinkGraph()
    b = LinkGraph()
    a.add_vertex(h2)
    b.add_vertex(h3)
    input('press any key...')
