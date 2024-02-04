﻿# /**
#  * @author [author]
#  * @email [example@mail.com]
#  * @create date 2024-01-13 17:36:12
#  * @modify date 2024-01-13 17:36:12
#  * @desc Used to ingest NCUA data into the database
#  */


##########
# Imports 
##########

from datetime import date, datetime, timedelta
import io
import os
import logging 

import requests
import sqlite3
import urllib.parse

import pandas as pd

try:
    import constants as c
    import database_funcs 
    import database_setup
    import logger
except ModuleNotFoundError:
    import src.constants as c
    import src.database_funcs as database_funcs
    import src.database_setup as database_setup
    import src.logger as logger


##########
#  Helper Funcs
##########

def get_date_from_ncua_fn(file_dir: str) -> str:
    """Returns the data from the NCUA autogenerated custom query Filename:
    
    get_date_from_ncua_fn("5740_Sep-2023.xlsx") = 9/1/2023
    """
    fn = file_dir.split('\\')[-1]
    
    date_start = fn.index("_") + 1
    date_end = fn.index(".")
    if not date_start or not date_end:
        raise Exception("Unknown file format!")
    
    date_str = fn[date_start: date_end]
    date = datetime.strptime(date_str, "%b-%Y")
    return date


def get_ncua_data(fn: str, ws: str) -> pd.DataFrame:
    """Returns dataframe of NCUA Data"""
    df_ncua_data = pd.read_excel(fn, sheet_name = ws)
    fn_date = get_date_from_ncua_fn(fn)
    df_ncua_data['date_updated'] = fn_date
    return df_ncua_data


##########
#  Ingest NCUA Data 
##########
def get_all_ncua_files_to_process():
    """
    Find all NCUA files to process & resets them.

    TODO: we should also have a reset NCUA process, incase data is messed up. 
    This will delete all CU data, then ingest data from both processed and to process dirs
    """
    ncua_data_files = os.listdir(c.DIR_NCUA_DATA_TO_PROCESS) 
    ncua_data_files = [os.path.join(c.DIR_NCUA_DATA_TO_PROCESS, file) for file in ncua_data_files]
    return ncua_data_files


def ingest_all_ncua_data(engine: object):
    """Used to ingest NCUA data from a csv retrieved from the custom query
    
    Intake parameter is the database engine object.
    """
    ##### Ingest NCUA Data
    logging.info("Ingesting NCUA Data")

    ##### Setup dirs
    if not os.path.exists(c.DIR_NCUA_DATA_PROCESSED):
        os.makedirs(c.DIR_NCUA_DATA_PROCESSED)
   
    ##### Integrate all data
    files_to_process = get_all_ncua_files_to_process()
    for data_file in files_to_process:
        logging.info(f"Processing NCUA Data: {data_file}")
        if not data_file.endswith('.xlsx'):
            raise Exception(f"Not an excel file: {data_file}")

        with engine.begin() as conn:
            logging.debug("...getting NCUA Profile data")
            df_ncua_profile_info = get_ncua_data(data_file, 'ProfileGenInfo')
            df_ncua_profile_info.to_sql(c.DB_NCUA_PROFILE_EXTRACT_TBL, conn, if_exists='append', index = False)
            database_funcs.check_tbl(engine, c.DB_NCUA_PROFILE_EXTRACT_TBL)
    
            logging.debug("...getting NCUA Deposit data")
            df_ncua_deposit_info = get_ncua_data(data_file, 'Shares and Deposits')
            df_ncua_deposit_info.to_sql(c.DB_NCUA_Deposits_EXTRACT_TBL, conn, if_exists='append', index = False)
            database_funcs.check_tbl(engine, c.DB_NCUA_Deposits_EXTRACT_TBL)
        
        ## Archive Data File
        new_file_path = data_file.replace(c.DIR_NCUA_DATA_TO_PROCESS, c.DIR_NCUA_DATA_PROCESSED)
        os.rename(data_file, new_file_path)
    
    ## Finish
    logging.info("Finished ingesting NCUA Data")
    return


##########
#  Main
##########
def main():

    ##### Setup
    engine  = database_funcs.connect_db(c.DB_NAME)
    database_funcs.reset_db(engine)

    logging.info(f"Setting up {c.DB_NAME} database")
    database_setup.setup_extract_tables(engine)
    logging.info(f"Finished setting up {c.DB_NAME} database")

    ##### Ingest NCUA Data
    ingest_all_ncua_data(engine)
    return



if __name__ == "__main__":
    main()

