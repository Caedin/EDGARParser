import lxml
from bs4 import BeautifulSoup
import re
import pickle
import csv
import glob
import collections
import shutil

Compile Search Terms 

noncfterms=re.compile('financial information|statement of income|operating data|balance sheet data|income statement|net revenues|cost of sales|cost of goods sold|selected other financial data|selected financial data|balance sheet data|statement of earnings data|common shares outstanding|other financial data|summary of operations|EBITDA|statement of operating|condensed', re.I)
cfop=re.compile('operating activities|cash flows from operations',re.I)
cfinvest=re.compile('investing activities|cash flows used for investments|investment activities',re.I)
cffin=re.compile('financing activities|cash flows from financing',re.I)
cash=re.compile('net cash provided by|net cash used by|net increase (decrease) in cash|net increase in cash|net decrease in cash|net cash used|net cash from', re.I)
inc=re.compile('income|earnings|loss',re.I)
denomthousands=re.compile('thousands|\'?000\'?s', re.I)
denommillions=re.compile('millions|\'?000,?000\'?s', re.I)

##Define Functions
##Function to test if the table is a statement of cash flow
def testtables(tablescf):
    if tablescf!=[]:
        global cfstatement
        cfstatement=[]
        for each in tablescf:
            item=each.get_text().strip()
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
                cfstatement.append(each)

##Create terms and function for removing messed up characters
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

##Create Functions for determining which years the SofC cover

def yeartest(item):
    n=0
    for i, obj in enumerate(item):
        if re.search(yearsearch,obj)!=None:
            n=n+1
        if i+1==len(item) and n>1:
            tempyears.extend(item)
            tempyears.append(n)

def yeartest2(item):
    m=0
    for i, obj in enumerate(item):
        if re.search(yearsearch,obj)!=None:
            m=m+1
        if i+1==len(item) and m>1:
            tempyears2.extend(item)
            tempyears2.append(m)

def checkyears2(z, tempyears):
    global tempyears2
    global tempyearsnew
    tempyears2=[]
    tempyearsnew=[]
    for p, item in enumerate(each[z+1:]):
        yeartest2(item)
        if tempyears2==[] and p!=len(each[z+1:])-1:
            continue
        if tempyears2!=[] and tempyears2[-1]>tempyears[-1]:
            tempyearsnew=tempyears2[0:-1]
            return
        else:
            tempyears2=[]

def checkyears(each):
    global tempyears
    tempyears=[]
    for z, item in enumerate(each):
        yeartest(item)
        if tempyears==[] and z!=len(each)-1:
            continue
        if tempyears==[] and z==len(each)-1:
            tempyears=['missing']
            years.append(tempyears)
            return
        if tempyears!=[] and z!=len(each)-1 and tempyears[1][0]!=len(item):
            checkyears2(z,tempyears)
        if tempyearsnew!=[]:
            years.append(tempyearsnew)
            return
        else:
            years.append(tempyears[0:-1])
            return
    

###Start execution of the program
##Read in CIK YEAR combinations from COMPUSTAT.  We do not need to parse the file if it's not in COMPUSTAT.
cikyearcomp=[]
f = open('E:\\projects\\SofC\\cikyearcomp0910.csv', 'rU')
try:
    reader = csv.reader(f)
    for row in reader:
        cikyearcomp.append(row)
finally:
    f.close()

##Collect all of the paths for 10K annual reports 
initial_paths = glob.glob('H:\\10KMASTER\\Y2009-Y2010\\FILINGS\\*\\*')

paths=[]
cikyearboth=[]
cikyearedgar=[]

##Using the path name collec the year and cik then test to make sure it is in the COMPUSTAT list of years and ciks.
for each in initial_paths:
    year=each.split('\\')[5].split('-')[1][1:]
    cik=each.split('\\')[4]
    cikyeartest=[cik, year]
    cikyearedgar.append(cikyeartest)
    if cikyeartest in cikyearcomp:
        cikyearboth.append(cikyeartest)
        paths.append(each)

cikyearcompmissing=[]

for each in cikyearcomp:
    if each not in cikyearedgar:
        cikyearcompmissing.append(each)
    
