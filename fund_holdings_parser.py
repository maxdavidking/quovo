from lxml import etree
import requests
import csv
import sys, getopt
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

def main():
    #Include getopts options
    #Have error message
    driver = webdriver.Firefox()
    driver.get("https://www.sec.gov/edgar/searchedgar/companysearch.html")
    element = driver.find_element_by_id("cik")
    element.send_keys(sys.argv[1])
    element.submit()
    wait(driver, 3).until(
    expected_conditions.text_to_be_present_in_element(
        (By.ID, 'documentsbutton'),
        'Documents'
        )
    )
    #Return this URL and pass to new function that looks for 'documents'?
    element2 = driver.find_element_by_xpath("//*[contains(text(), '13F-HR')]/following::td")
    element2.click()
    wait(driver, 3).until(
    expected_conditions.text_to_be_present_in_element(
        (By.ID, 'formName'),
        'Form 13F-HR'
        )
    )
    element3 = driver.find_element_by_partial_link_text("able.xml")
    #This is the URL
    return element3.get_attribute("href")



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

#Create TSV name - need to add pass through from ARGV
tsvFilename = "tmp/ticker.tsv"
#Create or Open TSV
tsv = open(tsvFilename, "w")
#Create colNames, need to get dynamically and separate with TSV
col_names = '\t'.join(reduced_headers)
tsv.write(col_names)
tsv.write('\n')
for values in funds_text:
    string_values = '\t'.join(values)
    print string_values
    #write to tsv
    tsv.write(string_values)
    #Move to new line
    tsv.write("\n")

if __name__ == "__main__":
    main()
