from lxml import etree
import requests
import csv
import sys, getopt
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

def main():
    search_results = cik_lookup()
    print search_results
    form_results = form_lookup(search_results)
    print form_results
    filing_details = get_xml_url(form_results)
    print filing_details
    xml_string = stringify_xml(filing_details)
    print xml_string
    xml_tree = create_etree(xml_string)
    print xml_tree
    headers = get_headers(xml_tree)
    print headers
    reduced_headers = trim_headers(headers)
    print reduced_headers
    fund_data = get_fund_data(xml_tree)
    #print fund_data
    write_tsv(reduced_headers, fund_data)

def cik_lookup():
    #Include getopts options
    #Have error handling
    driver = webdriver.Firefox()
    driver.get("https://www.sec.gov/edgar/searchedgar/companysearch.html")
    element = driver.find_element_by_id("cik")
    #Pass CIK from command line arguments to search box
    element.send_keys(sys.argv[1])
    element.submit()
    #Call wait to ensure that new page loads
    wait_for_load(driver, 'documentsbutton', 'Documents')
    return driver.current_url

def form_lookup(url):
    #Have error handling
    driver = webdriver.Firefox()
    driver.get(url)
    element = driver.find_element_by_xpath("//*[contains(text(), '13F-HR')]/following::td")
    element.click()
    #Call wait to ensure that new page loads
    wait_for_load(driver, 'formName', 'Form 13F-HR')
    return driver.current_url

def get_xml_url(url):
    #Have error handling
    driver = webdriver.Firefox()
    driver.get(url)
    element = driver.find_element_by_partial_link_text("able.xml")
    return element.get_attribute("href")

#Selenium will look for an element on a page without waiting for the new page
#to load. This function ensures the new page loads
def wait_for_load(driver, div_id, text):
    wait(driver, 3).until(
    expected_conditions.text_to_be_present_in_element(
        (By.ID, div_id),
        text
        )
    )

def stringify_xml(url):
    #Use requests library to retrieve source code
    response = requests.get(url)
    #Add error handling based on http response code
    print response
    #transform response into string
    return response.content

def create_etree(xml):
    #create lxml etree element
    return etree.fromstring(xml)

def get_headers(etree):
    funds = etree.xpath('//informationTable:infoTable', namespaces = {"informationTable": "http://www.sec.gov/edgar/document/thirteenf/informationtable"})
    headers = []
    fund = funds[0]
    elements = fund.xpath('.//*')
    #Set up counter to loop through elements list
    i = 0
    for x in elements:
        #Insert tag value into headers list
        headers.append(elements[i].tag)
        #increment counter up one
        i += 1
    return headers

#XMl tags inserted into headers come with namespace URL - this function trims that off
def trim_headers(headers):
    split_headers = []
    for x in headers:
        split_headers.append(x.split('}', 1)[-1])
    return split_headers

def get_fund_data(etree):
    #Define namespace and get all records of infoTable
    funds = etree.xpath('//informationTable:infoTable', namespaces = {"informationTable": "http://www.sec.gov/edgar/document/thirteenf/informationtable"})
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
            #store text values in fund_attributes
            if elements[i].text == "\n      ":
                fund_attributes.append("empty")
            else:
                fund_attributes.append(elements[i].text)
            #increment counter up one
            i += 1
    return funds_text

def write_tsv(headers, data):
    #Add third option above to pass filename from ARGV
    #Create TSV name - need to add pass through from ARGV
    tsvFilename = "tmp/ticker.tsv"
    #Create or Open TSV
    tsv = open(tsvFilename, "w")
    #Create colNames, need to get dynamically and separate with TSV
    col_names = '\t'.join(headers)
    tsv.write(col_names)
    tsv.write('\n')
    for values in data:
        string_values = '\t'.join(values)
        #print string_values
        #write to tsv
        tsv.write(string_values)
        #Move to new line
        tsv.write("\n")

if __name__ == "__main__":
    main()