###Collect names of files already parsed and only do the ones that are not done

filesdone=glob.glob('E:\\projects\\SofC\\HTMCFparsedcomp0910\\*')
cikfolderdone=[]
cikyeardone=[]

for each in filesdone:
    pieces=each.split('\\')[4].split('-')
    folder=pieces[0]+'-'+pieces[1]+'-'+pieces[2]+'-'+pieces[3]
    cikyeardonetemp=[pieces[0],pieces[2][1:]]
    cikfolderdone.append(folder)
    cikyeardone.append(cikyeardonetemp)
        

for initial_path in paths:

#checking to make sure it's not done already
    year=initial_path.split('\\')[5].split('-')[1][1:]
    cik=initial_path.split('\\')[4]
    cikyeartest=[cik, year]
    if cikyeartest in cikyeardone:
        continue


# for each directory I am collecting all of the files in the directory
    files = glob.glob(initial_path + '\\*')
    files = [item for item in files if item.split('.')[-1] in ['htm']]

##This is a test file for debugging
##files=['H:\\10KMASTER\\Y2009-Y2010\\FILINGS\\1015593\\R20090318-C20081231-F31\\rvb_10k.htm']

    for filename in files:

##Collect all of the tables from the html file

        test=BeautifulSoup(open(filename))
        tables=test.find_all('table')

        cftables=[]
        for each in tables:
            cftables.append(each)

##Test and only keep the tables that appear to be cash flow statements.

        testtables(cftables)
        if cfstatement==[]:
            continue

