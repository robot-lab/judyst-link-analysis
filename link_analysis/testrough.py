import datetime
import collections
import unittest
from models import DocumentHeader, Header, DuplicateHeader, Link, RoughLink
from models import CleanLink, HeadersFilter, GraphNodesFilter, GraphEdgesFilter
from models import LinkGraph


class RoughAnalysisTestCase(unittest.TestCase):
    def setUp(self):
        self.header1 = DocumentHeader(r'КСРФ/31-П/2018')
        self.header2 = DocumentHeader(r'КСРФ/31-П/2018')
        self.header3 = DocumentHeader(r'КСРФ/30-П/2018')

    def testCreate(self):
        try:
            self.header4 = DocumentHeader(True)
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testEq1(self):
        TestStatus = self.header1 == self.header2
        self.assertTrue(TestStatus)

    def testEq2(self):
        TestStatus = self.header1 == self.header3
        self.assertFalse(TestStatus)

    def testNe1(self):
        TestStatus = self.header1 != self.header2
        self.assertFalse(TestStatus)

    def testNe2(self):
        TestStatus = self.header1 != self.header3
        self.assertTrue(TestStatus)

    def testHash1(self):
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

    def testHash2(self):
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