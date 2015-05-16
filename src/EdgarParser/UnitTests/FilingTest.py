'''
Created on May 9, 2015

@author: Keith
'''
import unittest
from EdgarParser.Filing import Filing

class FilingTest(unittest.TestCase):
    test_path = "C:\\Users\\Keith\\Desktop\\Workspace\\Work - Summer 2015\\EDGARParser\\10KMASTER\\Y2009-Y2010\\Filings\\1750\\R20090716-C20090531-F83\\a2193700z10-k.htm"
    filing = Filing(test_path)
    
    def extractCompanyId_Test(self):
        self.filing.companyID = ''
        self.filing.extractCompanyID(self.test_path)
        self.assertNotEqual(self.filing.companyID, '', "Failed to extract company ID")
    
    def extractReportPeriod_Test(self):
        self.filing.reportPeriod = ''
        self.filing.extractReportPeriod(self.test_path)
        self.assertNotEqual(self.filing.reportPeriod, '', "Failed to extract report_period")
    
    def extractFilingText_Test(self):
        self.filing.filingText = ''
        self.filing.extractFilingText(self.test_path)
        self.assertNotEqual(self.filing.filingText, '', "Error Extracting filing_text")
    
    def extractFilingType_Test(self):
        self.filing.filingType = ''
        self.filing.extractFilingType(self.test_path)
        self.assertNotEqual(self.filing.filingType, '', "Error Extracting filing_type")
    
    def findStatementOfCashFlows_Test(self):
        self.filing.statementOfCashFlows = ''
        self.filing.findStatementOfCashFlows()
        self.assertNotEqual(self.filing.statementOfCashFlows, '', "Error Extracting Statement Of Cash Flows")
        
        self.filing.denomination = ''
        self.filing.determineDenomination()
        self.assertNotEqual(self.filing.denomination, '', "Error Extracting Denomination")

        cash_table = self.filing.statementOfCashFlows
        self.filing.cleanUpCashFlowTable()
        self.assertNotEqual(cash_table, self.filing.statementOfCashFlows, "Error Cleaning Up Cash Flow Table")
        
    def createCashFlowDictionary_Test(self):
        self.filing.cashFlowDictionary = ''
        self.filing.createCashFlowDictionary()
        self.assertNotEqual(self.filing.cashFlowDictionary, '', "Error Constructing Cash Flow Dictionary")
        
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()