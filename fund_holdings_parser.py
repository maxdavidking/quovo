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

funds_text = []
for fund in funds:
    elements = fund.xpath('*')
    i = 0
    fund_attributes = []
    funds_text.append(fund_attributes)
    for x in elements:
        fund_attributes.append(elements[i].text)
        i += 1

#print funds_text
for x in funds_text:
    print x
