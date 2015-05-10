'''
Created on May 8, 2015

@author: Keith
'''
import glob
import os
from Filing import Filing

# Accepts path to a folder, and returns the most likely file with the cash flow table. (10K)
def Find10KInFolder(folder):
    filesInFolder = glob.glob(folder + "\\*")
    htmlFiles = [item for item in filesInFolder if 'htm' in item.split('.')[-1] or 'txt' in item.split('.')[-1]]
    if len(htmlFiles) == 0:
        print 'Error, no HTML Files found in the folder.', folder
        return 
    else:
        htmlFiles.sort(key=lambda x: os.path.getsize(x))
        htmlFiles.reverse()
        return htmlFiles[0]

# Accepts a file with a list of company and year report pairs. Finds all available reports from the list, and returns a list of file paths to their respective 10K documents.
def FindEligibleReports(eligibleCompanyReports):
    eligibleCompanyReportDictionary = {}
    with open(eligibleCompanyReports, 'rb') as input_stream:
        for line in input_stream:
            line = line.strip()
            line = line.split(',')
            if line[0] not in eligibleCompanyReportDictionary:
                eligibleCompanyReportDictionary[line[0]] = [line[1]]
            else:
                eligibleCompanyReportDictionary[line[0]].append(line[1])
    
    
    initial_paths = glob.glob('C:\\Users\\Keith\\Desktop\\Workspace\\Work - Summer 2015\\EDGARParser\\10KMASTER\\Y2009-Y2010\\Filings\\*\\*')
    pruned_paths = []
    for path in initial_paths:
        year = path.split('\\')[-1].split('-')[1][1:]
        cik= path.split('\\')[-2]
        
        try:
            if year in eligibleCompanyReportDictionary[cik]:
                pruned_paths.append(path)
        except KeyError:
            #Company not found in check file, skipping.
            pass
        
    AnnualReports = []
    for k in pruned_paths:
        AnnualReports.append(Find10KInFolder(k))
    return AnnualReports

if __name__ == '__main__':
    AnnualReports = FindEligibleReports("C:\\Users\\Keith\\Desktop\\Workspace\\Work - Summer 2015\\EDGARParser\\Code and Utility Files\\cikyearcomp0910.csv")
    for i, k in enumerate(AnnualReports):
        print i+1, ' of ', len(AnnualReports)
        AnnualReports[i] = Filing(k)
        AnnualReports[i].saveCashFlowsToFile()
    

    
    