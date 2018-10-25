import datetime
import collections
import unittest
from models import DocumentHeader, Header, DuplicateHeader, Link, RoughLink
from models import CleanLink, HeadersFilter, GraphNodesFilter, GraphEdgesFilter
from models import LinkGraph


class DocumentHeaderTestCase(unittest.TestCase):
    def setUp(self):
        self.header1 = DocumentHeader(r'КСРФ/31-П/2018')
        self.header2 = DocumentHeader(r'КСРФ/31-П/2018')
        self.header3 = DocumentHeader(r'КСРФ/30-П/2018')

    def testCreateWithCorrectArguments(self):
        try:
            self.header4 = DocumentHeader(r'КСРФ/31-П/2018')
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testCreateWithIncorrectArguments(self):
        try:
            self.header4 = DocumentHeader(True)
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertFalse(TestStatus)

    def testEqWithEqualClasses(self):
        TestStatus = self.header1 == self.header2
        self.assertTrue(TestStatus)

    def testEqWithUnequalClasses(self):
        TestStatus = self.header1 == self.header3
        self.assertFalse(TestStatus)

    def testNeWithUnequalClasses(self):
        TestStatus = self.header1 != self.header2
        self.assertFalse(TestStatus)

    def testNeWithEqualClasses(self):
        TestStatus = self.header1 != self.header3
        self.assertTrue(TestStatus)

    def testHashWithSameClasses(self):
        HeaderList = []
        i = 0
        while i < 100:
            i += 1
            HeaderList.append(DocumentHeader(r'КСРФ/32-П/2018'))
        TestStatus = True
        for header in HeaderList:
            if header.__hash__ != HeaderList[0].__hash__:
                TestStatus = False
        self.assertTrue(TestStatus)

    def testHashWithDifferentClasses(self):
        HeaderList = []
        i = 0
        while i < 100:
            i += 1
            HeaderList.append(DocumentHeader(r'КСРФ/'+str(i)+r'-П/2018'))
        HeaderList = [header.__hash__() for header in HeaderList]
        TestStatus = True
        for header in HeaderList:
            if HeaderList.count(header) != 1:
                TestStatus = False
        self.assertTrue(TestStatus)


