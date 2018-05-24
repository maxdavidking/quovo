# Overview
The fund_holdings_parser is a script to get XML data from the 13F-HR forms
filed in EDGAR (https://www.sec.gov/edgar/searchedgar/companysearch.html)
and convert that data into a tab separated value file (TSV).

# Instructions
1. Get a valid ticker symbol or CIK number from http://morningstar.com/ or
lipperweb.com
  * Some working CIK's are:
    * 0001166559
    * 0000102909
    * 0001006438
2. Pass your CIK or ticker symbol to the script as an argument. Run the script
with the command:
  * $ python fund_holdings_parser.py <CIK>
3. The output is stored as a .tsv file in the tmp/ folder

# Notes
* This script collects all children and grandchildren nodes of the infoTable
parent node. This means that empty nodes that only exist to create grandchildren
are collected and returned as 'empty.'
* If any of EDGAR's URLs, HTML structure or file naming conventions change this
script could break. Some values are hardcoded into the script in order to crawl
through the site
* This script only returns the first 13F-HR form found. It needs to be
modified to get a specific form, or all forms.
* This script only returns 13F-HR forms. It needs to be modified to get other
types of forms.