##Try to identify the denomination the statement is reported in (e.g. thousands, millions) 
        denom=[]
        for table in cfstatement:
            tempdenom=''
            if re.search(denomthousands,table.get_text().strip())!=None:
                tempdenom='Thousands'
            elif re.search(denommillions,table.get_text().strip())!=None:
                tempdenom='Millions'
            denom.append(tempdenom)

        parsedtables=[]
        for each in cfstatement:
            doc=[]
            mytr=each.find_all('tr')
            for col in mytr:
                trs=col.find_all(['td','th'])
                firstinlist=[]
                for row in trs:
                    string=row.get_text()
                    stringnew=string.replace('\r',' ')
                    stringnew2=stringnew.replace('\n',' ')
                    stringnew3=' '.join(stringnew2.split())
                    stringnew3=stringnew3.encode('utf8')
                    stringnew3=re.sub('(' + '|'.join(chars.keys()) + ')', replace_chars, stringnew3)
                    firstinlist.append(stringnew3)
                doc.append(firstinlist)
            parsedtables.append(doc)

        newcf=[]

        for each in parsedtables:
            tab=[]
            for rows in each:
                row=[]
                for item in rows:
                    if item!='' and item!='$' and item!=')' and item!='(':
                        row.append(item)
                if row!=[]:
                    tab.append(row)
            newcf.append(tab)

        newcf2=[]
        for each in newcf:
            newtable=[]
            for item1 in each:
                row=[]
                for item in item1:
                    item=item.replace(',','')
                    if re.search('\(\s*?\d+\.?\d*?\s*?',item)!=None:
                        item=re.sub('\(\s?','-',item)
                    row.append(item)
                newtable.append(row)
            newcf2.append(newtable)
            

        yearsearch=re.compile('[^\d]((19)|(20)\d\d)[^\d]|^(((19)|(20))\d\d$)|\s(((19)|(20))\d\d)$|(^((19)|(20))\d\d)\s?|\s(((19)|(20))\d\d)\s', re.I)


        years=[]
        for each in newcf2:
            checkyears(each)


        finalyears=[]
        for table in years:
            tempyears=[]
            for each in table:
                if re.search(yearsearch,each)!=None:
                    yearsact=re.search(yearsearch,each).group()
                    tempyears.append(yearsact.strip())
                elif each=='missing':
                    tempyears.append(each)
            finalyears.append(tempyears)


        finalyears2=[]
        
        newcf25=[]
        for i, each in enumerate(finalyears):
            if each!=['missing']:
                finalyears2.append(each)
                newcf25.append(newcf2[i])
                
        yearstest=years
        years=finalyears2

        newcf3=[]
        taglist=[]
        for j, table in enumerate(newcf25):
            tagnum=0
            newtable=[]
            taglisttempdict={}
            noyears=len(years[j])
            for i, line in enumerate(table):
                if i>0 and len(line)==noyears+1 and len(table[i-1])==1:
                    if re.search('Years? Ended|In Thousands|000\'s|In Millions|000,000\'s',table[i-1][0], re.I)!=None:
                            continue
                    else:
                        if i>1 and len(table[i-2])==1:
                            tag=[table[i-1][0]+' '+table[i-2][0]]
                            if tag[0] not in taglisttempdict:
                                tagnum=tagnum+1
                                taglisttempdict[tag[0]]=tagnum
                            line.append([tagnum])
                            newtable.append(line)
                        else:
                            tag=table[i-1]
                            if tag[0] not in taglisttempdict:
                                tagnum=tagnum+1
                                taglisttempdict[tag[0]]=tagnum
                            line.append([tagnum])
                            newtable.append(line)
                if i>0 and len(line)==noyears+1 and len(table[i-1])!=1:
                    line.append([tagnum])
                    newtable.append(line)
            newcf3.append(newtable)
            taglist.append(taglisttempdict)

        newcf4=[]
        for table in newcf3:
            temptable=[]
            for i, line in enumerate(table):
                if line[-1]==[0]:
                    continue
                else:
                    temptable.append(line)
            newcf4.append(temptable)


        newcf5=[]
        for table in newcf4:
            newtable=[]
            for each in table:
                doc=[]
                for item in each:
                    try:
                        x=float(item)   
                        doc.append(x)
                    except:
                          doc.append(item)
                newtable.append(doc)
            newcf5.append(newtable)


        order=[]
        for table in years:
            try:
                if int(table[0])<int(table[-1]):
                    bigtolittle=0
                elif int(table[0])>int(table[-1]):
                    bigtolittle=1
                order.append(bigtolittle)
            except:
                bigtolittle=-999
                order.append(bigtolittle)

        newcf6=[]
        for j, table in enumerate(newcf5):
            newtable=[]
            for row in table:
                if order[j]==1 or order[j]==-999:
                    newrow=[row[0],row[1],row[-1]]
                else:
                    newrow=[row[0],row[-1],row[-1]]
                newtable.append(newrow)
            newcf6.append(newtable)
            
        for j, table in enumerate(newcf6):
            newcf6[j].insert(0,denom[j])
            if order[j]==1 or order[j]==-999:
                newcf6[j].insert(0,years[j][0])
            if order[j]==0:
                newcf6[j].insert(0,years[j][-1])
            newcf6[j].insert(0,taglist[j])

        newcf7=[]
        for j, table in enumerate(newcf6):
            if len(table)>5:
                newcf7.append(table)

        newcf7.insert(0,filename)

        stub=filename.split('\\')
        stub0=stub[4]
        stub1=stub[5]
        stub2=stub[6]
        stub2=stub2.split('.')
        stub2=stub2[0]
        stubfinal=stub0+'-'+stub1+'-'+stub2

        pickle.dump(newcf7, open('E:\\projects\\SofC\\HTMCFparsedcomp0910\\' + stubfinal +'.p',"wb"))



