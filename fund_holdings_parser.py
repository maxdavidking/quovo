from lxml import etree
import requests
import csv

#Open new TSV file to save data in tab separated format
ticker_data = open('tmp/ticker.tsv', 'w')
csvwriter = csv.writer(ticker_data, delimiter='\t')

#Hard code link directly to XML for now
link = "https://www.sec.gov/Archives/edgar/data/1166559/000110465918033472/a18-13444_1informationtable.xml"
