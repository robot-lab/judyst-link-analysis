import datetime
import collections
import unittest
from models import DocumentHeader, Header, DuplicateHeader, Link, RoughLink
from models import CleanLink, HeadersFilter, GraphNodesFilter, GraphEdgesFilter
from models import LinkGraph
from final_analysis import get_clean_links


class FinalAnalysisTestCase(unittest.TestCase):
    def testClean1(self):
        header1 = Header(
            'text1', 'txt', 'text1',
            datetime.date(2018, 10, 24),
            r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf',
            r'C:\\Vs Code Projects\\Python Projects\\link_analysis-project\\Decision files\\test1.txt')
        RoughList = [
            RoughLink(header1, 'от 31 8 октября 23 2007 42 года № 420-О', 'О', 31),
            RoughLink(header1, 'от 31 8 октября 23 2007 42 года № 13 421-П', 'П', 31),
            RoughLink(header1, 'от 31 8 октября 23 2007 42 года № 422-Р', 'Р', 31),
            RoughLink(header1, 'от 31 8 октября 23 2007 42 года № 423-О-П', 'О-П', 31)]
        CleanList = ['от 8 октября 2007 года № 420-О',
                     'от 8 октября 2007 года № 13 421-П',
                     'от 8 октября 2007 года № 423-О-П']
        DesicionID = 'text1'
        TestStatus = True
        if get_clean_links({header1: RoughList},
                           {DesicionID: header1})[0].get(header1) != CleanList:
            TestStatus = False
        self.assertTrue(TestStatus)

suite = unittest.TestLoader().loadTestsFromTestCase(FinalAnalysisTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
header1 = Header(
    'text1', 'txt', 'text1',
    datetime.date(2018, 10, 24),
    r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf',
    r'C:\\Vs Code Projects\\Python Projects\\link_analysis-project\\Decision files\\test1.txt')
RoughList = [
    RoughLink(header1, 'от 31 8 октября 23 2007 42 года № 420-О', 'О', 89),
    RoughLink(header1, 'от 31 8 октября 23 2007 42 года № 13 421-П', 'П', 48),
    RoughLink(header1, 'от 31 8 октября 23 2007 42 года № 422-Р', 'Р', 48),
    RoughLink(header1, 'от 31 8 октября 23 2007 42 года № 423-О-П', 'О-П', 48)]
DesicionID = 'text1'
print(get_clean_links({header1: RoughList},
                      {DesicionID: header1})[0].get(header1))
