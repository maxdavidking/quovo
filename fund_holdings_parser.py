from lxml import etree
import requests
import csv

#Open new TSV file to save data in tab separated format
ticker_data = open('tmp/ticker.tsv', 'w')
csvwriter = csv.writer(ticker_data, delimiter='\t')
