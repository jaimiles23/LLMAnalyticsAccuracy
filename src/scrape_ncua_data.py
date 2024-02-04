# **Notes**:

# Below shows a proof of concept on 2 ways of automatically retrieving the quarterly call report data:
# 1. Using HTML to webscrape the call report data and find the hyperlink references
# 2. Dynamically constructing the URLs
    
# However, I did not have a meaningful understanding of the data within the scope of this evaluation. After building these proofs of concepts, I used the custom query to get quarterly report data on the specified metrics. 


##########
# Imports 
##########

from datetime import date, datetime, timedelta
import io
import os
import bs4

import requests
import sqlite3
import urllib.parse
import logging

import pandas as pd

import constants as c
import database_funcs 
import database_setup
import logger 


##########
# Imports 
##########


def scrape_ncua_html():
    """Shows beautiful soup scraping of the NCUA webpage to identify the .zip file downloads"""
    WEBSITE_NCRUA_REPORTS = r'https://ncua.gov/analysis/credit-union-corporate-call-report-data/quarterly-data'
    res = requests.get(WEBSITE_NCRUA_REPORTS)
    soup = bs4.BeautifulSoup(res.text)
    tbl_info: list = soup.select('td')
    for info in tbl_info:
        print(info)


def download_ncua_data(year, month):
    """Downloads the NCUA data
    
    ### Dynamically Construct URL Proof
    After June 2015**, the URLs follow the below format. Instead, we can dynamically construct these URLs by adjusting the date and quarter. 
        https://ncua.gov/files/publications/analysis/call-report-data-2020-12.zip

    NOTE: this does NOT check for revised data; a better implementation would leverage the above beautiful soup concept to check for revised datasets. 
    When something is revised, it would delete all data and reinsert.
    """
    url = f'https://ncua.gov/files/publications/analysis/call-report-data-{year}-{month:0>{2}}.zip'
    logging.info(url)

    parent_dir = os.path.dirname(os.path.dirname( __file__ ))
    path_folder = r'data\Data_NCUA\zip_files'
    fn = f'{year}_{month}_ncua_callreport.zip'
    file_path = os.path.join(parent_dir, path_folder, fn)
    logging.info(f"Downloading {file_path}")

    try: 
        urllib.request.urlretrieve(url, file_path)
    except:  ## TODO: make more robust check
        print(fn)
        print(f"Could not download {year} - {month}. Double check this is published data.")
    return


##########
# Main 
##########

def main():
    """Download NCUA Data"""

    ##### Print HTML  for scraping reports
    scrape_ncua_html()

    ##### Download zip files from NCUA
    flag_download_data = True
    report_year = 2023 ##2016             ## This is the first full year of report URLs following this format
    quarter_months: tuple = (3, 6, 9, 12)
    now = datetime.today()

    while flag_download_data: 
        for month in quarter_months:
            report_date = datetime(report_year, month, 1)
            if report_date > now:
                flag_download_data = False
                break
            
            print(f"Downloading data for {report_year}-{month}")
            download_ncua_data(report_year, month)    
        
        report_year += flag_download_data    ## Increment year for next report


if __name__ == "__main__":
    main()

