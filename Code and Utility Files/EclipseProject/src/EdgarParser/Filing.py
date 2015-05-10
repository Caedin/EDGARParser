'''
Created on May 8, 2015

@author: Keith
'''
from bs4 import BeautifulSoup
import re

#Compile Search Terms 
noncfterms=re.compile('financial information|statement of income|operating data|balance sheet data|income statement|net revenues|cost of sales|cost of goods sold|selected other financial data|selected financial data|balance sheet data|statement of earnings data|common shares outstanding|other financial data|summary of operations|EBITDA|statement of operating|condensed', re.I)
cfop=re.compile('operating activities|cash flows from operations',re.I)
cfinvest=re.compile('investing activities|cash flows used for investments|investment activities',re.I)
cffin=re.compile('financing activities|cash flows from financing',re.I)
cash=re.compile('net cash provided by|net cash used by|net increase (decrease) in cash|net increase in cash|net decrease in cash|net cash used|net cash from', re.I)
inc=re.compile('income|earnings|loss',re.I)
denomthousands=re.compile('thousands|\'?000\'?s', re.I)
denommillions=re.compile('millions|\'?000,?000\'?s', re.I)

chars = {
    '\xc2\x82' : ',',        # High code comma
    '\xc2\x84' : ',,',       # High code double comma
    '\xc2\x85' : '...',      # Tripple dot
    '\xc2\x88' : '^',        # High carat
    '\xc2\x91' : '\x27',     # Forward single quote
    '\xc2\x92' : '\x27',     # Reverse single quote
    '\xc2\x93' : '\x22',     # Forward double quote
    '\xc2\x94' : '\x22',     # Reverse double quote
    '\xc2\x95' : ' ',
    '\xc2\x96' : '-',        # High hyphen
    '\xc2\x97' : '--',       # Double hyphen
    '\xc2\x99' : ' ',
    '\xc2\xa0' : ' ',
    '\xc2\xa6' : '|',        # Split vertical bar
    '\xc2\xab' : '<<',       # Double less than
    '\xc2\xbb' : '>>',       # Double greater than
    '\xc2\xbc' : '1/4',      # one quarter
    '\xc2\xbd' : '1/2',      # one half
    '\xc2\xbe' : '3/4',      # three quarters
    '\xca\xbf' : '\x27',     # c-single quote
    '\xcc\xa8' : '',         # modifier - under curve
    '\xcc\xb1' : '',          # modifier - under line
    '\xe2\x80\x93' : '-',
    '\xe2\x80\x94' : '-'
    
}

def replace_chars(match):
    char = match.group(0)
    return chars[char]

