import datetime
import collections
import unittest
from models import DocumentHeader, Header, DuplicateHeader, Link, RoughLink
from models import CleanLink, HeadersFilter, GraphNodesFilter, GraphEdgesFilter
from models import LinkGraph
from rough_analysis import get_rough_links


class RoughAnalysisTestCase(unittest.TestCase):
    def testRough1(self):
        header1 = Header(
            'text1', 'txt', 'text1',
            datetime.date(2018, 10, 24),
            r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf',
            r'C:\\Vs Code Projects\\Python Projects\\link_analysis-project\\Decision files\\test1.txt')
        RoughList = ['от 31 8 октября 23 2007 42 года № 420-О',
                     'от 31 8 октября 23 2007 42 года № 13 421-П',
                     'от 31 8 октября 23 2007 42 года № 422-Р',
                     'от 31 8 октября 23 2007 42 года № 423-О-П']
        TestStatus = True
        BodyList = []
        for roughlink in get_rough_links(header1):
            BodyList.append(roughlink.body)
        if BodyList != RoughList:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testRough2(self):
        header1 = Header(
            'text2', 'txt', 'text2',
            datetime.date(2018, 10, 24),
            r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf',
            r'C:\\Vs Code Projects\\Python Projects\\link_analysis-project\\Decision files\\test2.txt')
        RoughList = ['от 322 16 228 мая 007 1998 1488 года № 1707 80-Л-О-Л-З-А-А-Л-Ь-Я-Н-С']
        TestStatus = True
        BodyList = []
        for roughlink in get_rough_links(header1):
            BodyList.append(roughlink.body)
        if BodyList != RoughList:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testRough3(self):
        header1 = Header(
            'text3', 'txt', 'text3',
            datetime.date(2018, 10, 24),
            r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf',
            r'C:\\Vs Code Projects\\Python Projects\\link_analysis-project\\Decision files\\test3.txt')
        RoughList = ['от 4444 44444444 4444 28 4221 декабря  2111 2019 года № 1111111-J-P-E']
        TestStatus = True
        BodyList = []
        for roughlink in get_rough_links(header1):
            BodyList.append(roughlink.body)
        if BodyList != RoughList:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testRough4(self):
        header1 = Header(
            'text4', 'txt', 'text4',
            datetime.date(2018, 10, 24),
            r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf',
            r'C:\\Vs Code Projects\\Python Projects\\link_analysis-project\\Decision files\\test4.txt')
        RoughList = ['от 23 2 февраля 222 2005 133 года № 18-Г-О',
                     'от 23 2 февраля 222 2005 133 года № 13 19-Ю-S',
                     'от 23 2 февраля 222 2005 133 года № 20-R',
                     'от 23 2 февраля 222 2005 133 года № 21-U-F-C',
                     'от 28 марта 2014 года № 300-О-П']
        TestStatus = True
        BodyList = []
        for roughlink in get_rough_links(header1):
            BodyList.append(roughlink.body)
        if BodyList != RoughList:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testRough5(self):
        header1 = Header(
            'text5', 'txt', 'text5',
            datetime.date(2018, 10, 24),
            r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf',
            r'C:\\Vs Code Projects\\Python Projects\\link_analysis-project\\Decision files\\test5.txt')
        RoughList = ['от 24 декабря 1992 года № 123-А']
        TestStatus = True
        BodyList = []
        for roughlink in get_rough_links(header1):
            BodyList.append(roughlink.body)
        if BodyList != RoughList:
            TestStatus = False
        self.assertTrue(TestStatus)


suite = unittest.TestLoader().loadTestsFromTestCase(RoughAnalysisTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
'''
header1 = Header(
            'text5', 'txt', 'text5',
            datetime.date(2018, 10, 24),
            r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf',
            r'C:\\Vs Code Projects\\Python Projects\\link_analysis-project\\Decision files\\test5.txt')
for roughlink in get_rough_links(header1):
    print(roughlink.body)
'''
