import datetime


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
    def __init__(self, id, document_type, title, date, source_url,
                 text_location=None):
        DocumentHeader.__init__(self, id)
        self.document_type = document_type
        self.title = title
        if isinstance(date, datetime.date):
            self.date = date
        else:
            raise TypeError("Variable 'date' is not instance of datetime.date")
        self.source_url = source_url
        self.text_location = text_location

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
    def __init__(self, id, document_type, title, date, source_url,
                 text_location=None):
        DocumentHeader.__init__(self, id)
        self.header_list = [Header(id, document_type, title,
                            date, source_url, text_location=None)]

    def __eq__(self, other):
        return (DocumentHeader.__eq__(self, other) and
                set(self.header_list) == set(other.header_list))

    def __ne__(self, other):
        return (not DocumentHeader.__eq__(self, other) or
                not set(self.header_list) == set(other.header_list))

    def __hash__(self):
        return DocumentHeader.__hash__(self)

    def append(self, document_type, title, date, source_url,
               text_location=None):
        h = Header(self.id, document_type, title, date, source_url,
                   text_location)
        if h not in self.header_list:
            self.header_list.append(h)


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
    print(h3 == h2)
    print(h2 != h3)
    input('press any key...')