class Filing(object):
    companyID = ''
    reportPeriod = ''
    filingText = ''
    filingPath = ''
    statementOfCashFlows = ''
    filingType = ''
    denomination = ''
    cashFlowDictionary = ''
    yearsInStatement = []

    def __init__(self, path_to_filing):
        self.extractFilingType(path_to_filing)
        self.extractCompanyID(path_to_filing)
        self.extractReportPeriod(path_to_filing)
        self.extractFilingText(path_to_filing)
        self.findStatementOfCashFlows()
        self.determineDenomination()
        self.cleanUpCashFlowTable()
        self.createCashFlowDictionary()

    def extractFilingType(self, path_to_filing):
        if '.htm' in path_to_filing:
            self.filingType = 'HTML'
        elif '.txt.' in path_to_filing:
            self.filingType = 'TXT'
        self.filingPath = path_to_filing
    
    def extractCompanyID(self, path_to_filing):
        path_parts = path_to_filing.split('\\')
        self.companyID = path_parts[-3]
    
    def extractReportPeriod(self, path_to_filing):
        path_parts = path_to_filing.split('\\')
        self.reportPeriod = path_parts[-2].split('-')[1][1:]
        
    def extractFilingText(self, path_to_filing):
        with open(path_to_filing, 'rb') as input_stream:
            self.filingText = ''.join([x for x in input_stream])
             
    def findStatementOfCashFlows(self):
        # Extracts the statement of cash flow table from the input file.
        if self.filingType == 'HTML':
            soup = BeautifulSoup(self.filingText)
            tables = soup.find_all('table')
            for table in tables:
                item= table.get_text().strip().encode('ascii','ignore')
                n=0
                if cfop.search(item)!=None:
                    n=n+1
                if cfinvest.search(item)!=None:
                    n=n+1
                if cffin.search(item)!=None:
                    n=n+1
                if cash.search(item)!=None:
                    n=n+1
                if inc.search(item)!=None:
                    n=n+1
                if n>=3 and re.search(noncfterms,item)==None:
                    self.statementOfCashFlows = table
        
        if self.filingType == 'TXT':
            pass
        
    def determineDenomination(self):
        if self.statementOfCashFlows == '':
            return 'Error, Statement of Cash Flow Table is not populated. Unable to search for denominations.'
        else:
            if re.search(denomthousands,self.statementOfCashFlows.get_text().strip())!=None:
                self.denomination = 'Thousands'
            elif re.search(denommillions,self.statementOfCashFlows.get_text().strip())!=None:
                self.denomination = 'Millions'
    
    def cleanUpCashFlowTable(self):
        parsed_SCF_table = []
        mytr = self.statementOfCashFlows.find_all('tr')
        for col in mytr:
            trs = col.find_all(['td','th'])
            row_items = []
            for row in trs:
                string = row.get_text()
                string = string.replace('\r',' ')
                string = string.replace('\n',' ')
                string = ' '.join(string.split())
                string = string.encode('utf8')
                string = re.sub('(' + '|'.join(chars.keys()) + ')', replace_chars, string)
                
                #Optimizations: Putting all 3 clean up loops into one.
                item = string
                if item != '' and item != '$' and item != ')' and item != '(':
                    pass
                else:
                    continue
                item = item.replace(',','')
                if re.search('\(\s*?\d+\.?\d*?\s*?',item)!=None:
                    item = re.sub('\(\s?','-',item)
                #End Optimizations
                
                row_items.append(item)
            
            if len(row_items)>0:
                parsed_SCF_table.append(row_items)
                
            self.statementOfCashFlows = parsed_SCF_table
                
    def createCashFlowDictionary(self):
        # Construct a dictionary to access the cash flow statement more easily. The dictionary will have years as keys, and will have a list of tuples (line item, amount) as values.
        self.cashFlowDictionary = {}
        years = []
        for row in self.statementOfCashFlows:
            try:
                for item in row:
                    if int(item) > 1950 and int(item) < 2050:
                        pass
                    else:
                        break
                years = row
                self.yearsInStatement = years
                for item in years:
                    self.cashFlowDictionary[item] = []
                break
            except:
                continue
        
        for x, year in enumerate(years):
            for row in self.statementOfCashFlows:
                if len(row)>len(years):
                    self.cashFlowDictionary[year].append((row[0], row[x+1]))
                else:
                    if row == years:
                        self.cashFlowDictionary[year].append(year)
                    else:
                        self.cashFlowDictionary[year].append(row[0])

    def saveCashFlowsToFile(self):
        for year in self.yearsInStatement:
            output_path = self.filingPath.split('\\')[0:-1]
            output_path = '\\'.join(output_path)
            output_path = output_path + '\\' +self.companyID+'_'+ year + '_CFStatement.csv'
            with open(output_path, 'wb') as output_stream:
                output_stream.write("Denominations: " + self.denomination + '\n')
                for k in self.cashFlowDictionary[year]:
                    if isinstance(k, basestring):
                        output_stream.write(k.strip() + '\n')
                    else:
                        temp_string = ''
                        for item in k:
                            temp_string = temp_string + item.strip() + ', '
                        temp_string = temp_string[0:-2] + '\n'
                        output_stream.write(temp_string)
            
       
    def __str__(self):
        to_string = ''
        to_string = to_string + 'CIK:' + str(self.companyID) + '\n'
        to_string = to_string + 'Report Period:' + str(self.reportPeriod) + '\n'
        to_string = to_string + 'Filing Type:' + str(self.filingType) + '\n'
        return to_string