titlecf={
'(Increase) decrease in:':'cfo',
'Adjustment for:':'cfo',
'Adjustments to reconcile income from continuing operations to net cash provided by operating activities:':'cfo',
'Adjustments to reconcile net (loss) income to net cash provided by operating activities:':'cfo',
'Adjustments to reconcile net earnings (loss) to cash provided by (used in) operating activities:':'cfo',
'Adjustments to reconcile net earnings (loss) to net cash provided by operating activities:':'cfo',
'Adjustments to reconcile net earnings to net cash flows from operating activities:':'cfo',
'Adjustments to reconcile net earnings to net cash provided by (used in) operating activities:':'cfo',
'Adjustments to reconcile net earnings to net cash provided from operating activities:':'cfo',
'Adjustments to reconcile net income (loss) attributable to common stockholders to net cash provided by operating activities:':'cfo',
'Adjustments to reconcile net income (loss) to net cash provided by operating activities:':'cfo',
'Adjustments to reconcile net income to net cash from operating activities':'cfo',
'Adjustments to reconcile net income to net cash provided by (used in) operating activities:':'cfo',
'Adjustments to reconcile net income to net cash Provided by operating activities:':'cfo',
'Adjustments to reconcile net income to net cash provided by operating activities:':'cfo',
'Adjustments to reconcile net increase in net assets resulting from operations to net cash provided by operating activities:':'cfo',
'Adjustments to reconcile net los to net cash used in operating activities:':'cfo',
'Adjustments to reconcile net loss to net cash provided by operating activities:':'cfo',
'Adjustments to reconcile net loss to net cash used in operating activities:':'cfo',
'Cash (used for) provided by':'cfo',
'Cash Flow Data:':'cfo',
'Cash Flows from Operating Activities':'cfo',
'CASH FLOWS FROM OPERATING ACTIVITIES':'cfo',
'Cash flows from operating activities':'cfo',
'CASH FLOWS FROM OPERATING ACTIVITIES:':'cfo',
'Cash flows from operating activities:':'cfo',
'Cash Flows From Operating Activities:':'cfo',
'Cash Flows:':'cfo',
'Cash provided by (used in):':'cfo',
'Cash provided by/(used in):':'cfo',
'OPERATING ACTIVITIES':'cfo',
'Operating activities':'cfo',
'OPERATING ACTIVITIES':'cfo',
'Operating activities:':'cfo',
'Operating Activities:':'cfo',
'OPERATING ACTIVITIES:':'cfo',
'Operating Activities (In Thousands)':'cfo',
'Operating Activities (In Thousands):':'cfo',
'Operating Activities (In Millions)':'cfo',
'Operating Activities (In Millions):':'cfo',
'Operating activities (In Thousands)':'cfo',
'Operating activities (In Thousands):':'cfo',
'Operating activities (In Millions)':'cfo',
'Operating activities (In Millions):':'cfo',
'OPERATING ACTIVITIES (In Thousands)':'cfo',
'OPERATING ACTIVITIES (In Thousands):':'cfo',
'OPERATING ACTIVITIES (In Millions)':'cfo',
'OPERATING ACTIVITIES (In Millions):':'cfo',
'OPERATING ACTIVITIES (In Thousands)':'cfo',
'OPERATING ACTIVITIES (In Thousands):':'cfo',
'OPERATING ACTIVITIES (In Millions)':'cfo',
'OPERATING ACTIVITIES (In Millions):':'cfo',
'Provided by operating activities':'cfo',
'provided by operating activities:':'cfo',
'Reconciliation of net loss to net cash used in operating activities:':'cfo',
'used in operating activities:':'cfo',
'Cash flows from financing':'fin',
'Cash Flows from Financing Activities':'fin',
'Cash flows from financing activities':'fin',
'Cash Flows from Financing Activities':'fin',
'Cash flows from financing activities':'fin',
'CASH FLOWS FROM FINANCING ACTIVITIES':'fin',
'Cash Flows From Financing Activities:':'fin',
'Cash flows from financing activities:':'fin',
'Cash flows from financing activities:':'fin',
'Cash Flows From Financing Activities:':'fin',
'CASH FLOWS FROM FINANCING ACTIVITIES:':'fin',
'CASH FLOWS FROM FINANCING ACTIVITIES:':'fin',
'CASH FLOWS FROM FINANCING ACTIVITIES:':'fin',
'Cash Flows from Investing Activities':'invest',
'Cash flows from investing activities':'invest',
'Cash flows from investing activities':'invest',
'Cash Flows from Investing Activities':'invest',
'CASH FLOWS FROM INVESTING ACTIVITIES':'invest',
'Cash flows from investing activities:':'invest',
'Cash flows from investing activities:':'invest',
'CASH FLOWS FROM INVESTING ACTIVITIES:':'invest',
'CASH FLOWS FROM INVESTING ACTIVITIES:':'invest',
'CASH FLOWS FROM INVESTING ACTIVITIES:':'invest',
'Cash Flows From Investing Activities:':'invest',
'Cash Flows From Investing Activities:':'invest',
'CASH FLOWS USED FOR INVESTING ACTIVITIES':'invest',
'INVESTING ACTIVITIES':'invest',
'INVESTING ACTIVITIES':'invest',
'Investing activities':'invest',
'Investing Activities:':'invest',
'Investing activities:':'invest',
'INVESTING ACTIVITIES:':'invest',
'Marketable securities:':'invest',
'Cash (refunded) paid during the period for income taxes':'sup',
'Cash paid during period for:':'sup',
'Cash paid during the year for:':'sup',
'Cash paid for:':'sup',
'Net change in Financing Activities':'fin',
'Net change in Financing activities':'fin',
'Net change in Financing Activities:':'fin',
'Net change in Financing activities:':'fin',    
'Non-Cash Financing Activity':'sup',
'Non-cash financing and investing activities:':'sup',
'Non-cash investing activity':'sup',
'Noncash investing and financing activities:':'sup',
'Non-cash investing and financing activities:':'sup',
'Non-cash investing and financing activities:':'sup',
'Non-cash Investing Transactions:':'sup',
'Supplemental Cash Flow Information:':'sup',
'Supplemental Cash Flow Information:':'sup',
'Supplemental cash flow information:':'sup',
'Supplemental cash flow information:':'sup',
'Supplemental disclosure of cash flow information:':'sup',
'Supplemental disclosure of cash flow information:':'sup',
'Supplemental disclosure of cash flow information:':'sup',
'SUPPLEMENTAL DISCLOSURE OF CASH FLOW INFORMATION:':'sup',
'Supplemental Disclosure of Cash Flow Information:':'sup',
'Supplemental disclosure of non cash transactions':'sup',
'Supplemental disclosure of non-cash activities:':'sup',
'Supplemental disclosure of noncash investing and financing activities:':'sup',
'Supplemental disclosure of noncash investing and financing activities:':'sup',
'Supplemental disclosures of cash flow information:':'sup',
'Supplemental disclosures of non-cash investing activity:':'sup',
'SUPPLEMENTAL INFORMATION':'sup',
'Supplemental non-cash disclosure:':'sup',
'Supplemental non-cash investing and financing activities:':'sup',
'Supplemental schedule of non-cash operating investing and financing activities:':'sup'
}

