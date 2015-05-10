'''
Created on May 8, 2015

@author: Keith
'''
import glob
import os
from Filing import Filing

def Find_Most_Likely_Statement_In_Folder(folder):
    #Takes the path to a folder, returns the path to the largest file in that folder of type .htm.
    files = glob.glob(folder + "\\*")
    html_files = [item for item in files if 'htm' in item.split('.')[-1] or 'txt' in item.split('.')[-1]]
    if len(html_files) == 0:
        print 'Error, no files found in the folder.', folder
        return 
    else:
        html_files.sort(key=lambda x: os.path.getsize(x))
        html_files.reverse()
        return html_files[0]

def Find_All_10K(company_check_file):
    #Loop through folder and find all 10k statements
    #Avoid companies not listed in the check_file
    #Returns a list of paths to files which should contain the 10k form.
    
    # Key is company ID, value is list of reporting years
    companies_to_extract = {}
    with open(company_check_file, 'rb') as input_stream:
        for line in input_stream:
            line = line.strip()
            line = line.split(',')
            if line[0] not in companies_to_extract:
                companies_to_extract[line[0]] = [line[1]]
            else:
                companies_to_extract[line[0]].append(line[1])
    
    
    initial_paths = glob.glob('C:\\Users\\Keith\\Desktop\\Workspace\\Work - Summer 2015\\EDGARParser\\10KMASTER\\Y2009-Y2010\\Filings\\*\\*')
    pruned_paths = []
    for path in initial_paths:
        year = path.split('\\')[-1].split('-')[1][1:]
        cik= path.split('\\')[-2]
        
        try:
            if year in companies_to_extract[cik]:
                pruned_paths.append(path)
        except KeyError:
            #Company not found in check file, skipping.
            pass
        
    list_of_annual_reports = []
    for k in pruned_paths:
        list_of_annual_reports.append(Find_Most_Likely_Statement_In_Folder(k))
    return list_of_annual_reports

            

if __name__ == '__main__':
    tenK_reports = Find_All_10K("C:\\Users\\Keith\\Desktop\\Workspace\\Work - Summer 2015\\EDGARParser\\Code and Utility Files\\cikyearcomp0910.csv")
    list_of_filings = [0.0] * len(tenK_reports)
    for i, k in enumerate(tenK_reports):
        print i+1, ' of ', len(tenK_reports)
        list_of_filings[i] = Filing(k)
        list_of_filings[i].save_CFs_to_file();
    

    
    