from lxml import etree
import requests
import csv
import sys, getopt
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

def main():
    driver = webdriver.Firefox()
    search_results = cik_lookup(driver)
    print search_results
    form_results = form_lookup(driver, search_results)
    print form_results
    filing_details = get_xml_url(driver, form_results)
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
    print fund_data
    write_tsv(reduced_headers, fund_data)

def cik_lookup(driver):
    #Include getopts options
    #Have error handling
    driver.get("https://www.sec.gov/edgar/searchedgar/companysearch.html")
    cik_search = driver.find_element_by_id("cik")
    #Pass CIK from command line arguments to search box
    cik_search.send_keys(sys.argv[1])
    cik_search.submit()
    #Call wait_for_load to ensure that new page loads
    wait_for_load(driver, 'documentsbutton', 'Documents')
    return driver.current_url

def form_lookup(driver, url):
    #Have error handling
    driver.get(url)
    #Get the link from the table cell directly after the cell that contains the
    #13F-HR text
    form_13F_HR = driver.find_element_by_xpath(
                                "//*[contains(text(), '13F-HR')]/following::td")
    form_13F_HR.click()
    #Call wait_for_load to ensure that new page loads
    wait_for_load(driver, 'formName', 'Form 13F-HR')
    return driver.current_url

def get_xml_url(driver, url):
    #Have error handling
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
    #Use requests library to retrieve source XML
    response = requests.get(url)
    #Add error handling based on http response code
    print response
    #transform response into string
    return response.content

def create_etree(xml):
    #create lxml etree element
    return etree.fromstring(xml)

def get_headers(etree):
    funds = etree.xpath(
                '//informationTable:infoTable',
                namespaces = {"informationTable":
                "http://www.sec.gov/edgar/document/thirteenf/informationtable"})
    headers = []
    #Only need to loop through one fund
    fund = funds[0]
    fund_tags = fund.xpath('.//*')
    #Set up counter to loop through elements list
    i = 0
    for x in fund_tags:
        #Insert tag value into headers list
        headers.append(fund_tags[i].tag)
        #increment counter up one
        i += 1
    return headers

#XMl tags inserted into headers come with namespace URL, this trims those off
def trim_headers(headers):
    split_headers = []
    for x in headers:
        split_headers.append(x.split('}', 1)[-1])
    return split_headers

def get_fund_data(etree):
    #Define namespace and get all records of infoTable
    funds = etree.xpath(
                '//informationTable:infoTable',
                namespaces = {"informationTable":
                "http://www.sec.gov/edgar/document/thirteenf/informationtable"})
    #Set up empty list for lists of child nodes' text (multidimensional list)
    funds_values = []
    #Iterate through each infoTable tag
    for fund in funds:
        #Get all child and grandchild elements within the infoTable
        fund_text = fund.xpath('.//*')
        #Set up counter for second level of iteration
        i = 0
        #Empty list for text values that get inserted into funds_values list
        fund_attributes = []
        #insert the list of text values into the funds_values list
        funds_values.append(fund_attributes)
        #iterate through children of infoTable getting their text values
        for x in fund_text:
            #check for empty values and rewrite as string
            if fund_text[i].text == "\n      ":
                fund_attributes.append("empty")
            else:
                fund_attributes.append(fund_text[i].text)
            #increment counter up one
            i += 1
    return funds_values

def write_tsv(headers, data):
    #Add third option above to pass filename from ARGV
    #Create TSV name - need to add pass through from ARGV
    tsvFilename = "tmp/ticker.tsv"
    #Create or Open TSV
    tsv = open(tsvFilename, "w")
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