newtitlecf={}

for key,value in titlecf.items():
    if key not in newtitlecf.keys():
        newtitlecf[key]=value

files=glob.glob('E:\\projects\\SofC\\HTMCFparsedcomp0910\\*')

biglist=[]
for each in files:
    cf=pickle.load(open(each, 'rb'))
    for i,tables in enumerate(cf[1:]):
        #turn dictionary into tuples 
        dictordered=sorted([(v,k) for k, v in tables[0].iteritems()], key=lambda line: line[0])
        tempdict={}
        tempval=''
        tempkey=''
        for value, key in dictordered:
            if key in newtitlecf.keys():
                tempdict[value]=newtitlecf[key]
                tempval=value
                tempkey=newtitlecf[key]
            else:
                if tempval!='':
                    tempdict[value]=tempkey
                else:
                    tempdict[value]='cfo'            
        newtables=tables
        newtables[0]=[tempdict]
        
        for item in newtables[3:]:
            if isinstance(item[0],str):
                tup=((item[0].lower(),tempdict[item[2][0]]), cf[0])
            else:
                tup=((item[0],tempdict[item[2][0]]), cf[0])
            biglist.append(tup)

listwithoutnames=[]
for each in biglist:
    listwithoutnames.append(each[0])
    

#output the label (biglist)
test=collections.Counter(listwithoutnames)

collapsedict=collections.defaultdict(list)
for each in biglist:
    collapsedict[each[0]].append(each[1])

output=[]
for v, k in collapsedict.items():
    if len(k)>10:
        n=10
    else:
        n=len(k)
    out=(v,len(k),k[0:n])
    output.append(out)

                
with open('E:\\projects\\SofC\\biglistv2.csv','wb') as f:
	spam=csv.writer(f, delimiter=',')
	for each in output:
		spam.writerow(each)