class HeaderTestCase(unittest.TestCase):
    def setUp(self):
        self.header1 = Header(
            r'КСРФ/31-П/2018', r'КСРФ/П', 'privet',
            datetime.date(2018, 10, 16),
            r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf')
        self.header2 = Header(
            r'КСРФ/31-П/2018', r'КСРФ/П', 'privet',
            datetime.date(2018, 10, 16),
            r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf')
        self.header3 = Header(
            r'КСРФ/30-О/2018', r'КСРФ/О', 'zdarova',
            datetime.date(2018, 9, 27),
            r'http://doc.ksrf.ru/decision/KSRFDecision357727.pdf')

    def testCreateWithCorrectArguments(self):
        try:
            self.header4 = Header(
                r'КСРФ/30-О/2018', r'КСРФ/О', 'zdarova',
                datetime.date(2018, 9, 27),
                r'http://doc.ksrf.ru/decision/KSRFDecision357727.pdf')
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testCreateWithIncorrectArguments(self):
        try:
            self.header4 = Header(
                r'КСРФ/30-О/2018', 12, False,
                datetime.date(2018, 9, 27),
                r'http://doc.ksrf.ru/decision/KSRFDecision357727.pdf')
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertFalse(TestStatus)

    def testEqWithEqualClasses(self):
        TestStatus = self.header1 == self.header2
        self.assertTrue(TestStatus)

    def testEqWithUnequalClasses(self):
        TestStatus = self.header1 == self.header3
        self.assertFalse(TestStatus)

    def testNeWithUnequalClasses(self):
        TestStatus = self.header1 != self.header2
        self.assertFalse(TestStatus)

    def testNeWithEqualClasses(self):
        TestStatus = self.header1 != self.header3
        self.assertTrue(TestStatus)

    def testHashWithSameClasses(self):
        HeaderList = []
        i = 0
        while i < 100:
            i += 1
            HeaderList.append(
                Header(r'КСРФ/32-П/2018', r'КСРФ/П', 'privet',
                       datetime.date(2018, 10, 16),
                       r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf'))
        TestStatus = True
        for header in HeaderList:
            if header.__hash__ != HeaderList[0].__hash__:
                TestStatus = False
        self.assertTrue(TestStatus)

    def testHashWithDifferentClasses(self):
        HeaderList = []
        i = 0
        while i < 100:
            i += 1
            HeaderList.append(
                Header(r'КСРФ/'+str(i)+r'-П/2018', r'КСРФ/П', 'privet',
                       datetime.date(2018, 10, 16),
                       r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf'))
        HeaderList = [header.__hash__() for header in HeaderList]
        TestStatus = True
        for header in HeaderList:
            if HeaderList.count(header) != 1:
                TestStatus = False
        self.assertTrue(TestStatus)


class DuplicateHeaderTestCase(unittest.TestCase):
    def setUp(self):
        self.header1 = DuplicateHeader(
            r'КСРФ/31-П/2018', r'КСРФ/П', 'privet',
            datetime.date(2018, 10, 16),
            r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf')
        self.header2 = DuplicateHeader(
            r'КСРФ/31-П/2018', r'КСРФ/П', 'privet',
            datetime.date(2018, 10, 16),
            r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf')
        self.header3 = DuplicateHeader(
            r'КСРФ/30-О/2018', r'КСРФ/О', 'zdarova',
            datetime.date(2018, 9, 27),
            r'http://doc.ksrf.ru/decision/KSRFDecision357727.pdf')

    def testCreateWithCorrectArguments(self):
        try:
            self.header4 = DuplicateHeader(
                r'КСРФ/30-О/2018', r'КСРФ/О', 'zdarova',
                datetime.date(2018, 9, 27),
                r'http://doc.ksrf.ru/decision/KSRFDecision357727.pdf')
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testCreateWithIncorrectArguments(self):
        try:
            self.header4 = DuplicateHeader(
                r'КСРФ/30-О/2018', r'КСРФ/О', 1488,
                'datetime.date(2018, 9, 27)',
                r'http://doc.ksrf.ru/decision/KSRFDecision357727.pdf')
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertFalse(TestStatus)

    def testEqWithEqualClasses(self):
        TestStatus = self.header1 == self.header2
        self.assertTrue(TestStatus)

    def testEqWithUnequalClasses(self):
        TestStatus = self.header1 == self.header3
        self.assertFalse(TestStatus)

    def testNeWithUnequalClasses(self):
        TestStatus = self.header1 != self.header2
        self.assertFalse(TestStatus)

    def testNeWithEqualClasses(self):
        TestStatus = self.header1 != self.header3
        self.assertTrue(TestStatus)

    def testHashWithSameClasses(self):
        HeaderList = []
        i = 0
        while i < 100:
            i += 1
            HeaderList.append(
                DuplicateHeader(r'КСРФ/32-П/2018', r'КСРФ/П', 'privet',
                                datetime.date(2018, 10, 16),
                                r'http://doc.ksrf.ru/decision/357646.pdf'))
        TestStatus = True
        for header in HeaderList:
            if header.__hash__ != HeaderList[0].__hash__:
                TestStatus = False
        self.assertTrue(TestStatus)

    def testHashWithDifferentClasses(self):
        HeaderList = []
        i = 0
        while i < 100:
            i += 1
            HeaderList.append(
                DuplicateHeader(r'КСРФ/'+str(i)+r'-П/2018',
                                r'КСРФ/П', 'privet',
                                datetime.date(2018, 10, 16),
                                r'http://doc.ksrf.ru/decision/357646.pdf'))
        HeaderList = [header.__hash__() for header in HeaderList]
        TestStatus = True
        for header in HeaderList:
            if HeaderList.count(header) != 1:
                TestStatus = False
        self.assertTrue(TestStatus)


class LinkTestCase(unittest.TestCase):
    def setUp(self):
        self.link1 = Link(
            Header(r'КСРФ/31-П/2018', r'КСРФ/П', 'privet',
                   datetime.date(2018, 10, 16),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf'))
        self.link2 = Link(
            Header(r'КСРФ/31-П/2018', r'КСРФ/П', 'privet',
                   datetime.date(2018, 10, 16),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf'))
        self.link3 = Link(
            Header(r'КСРФ/30-О/2018', r'КСРФ/О', 'zdarova',
                   datetime.date(2018, 9, 27),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357727.pdf'))

    def testCreateWithCorrectArguments(self):
        try:
            self.link4 = Link(
                Header(r'КСРФ/30-О/2018', r'КСРФ/О', 'zdarova',
                       datetime.date(2018, 9, 27),
                       r'http://doc.ksrf.ru/decision'
                       f'/KSRFDecision357727.pdf'))
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testCreateWithIncorrectArguments(self):
        try:
            self.link4 = Link(
                Header(True, r'КСРФ/О', 'zdarova',
                       datetime.date(2018, 9, 27),
                       322))
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertFalse(TestStatus)

    def testEqWithEqualClasses(self):
        TestStatus = self.link1 == self.link2
        self.assertTrue(TestStatus)

    def testEqWithUnequalClasses(self):
        TestStatus = self.link1 == self.link3
        self.assertFalse(TestStatus)

    def testNeWithUnequalClasses(self):
        TestStatus = self.link1 != self.link2
        self.assertFalse(TestStatus)

    def testNeWithEqualClasses(self):
        TestStatus = self.link1 != self.link3
        self.assertTrue(TestStatus)

    def testHashWithSameClasses(self):
        LinkList = []
        i = 0
        while i < 100:
            i += 1
            LinkList.append(
                Link(Header(r'КСРФ/32-П/2018', r'КСРФ/П', 'privet',
                            datetime.date(2018, 10, 16),
                            r'http://doc.ksrf.ru/decision/357646.pdf')))
        TestStatus = True
        for link in LinkList:
            if link.__hash__ != LinkList[0].__hash__:
                TestStatus = False
        self.assertTrue(TestStatus)

    def testHashWithDifferentClasses(self):
        LinkList = []
        i = 0
        while i < 100:
            i += 1
            LinkList.append(
                Link(Header(r'КСРФ/'+str(i)+r'-П/2018',
                            r'КСРФ/П', 'privet',
                            datetime.date(2018, 10, 16),
                            r'http://doc.ksrf.ru/decision/357646.pdf')))
        LinkList = [link.__hash__() for link in LinkList]
        TestStatus = True
        for link in LinkList:
            if LinkList.count(link) != 1:
                TestStatus = False
        self.assertTrue(TestStatus)


class RoughLinkTestCase(unittest.TestCase):
    def setUp(self):
        self.link1 = RoughLink(
            Header(r'КСРФ/31-П/2018', r'КСРФ/П', 'privet',
                   datetime.date(2018, 10, 16),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf)'),
            'от 1 мая 2018 года № 31-П', 'постановление', 31)
        self.link2 = RoughLink(
            Header(r'КСРФ/31-П/2018', r'КСРФ/П', 'privet',
                   datetime.date(2018, 10, 16),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf)'),
            'от 1 мая 2018 года № 31-П', 'постановление', 31)
        self.link3 = RoughLink(
            Header(r'КСРФ/30-О/2018', r'КСРФ/О', 'zdarova',
                   datetime.date(2018, 9, 27),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357727.pdf'),
            'от 2 мая 2018 года № 30-О', 'определение', 30)

    def testCreateWithCorrectArguments(self):
        try:
            self.link4 = RoughLink(
                Header(r'КСРФ/30-О/2018', r'КСРФ/О', 'zdarova',
                       datetime.date(2018, 9, 27),
                       r'http://doc.ksrf.ru/decision/KSRFDecision357727.pdf'),
                'от 2 мая 2018 года № 30-О', 'определение', 30)
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testCreateWithIncorrectArguments(self):
        try:
            self.link4 = RoughLink(
                'Header',
                'от 2 мая 2018 года № 30-О', 'определение', 30)
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertFalse(TestStatus)

    def testEqWithEqualClasses(self):
        TestStatus = self.link1 == self.link2
        self.assertTrue(TestStatus)

    def testEqWithUnequalClasses(self):
        TestStatus = self.link1 == self.link3
        self.assertFalse(TestStatus)

    def testNeWithUnequalClasses(self):
        TestStatus = self.link1 != self.link2
        self.assertFalse(TestStatus)

    def testNeWithEqualClasses(self):
        TestStatus = self.link1 != self.link3
        self.assertTrue(TestStatus)

    def testHashWithSameClasses(self):
        LinkList = []
        i = 0
        while i < 100:
            i += 1
            LinkList.append(RoughLink(
                Header(r'КСРФ/32-П/2018', r'КСРФ/П', 'privet',
                       datetime.date(2018, 10, 16),
                       r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf'),
                'от 3 мая 2018 года № 32-П', 'постановление', 32))
        TestStatus = True
        for link in LinkList:
            if link.__hash__ != LinkList[0].__hash__:
                TestStatus = False
        self.assertTrue(TestStatus)

    def testHashWithDifferentClasses(self):
        LinkList = []
        i = 0
        while i < 100:
            i += 1
            LinkList.append(RoughLink(
                Header(r'КСРФ/'+str(i)+r'-П/2018',
                       r'КСРФ/П', 'privet',
                       datetime.date(2018, 10, 16),
                       r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf'),
                'от 3 мая 2018 года № 32-П', 'постановление', 32))
        LinkList = [link.__hash__() for link in LinkList]
        TestStatus = True
        for link in LinkList:
            if LinkList.count(link) != 1:
                TestStatus = False
        self.assertTrue(TestStatus)


class CleanLinkTestCase(unittest.TestCase):
    def setUp(self):
        self.link1 = CleanLink(
            Header(r'КСРФ/31-П/2018', r'КСРФ/П', 'privet',
                   datetime.date(2018, 10, 16),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf)'),
            Header(r'КСРФ/32-П/2018', r'КСРФ/П', 'poka',
                   datetime.date(2018, 10, 17),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357647.pdf)'),
            31, (31, 'постановление'))
        self.link2 = CleanLink(
            Header(r'КСРФ/31-П/2018', r'КСРФ/П', 'privet',
                   datetime.date(2018, 10, 16),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf)'),
            Header(r'КСРФ/32-П/2018', r'КСРФ/П', 'poka',
                   datetime.date(2018, 10, 17),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357647.pdf)'),
            31, (31, 'постановление'))
        self.link3 = CleanLink(
            Header(r'КСРФ/30-О/2018', r'КСРФ/О', 'zdarova',
                   datetime.date(2018, 9, 27),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357727.pdf'),
            Header(r'КСРФ/31-О/2018', r'КСРФ/О', 'uvidimsya',
                   datetime.date(2018, 9, 28),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357728.pdf'),
            30, (30, 'определение'))

    def testCreateWithCorrectArguments(self):
        try:
            self.link4 = CleanLink(
                Header(r'КСРФ/30-О/2018', r'КСРФ/О', 'zdarova',
                       datetime.date(2018, 9, 27),
                       r'http://doc.ksrf.ru/decision/KSRFDecision357727.pdf'),
                Header(r'КСРФ/31-О/2018', r'КСРФ/О', 'uvidimsya',
                       datetime.date(2018, 9, 28),
                       r'http://doc.ksrf.ru/decision/KSRFDecision357728.pdf'),
                30, (30, 'определение'))
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testCreateWithIncorrectArguments(self):
        try:
            self.link4 = CleanLink(
                Header(r'КСРФ/30-О/2018', 228, 'zdarova',
                       datetime.date(2018, 9, 27),
                       r'http://doc.ksrf.ru/decision/KSRFDecision357727.pdf'),
                Header(r'КСРФ/31-О/2018', r'КСРФ/О', 'uvidimsya',
                       'datetime.date(2018, 9, 28)',
                       r'http://doc.ksrf.ru/decision/KSRFDecision357728.pdf'),
                '30', (30, 'определение'))
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertFalse(TestStatus)

    def testEqWithEqualClasses(self):
        TestStatus = self.link1 == self.link2
        self.assertTrue(TestStatus)

    def testEqWithUnequalClasses(self):
        TestStatus = self.link1 == self.link3
        self.assertFalse(TestStatus)

    def testNeWithUnequalClasses(self):
        TestStatus = self.link1 != self.link2
        self.assertFalse(TestStatus)

    def testNeWithEqualClasses(self):
        TestStatus = self.link1 != self.link3
        self.assertTrue(TestStatus)

    def testHashWithSameClasses(self):
        LinkList = []
        i = 0
        while i < 100:
            i += 1
            LinkList.append(CleanLink(
                Header(r'КСРФ/32-П/2018', r'КСРФ/П', 'privet',
                       datetime.date(2018, 10, 16),
                       r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf'),
                Header(r'КСРФ/33-П/2018', r'КСРФ/П', 'poka',
                       datetime.date(2018, 10, 17),
                       r'http://doc.ksrf.ru/decision/KSRFDecision357647.pdf'),
                32, (32, 'постановление')))
        TestStatus = True
        for link in LinkList:
            if link.__hash__ != LinkList[0].__hash__:
                TestStatus = False
        self.assertTrue(TestStatus)

    def testHashWithDifferentClasses(self):
        LinkList = []
        i = 0
        while i < 100:
            i += 1
            LinkList.append(CleanLink(
                Header(r'КСРФ/'+str(i)+r'-П/2018',
                       r'КСРФ/П', 'privet',
                       datetime.date(2018, 10, 16),
                       r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf'),
                Header(r'КСРФ/'+str(i+100)+r'-П/2018',
                       r'КСРФ/П', 'poka',
                       datetime.date(2018, 10, 17),
                       r'http://doc.ksrf.ru/decision/KSRFDecision357647.pdf'),
                32, (32, 'постановление')))
        LinkList = [link.__hash__() for link in LinkList]
        TestStatus = True
        for link in LinkList:
            if LinkList.count(link) != 1:
                TestStatus = False
        self.assertTrue(TestStatus)


class HeadersFilterTestCase(unittest.TestCase):
    def setUp(self):
        self.header1 = HeadersFilter(r'КСРФ/П', datetime.date(2018, 10, 16),
                                     datetime.date(2018, 10, 17))
        self.header2 = HeadersFilter(r'КСРФ/П', datetime.date(2018, 10, 16),
                                     datetime.date(2018, 10, 17))
        self.header3 = HeadersFilter(r'КСРФ/О', datetime.date(2018, 9, 27),
                                     datetime.date(2018, 9, 28))

    def testCreateWithCorrectArguments(self):
        try:
            self.header4 = HeadersFilter(r'КСРФ/О',
                                         datetime.date(2018, 9, 27),
                                         datetime.date(2018, 9, 28))
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testCreateWithIncorrectArguments(self):
        try:
            self.header4 = HeadersFilter(r'КСРФ/О',
                                         True,
                                         datetime.date(2018, 9, 28))
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertFalse(TestStatus)

    def testEqWithEqualClasses(self):
        TestStatus = self.header1 == self.header2
        self.assertTrue(TestStatus)

    def testEqWithUnequalClasses(self):
        TestStatus = self.header1 == self.header3
        self.assertFalse(TestStatus)

    def testNeWithUnequalClasses(self):
        TestStatus = self.header1 != self.header2
        self.assertFalse(TestStatus)

    def testNeWithEqualClasses(self):
        TestStatus = self.header1 != self.header3
        self.assertTrue(TestStatus)

    def testHashWithSameClasses(self):
        HeaderList = []
        i = 0
        while i < 100:
            i += 1
            HeaderList.append(HeadersFilter(r'КСРФ/П',
                                            datetime.date(2018, 10, 16),
                                            datetime.date(2018, 10, 17)))
        TestStatus = True
        for header in HeaderList:
            if header.__hash__ != HeaderList[0].__hash__:
                TestStatus = False
        self.assertTrue(TestStatus)

    def testHashWithDifferentClasses(self):
        HeaderList = []
        i = 0
        while i < 100:
            i += 1
            HeaderList.append(HeadersFilter(r'КСРФ/П'+str(i),
                                            datetime.date(i, 10, 16),
                                            datetime.date(i, 10, 17)))
        HeaderList = [header.__hash__() for header in HeaderList]
        TestStatus = True
        for header in HeaderList:
            if HeaderList.count(header) != 1:
                TestStatus = False
        self.assertTrue(TestStatus)

    def testGetFilteredHeadersWithNotEmptyFilter(self):
        HeadersDict = {r'КСРФ/31-П/2018': Header(
            r'КСРФ/31-П/2018', r'КСРФ/П', 'privet',
            datetime.date(2018, 10, 16),
            r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf')}
        TestStatus = True
        if self.header1.get_filtered_headers(HeadersDict) is None:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testGetFilteredHeadersWithEmptyFilter(self):
        HeadersDict = {r'КСРФ/31-П/2018': Header(
            r'КСРФ/31-П/2018', r'КСРФ/П', 'privet',
            datetime.date(2018, 10, 16),
            r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf')}
        TestStatus = True
        self.header4 = HeadersFilter()
        if self.header4.get_filtered_headers(HeadersDict) is None:
            TestStatus = False
        self.assertTrue(TestStatus)


class GraphNodesFilterTestCase(unittest.TestCase):
    def setUp(self):
        self.node1 = GraphNodesFilter(r'КСРФ/П', datetime.date(2018, 10, 16),
                                      datetime.date(2018, 10, 17),
                                      (0, 31), (32, 60))
        self.node2 = GraphNodesFilter(r'КСРФ/П', datetime.date(2018, 10, 16),
                                      datetime.date(2018, 10, 17),
                                      (0, 31), (32, 60))
        self.node3 = GraphNodesFilter(r'КСРФ/О', datetime.date(2018, 9, 27),
                                      datetime.date(2018, 9, 28),
                                      (0, 30), (31, 60))

    def testCreateWithCorrectArguments(self):
        try:
            self.node4 = GraphNodesFilter(r'КСРФ/О',
                                          datetime.date(2018, 9, 27),
                                          datetime.date(2018, 9, 28),
                                          (0, 30), (31, 60))
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testCreateWithIncorrectArguments(self):
        try:
            self.node4 = GraphNodesFilter(r'КСРФ/О',
                                          datetime.date(2018, 9, 27),
                                          datetime.date(2018, 9, 28),
                                          (0, 'lol'), ('proverka', 60))
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertFalse(TestStatus)

    def testEqWithEqualClasses(self):
        TestStatus = self.node1 == self.node2
        self.assertTrue(TestStatus)

    def testEqWithUnequalClasses(self):
        TestStatus = self.node1 == self.node3
        self.assertFalse(TestStatus)

    def testNeWithUnequalClasses(self):
        TestStatus = self.node1 != self.node2
        self.assertFalse(TestStatus)

    def testNeWithEqualClasses(self):
        TestStatus = self.node1 != self.node3
        self.assertTrue(TestStatus)

    def testHashWithSameClasses(self):
        NodeList = []
        i = 0
        while i < 100:
            i += 1
            NodeList.append(GraphNodesFilter(r'КСРФ/П',
                                             datetime.date(2018, 10, 16),
                                             datetime.date(2018, 10, 17),
                                             (0, 32), (33, 60)))
        TestStatus = True
        for node in NodeList:
            if node.__hash__ != NodeList[0].__hash__:
                TestStatus = False
        self.assertTrue(TestStatus)

    def testHashWithDifferentClasses(self):
        NodeList = []
        i = 0
        while i < 100:
            i += 1
            NodeList.append(GraphNodesFilter(r'КСРФ/П'+str(i),
                                             datetime.date(i, 10, 16),
                                             datetime.date(i, 10, 17),
                                             (0, 32), (33, 60)))
        NodeList = [node.__hash__() for node in NodeList]
        TestStatus = True
        for node in NodeList:
            if NodeList.count(node) != 1:
                TestStatus = False
        self.assertTrue(TestStatus)


class GraphEdgesFilterTestCase(unittest.TestCase):
    def setUp(self):
        self.edge1 = GraphEdgesFilter(
            HeadersFilter(r'КСРФ/П', datetime.date(2018, 10, 16),
                          datetime.date(2018, 10, 17)),
            HeadersFilter(r'КСРФ/П-О', datetime.date(2018, 10, 17),
                          datetime.date(2018, 10, 18)),
            (0, 31))
        self.edge2 = GraphEdgesFilter(
            HeadersFilter(r'КСРФ/П', datetime.date(2018, 10, 16),
                          datetime.date(2018, 10, 17)),
            HeadersFilter(r'КСРФ/П-О', datetime.date(2018, 10, 17),
                          datetime.date(2018, 10, 18)),
            (0, 31))
        self.edge3 = GraphEdgesFilter(
            HeadersFilter(r'КСРФ/О', datetime.date(2018, 9, 27),
                          datetime.date(2018, 9, 28)),
            HeadersFilter(r'КСРФ/О-О', datetime.date(2018, 9, 28),
                          datetime.date(2018, 9, 29)),
            (0, 30))

    def testCreateWithCorrectArguments(self):
        try:
            self.edge4 = GraphEdgesFilter(
                HeadersFilter(r'КСРФ/О', datetime.date(2018, 9, 27),
                              datetime.date(2018, 9, 28)),
                HeadersFilter(r'КСРФ/О-О', datetime.date(2018, 9, 28),
                              datetime.date(2018, 9, 29)),
                (0, 30))
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testCreateWithIncorrectArguments(self):
        try:
            self.edge4 = GraphEdgesFilter(
                HeadersFilter(r'КСРФ/О', datetime.date(2018, 9, 27),
                              datetime.date(2018, 9, 28)),
                'HeadersFilter',
                (0, 30))
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertFalse(TestStatus)

    def testEqWithEqualClasses(self):
        TestStatus = self.edge1 == self.edge2
        self.assertTrue(TestStatus)

    def testEqWithUnequalClasses(self):
        TestStatus = self.edge1 == self.edge3
        self.assertFalse(TestStatus)

    def testNeWithUnequalClasses(self):
        TestStatus = self.edge1 != self.edge2
        self.assertFalse(TestStatus)

    def testNeWithEqualClasses(self):
        TestStatus = self.edge1 != self.edge3
        self.assertTrue(TestStatus)

    def testHashWithSameClasses(self):
        EdgeList = []
        i = 0
        while i < 100:
            i += 1
            EdgeList.append(GraphEdgesFilter(
                HeadersFilter(r'КСРФ/П', datetime.date(2018, 10, 16),
                              datetime.date(2018, 10, 17)),
                HeadersFilter(r'КСРФ/П-О', datetime.date(2018, 10, 17),
                              datetime.date(2018, 10, 18)),
                (0, 32)))
        TestStatus = True
        for edge in EdgeList:
            if edge.__hash__ != EdgeList[0].__hash__:
                TestStatus = False
        self.assertTrue(TestStatus)

    def testHashWithDifferentClasses(self):
        EdgeList = []
        i = 0
        while i < 100:
            i += 1
            EdgeList.append(GraphEdgesFilter(
                HeadersFilter(r'КСРФ/П', datetime.date(i, 10, 16),
                              datetime.date(i, 10, 17)),
                HeadersFilter(r'КСРФ/П-О', datetime.date(i, 10, 17),
                              datetime.date(i, 10, 18)),
                (0, i)))
        EdgeList = [edge.__hash__() for edge in EdgeList]
        TestStatus = True
        for edge in EdgeList:
            if EdgeList.count(edge) != 1:
                TestStatus = False
        self.assertTrue(TestStatus)

    def testGetFilteredEdgesWithNotEmptyFilter(self):
        Edges = [CleanLink(
            Header(r'КСРФ/31-П/2018', r'КСРФ/П', 'privet',
                   datetime.date(2018, 10, 16),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf)'),
            Header(r'КСРФ/32-П/2018', r'КСРФ/П', 'poka',
                   datetime.date(2018, 10, 17),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357647.pdf)'),
            31, (31, 'постановление')),
            CleanLink(
            Header(r'КСРФ/30-О/2018', r'КСРФ/О', 'zdarova',
                   datetime.date(2018, 9, 27),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357727.pdf'),
            Header(r'КСРФ/31-О/2018', r'КСРФ/О', 'uvidimsya',
                   datetime.date(2018, 9, 28),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357728.pdf'),
            30, (30, 'определение'))]
        TestStatus = True
        if self.edge1.get_filtered_edges(Edges) is None:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testGetFilteredEdgesWithEmptyFilter(self):
        Edges = [CleanLink(
            Header(r'КСРФ/31-П/2018', r'КСРФ/П', 'privet',
                   datetime.date(2018, 10, 16),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf)'),
            Header(r'КСРФ/32-П/2018', r'КСРФ/П', 'poka',
                   datetime.date(2018, 10, 17),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357647.pdf)'),
            31, (31, 'постановление')),
            CleanLink(
            Header(r'КСРФ/30-О/2018', r'КСРФ/О', 'zdarova',
                   datetime.date(2018, 9, 27),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357727.pdf'),
            Header(r'КСРФ/31-О/2018', r'КСРФ/О', 'uvidimsya',
                   datetime.date(2018, 9, 28),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357728.pdf'),
            30, (30, 'определение'))]
        TestStatus = True
        self.edge4 = GraphEdgesFilter()
        if self.edge4.get_filtered_edges(Edges) is None:
            TestStatus = False
        self.assertTrue(TestStatus)


class LinkGraphTestCase(unittest.TestCase):
    def setUp(self):
        self.graph1 = LinkGraph()
        self.graph1.add_node(
            Header(r'КСРФ/31-П/2018', r'КСРФ/П', 'privet',
                   datetime.date(2018, 10, 16),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf)'))
        self.graph1.add_node(
            Header(r'КСРФ/32-П/2018', r'КСРФ/П', 'poka',
                   datetime.date(2018, 10, 17),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357647.pdf)'))
        self.graph1.add_edge(
            CleanLink(
                Header(r'КСРФ/31-П/2018', r'КСРФ/П', 'privet',
                       datetime.date(2018, 10, 16),
                       r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf)'),
                Header(r'КСРФ/32-П/2018', r'КСРФ/П', 'poka',
                       datetime.date(2018, 10, 17),
                       r'http://doc.ksrf.ru/decision/KSRFDecision357647.pdf)'),
                31, (31, 'постановление')))
        self.graph2 = LinkGraph()
        self.graph2.add_node(
            Header(r'КСРФ/31-П/2018', r'КСРФ/П', 'privet',
                   datetime.date(2018, 10, 16),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf)'))
        self.graph2.add_node(
            Header(r'КСРФ/32-П/2018', r'КСРФ/П', 'poka',
                   datetime.date(2018, 10, 17),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357647.pdf)'))
        self.graph2.add_edge(
            CleanLink(
                Header(r'КСРФ/31-П/2018', r'КСРФ/П', 'privet',
                       datetime.date(2018, 10, 16),
                       r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf)'),
                Header(r'КСРФ/32-П/2018', r'КСРФ/П', 'poka',
                       datetime.date(2018, 10, 17),
                       r'http://doc.ksrf.ru/decision/KSRFDecision357647.pdf)'),
                31, (31, 'постановление')))
        self.graph3 = LinkGraph()
        self.graph3.add_node(
            Header(r'КСРФ/30-О/2018', r'КСРФ/О', 'zdarova',
                   datetime.date(2018, 9, 27),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357727.pdf'))
        self.graph3.add_node(
            Header(r'КСРФ/31-О/2018', r'КСРФ/О', 'uvidimsya',
                   datetime.date(2018, 9, 28),
                   r'http://doc.ksrf.ru/decision/KSRFDecision357728.pdf'))
        self.graph3.add_edge(
            CleanLink(
                Header(r'КСРФ/30-О/2018', r'КСРФ/О', 'zdarova',
                       datetime.date(2018, 9, 27),
                       r'http://doc.ksrf.ru/decision/KSRFDecision357727.pdf'),
                Header(r'КСРФ/31-О/2018', r'КСРФ/О', 'uvidimsya',
                       datetime.date(2018, 9, 28),
                       r'http://doc.ksrf.ru/decision/KSRFDecision357728.pdf'),
                30, (30, 'определение')))

    def testCreateWithCorrectArguments(self):
        try:
            self.graph4 = LinkGraph()
            self.graph4.add_node(
                Header(r'КСРФ/30-О/2018', r'КСРФ/О', 'zdarova',
                       datetime.date(2018, 9, 27),
                       r'http://doc.ksrf.ru/decision/357727.pdf'))
            self.graph4.add_node(
                Header(r'КСРФ/31-О/2018', r'КСРФ/О', 'uvidimsya',
                       datetime.date(2018, 9, 28),
                       r'http://doc.ksrf.ru/decision/357728.pdf'))
            self.graph4.add_edge(
                CleanLink(
                    Header(r'КСРФ/30-О/2018', r'КСРФ/О', 'zdarova',
                           datetime.date(2018, 9, 27),
                           r'http://doc.ksrf.ru/decision/357727.pdf'),
                    Header(r'КСРФ/31-О/2018', r'КСРФ/О', 'uvidimsya',
                           datetime.date(2018, 9, 28),
                           r'http://doc.ksrf.ru/decision/357728.pdf'),
                    30, (30, 'определение')))
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testCreateWithIncorrectArguments(self):
        try:
            self.graph4 = LinkGraph()
            self.graph4.add_node(
                Header(r'КСРФ/30-О/2018', r'КСРФ/О', 'zdarova',
                       datetime.date(2018, 9, 27),
                       r'http://doc.ksrf.ru/decision/357727.pdf'))
            self.graph4.add_node(
                Header(r'КСРФ/31-О/2018', r'КСРФ/О', 14,
                       datetime.date(2018, 9, 28),
                       r'http://doc.ksrf.ru/decision/357728.pdf'))
            self.graph4.add_edge(
                CleanLink(
                    Header(r'КСРФ/30-О/2018', r'КСРФ/О', 'zdarova',
                           datetime.date(2018, 9, 27),
                           r'http://doc.ksrf.ru/decision/357727.pdf'),
                    Header(r'КСРФ/31-О/2018', False, 'uvidimsya',
                           datetime.date(2018, 9, 28),
                           r'http://doc.ksrf.ru/decision/357728.pdf'),
                    30, (30, 322)))
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertFalse(TestStatus)

    def testEqWithEqualClasses(self):
        TestStatus = self.graph1 == self.graph2
        self.assertTrue(TestStatus)

    def testEqWithUnequalClasses(self):
        TestStatus = self.graph1 == self.graph3
        self.assertFalse(TestStatus)

    def testNeWithUnequalClasses(self):
        TestStatus = self.graph1 != self.graph2
        self.assertFalse(TestStatus)

    def testNeWithEqualClasses(self):
        TestStatus = self.graph1 != self.graph3
        self.assertTrue(TestStatus)

    def testHashWithSameClasses(self):
        GraphList = []
        i = 0
        while i < 100:
            i += 1
            self.graph = LinkGraph()
            self.graph.add_node(
                Header(r'КСРФ/32-П/2018', r'КСРФ/П', 'privet',
                       datetime.date(2018, 10, 16),
                       r'http://doc.ksrf.ru/decision/357646.pdf'))
            self.graph.add_node(
                Header(r'КСРФ/33-П/2018', r'КСРФ/П', 'poka',
                       datetime.date(2018, 10, 17),
                       r'http://doc.ksrf.ru/decision/357647.pdf'))
            self.graph.add_edge(
                CleanLink(
                    Header(r'КСРФ/32-П/2018', r'КСРФ/П', 'privet',
                           datetime.date(2018, 10, 16),
                           r'http://doc.ksrf.ru/decision/357646.pdf'),
                    Header(r'КСРФ/33-П/2018', r'КСРФ/П', 'poka',
                           datetime.date(2018, 10, 17),
                           r'http://doc.ksrf.ru/decision/357647.pdf'),
                    32, (32, 'постановление')))
            GraphList.append(self.graph)
        TestStatus = True
        for graph in GraphList:
            if graph.__hash__ != GraphList[0].__hash__:
                TestStatus = False
        self.assertTrue(TestStatus)

    def testHashWithDifferentClasses(self):
        GraphList = []
        i = 0
        while i < 100:
            i += 1
            self.graph = LinkGraph()
            self.graph.add_node(
                Header(r'КСРФ/'+str(i)+r'-П/2018',
                       r'КСРФ/П', 'privet',
                       datetime.date(2018, 10, 16),
                       r'http://doc.ksrf.ru/decision/357646.pdf'))
            self.graph.add_node(
                Header(r'КСРФ/'+str(i+1)+r'-П/2018',
                       r'КСРФ/П', 'poka',
                       datetime.date(2018, 10, 17),
                       r'http://doc.ksrf.ru/decision/357647.pdf'))
            self.graph.add_edge(
                CleanLink(
                    Header(r'КСРФ/'+str(i)+r'-П/2018', r'КСРФ/П', 'privet',
                           datetime.date(2018, 10, 16),
                           r'http://doc.ksrf.ru/decision/357646.pdf'),
                    Header(r'КСРФ/'+str(i+1)+r'-П/2018', r'КСРФ/П', 'poka',
                           datetime.date(2018, 10, 17),
                           r'http://doc.ksrf.ru/decision/357647.pdf'),
                    32, (32, 'постановление')))
            GraphList.append(self.graph)
        HashList = []
        for graph in GraphList:
            HashList.append(self.graph.__hash__())
        TestStatus = True
        for graph in GraphList:
            if GraphList.count(graph) != 1:
                TestStatus = False
        self.assertTrue(TestStatus)


suite = unittest.TestLoader().loadTestsFromTestCase(DocumentHeaderTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
suite = unittest.TestLoader().loadTestsFromTestCase(HeaderTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
suite = unittest.TestLoader().loadTestsFromTestCase(DuplicateHeaderTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
suite = unittest.TestLoader().loadTestsFromTestCase(LinkTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
suite = unittest.TestLoader().loadTestsFromTestCase(RoughLinkTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
suite = unittest.TestLoader().loadTestsFromTestCase(CleanLinkTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
suite = unittest.TestLoader().loadTestsFromTestCase(HeadersFilterTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
suite = unittest.TestLoader().loadTestsFromTestCase(GraphNodesFilterTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
suite = unittest.TestLoader().loadTestsFromTestCase(GraphEdgesFilterTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
suite = unittest.TestLoader().loadTestsFromTestCase(LinkGraphTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    unittest.main()
