from lxml import etree
import requests
import csv

#Open new TSV file to save data in tab separated format
ticker_data = open('tmp/ticker.tsv', 'w')
csvwriter = csv.writer(ticker_data, delimiter='\t')


#Hard code link directly to XML for now
link = "https://www.sec.gov/Archives/edgar/data/1166559/000110465918033472/a18-13444_1informationtable.xml"

#Use requests library to retrieve source code
response = requests.get(link)
#Add error handling based on http response code
print response

#transform response into string
source = response.content

#create lxml etree element
root = etree.fromstring(source)

#Define namespace and get all records of infoTable
funds = root.xpath('//informationTable:infoTable', namespaces = {"informationTable": "http://www.sec.gov/edgar/document/thirteenf/informationtable"})

#Set up empty list for headers
headers = []
#Set up empty list for lists of child nodes' text (multidimensional list)
funds_text = []
#Iterate through each infoTable
for fund in funds:
    #Get all child and grandchild elements within the infoTable
    elements = fund.xpath('.//*')
    #Set up counter for second level of iteration
    i = 0
    #Set up empty list for text values that will get inserted into funds_text list
    fund_attributes = []
    #insert the list of text values into the funds_text list
    funds_text.append(fund_attributes)
    #iterate through children of infoTable getting their text values
    for x in elements:
        #NEED TO JUST DO THIS ONCE
        headers.append(elements[i].tag)
        #store text values in fund_attributes
        if elements[i].text == "\n      ":
            fund_attributes.append("empty")
        else:
            fund_attributes.append(elements[i].text)

        #increment counter up one
        i += 1

#Temporary strip of all but first x elements - also strip out namespace from header
reduced_headers = headers[:12]
for x in reduced_headers:
    print type(x)
    x_split = x.split('}', 1)[-1]
    print x_split
