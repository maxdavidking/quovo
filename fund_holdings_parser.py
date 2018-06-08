from lxml import etree
from lxml import html
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
    requests_version = edgar_lookup(sys.argv[1])
    xml_list = requests_to_xml(requests_version, "/Archives")
    good_url = requests_url_fix(xml_list)
    final_url = requests_final_url(good_url)
    # Get XML and convert to string and then etree
    xml_string = stringify_xml(final_url)
    xml_tree = create_etree(xml_string)
    funds = query_etree(xml_tree)
    # Store XML tags as headers for TSV
    headers = get_headers(funds)
    reduced_headers = trim_headers(headers)
    # Get XML text as data for TSV
    fund_data = get_fund_data(funds)
    # Write to TSV file
    write_tsv(reduced_headers, fund_data)


# Is this fine hardcoded?
def edgar_lookup(cik):
    payload = {
        'CIK':cik,
        'action':'getcompany',
        'type':'13f-hr',
        'owner':'exclude',
        'count':100
    }
    url = "https://www.sec.gov/cgi-bin/browse-edgar?"
    return requests.get(url, payload)


# Get list of all links to 13f-hr form filings
def requests_to_xml(request, query_string):
    webpage = html.fromstring(request.content)
    return webpage.xpath('//a[contains(@href,"%s")]/@href' % query_string)


# Add base URL to relative links to 13f-hr forms
def requests_url_fix(xml_list):
    base_url = "https://www.sec.gov"
    archives_url = []
    for xml in xml_list:
        full_url = base_url + xml
        archives_url.append(full_url)
    return archives_url


# Add parameter to specify how many you want to run
def requests_final_url(url_list):
    xml_url = requests.get(url_list[0])
    form_13f = html.fromstring(xml_url.content)
    xml_file = form_13f.xpath('//a[contains(@href,"Table.xml")]/@href')
    final_string = "https://www.sec.gov" + xml_file[1]
    return final_string


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
