from lxml import etree
import requests
import csv
import sys
import getopt
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException


def main():
    # Set up webdriver to navigate EDGAR
    driver = webdriver.Firefox()
    # Move through pages to get to form 13F-HR XML file
    search_results = cik_lookup(driver)
    form_results = form_lookup(driver, search_results)
    filing = get_xml_url(driver, form_results)
    # Get XML and convert to string and then etree
    xml_string = stringify_xml(filing)
    xml_tree = create_etree(xml_string)
    funds = query_etree(xml_tree)
    # Store XML tags as headers for TSV
    headers = get_headers(funds)
    reduced_headers = trim_headers(headers)
    # Get XML text as data for TSV
    fund_data = get_fund_data(funds)
    # Write to TSV file
    write_tsv(reduced_headers, fund_data)


def cik_lookup(driver):
    driver.get("https://www.sec.gov/edgar/searchedgar/companysearch.html")
    cik_search = driver.find_element_by_id("cik")
    # Pass CIK from command line arguments to search box
    cik_search.send_keys(sys.argv[1])
    cik_search.submit()
    # Call wait_for_load to ensure that new page loads
    wait_for_load(driver, "documentsbutton", "Documents")
    return driver.current_url


def form_lookup(driver, url):
    try:
        driver.get(url)
        # Get the link from the table cell directly after the cell that
        # contains the text '13F-HR'
        form_13F_HR = driver.find_element_by_xpath(
            "//*[contains(text(), '13F-HR')]/following::td")
        form_13F_HR.click()
        # Call wait_for_load to ensure that new page loads
        wait_for_load(driver, "formName", "Form 13F-HR")
        return driver.current_url
    except NoSuchElementException:
        print "No Form 13F-HR was found for this CIK or ticker"
        sys.exit()


def get_xml_url(driver, url):
    try:
        driver.get(url)
        element = driver.find_element_by_partial_link_text("able.xml")
        return element.get_attribute("href")
    except NoSuchElementException:
        print "No XML file was found for this Form 13F-HR"
        sys.exit()


# Selenium will look for an element on a page without waiting for the new page
# to load. This function ensures the new page loads
def wait_for_load(driver, div_id, text):
    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.text_to_be_present_in_element(
                (By.ID, div_id), text))
    except TimeoutException:
        print "The page timed out. There may be a problem with your search"
        sys.exit()


def stringify_xml(url):
    # Use requests library to retrieve source XML
    response = requests.get(url)
    # transform response into string
    return response.content


def create_etree(xml):
    # Create lxml etree element
    return etree.fromstring(xml)


def query_etree(etree):
    # Returns a list of top level elements from XML etree
    return etree.xpath(
        "//informationTable:infoTable",
        namespaces={
            "informationTable":
            "http://www.sec.gov/edgar/document/thirteenf/informationtable"})


def get_headers(xpath):
    headers = []
    # Only need to loop through one fund
    fund = xpath[0]
    # Get all children and grandchildren
    fund_tags = fund.xpath(".//*")
    # Set up counter to loop through fund_tags list
    i = 0
    for x in fund_tags:
        # Insert tag value into headers list
        headers.append(fund_tags[i].tag)
        # Increment counter up one
        i += 1
    return headers


# XMl tags come with namespace (see line below) - this trims those off
# {http://www.sec.gov/edgar/document/thirteenf/informationtable}nameOfIssuer
def trim_headers(headers):
    split_headers = []
    for x in headers:
        split_headers.append(x.split("}", 1)[-1])
    return split_headers


def get_fund_data(xpath):
    # Set up empty list for lists of child nodes' text (multidimensional list)
    funds_values = []
    # Iterate through each infoTable tag
    for fund in xpath:
        # Get all child and grandchild elements within the infoTable
        fund_text = fund.xpath(".//*")
        # Set up counter for second level of iteration
        i = 0
        # Create empty list for text values that will get put into funds_values
        fund_attributes = []
        # Insert the list of text values into the funds_values list
        funds_values.append(fund_attributes)
        # Iterate through children of infoTable getting their text values
        for x in fund_text:
            # Check for empty values and rewrite
            if "\n" not in fund_text[i].text:
                fund_attributes.append(fund_text[i].text)
            else:
                fund_attributes.append("empty")
            # Increment counter up one
            i += 1
    return funds_values


def write_tsv(headers, data):
    # Create TSV named as argument value
    tsvFilename = ("tmp/%s.tsv" % sys.argv[1])
    print "Writing TSV to", tsvFilename
    # Create or Open TSV
    with open(tsvFilename, "w") as tsv:
        col_names = '\t'.join(headers)
        tsv.write(col_names)
        tsv.write('\n')
        for values in data:
            string_values = '\t'.join(values)
            # Write data to TSV
            tsv.write(string_values)
            # Move to new line
            tsv.write("\n")

if __name__ == "__main__":
    main()
