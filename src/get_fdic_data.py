# /**
#  * @author [author]
#  * @email [example@mail.com]
#  * @create date 2024-01-12 17:28:40
#  * @modify date 2024-01-12 17:28:40
#  * @desc Uses the FDIC API to get updated FDIC data.
# ## FDIC Data
# Use this FDIC [API](https://banks.data.fdic.gov/docs/#/Structure/searchInstitutions) to get new data.

# Filters will include:
# - Only specified columns
# - Only updated data

# NOTE: create catch; if anything breaks, delete all data past the last update.
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
except ModuleNotFoundError:
    import src.constants as c
    import src.database_funcs as database_funcs
    import src.database_setup as database_setup
    import src.logger as logger
    pass


##########
#  FDIC Data Functions
##########
## NOTE: with these constants & enough methods, might consider creating a class to dynamically construct URL


def create_request_url(
    engine : object,
    data_cols: list, 
    limit: int,
    offset: int 
) -> str:
    """Dynamically create requests URL for getting data from FDIC website.
    f'filters=DATEUPDT%3A%5B%22{last_update}%22%20TO%20%{today}%22%5D',
    """
    url_base = 'https://banks.data.fdic.gov/api/institutions?'
    
    ## DT Filters
    dt_delta = timedelta(days=1)
    dt_filter_start = (database_funcs.get_last_update(engine) + dt_delta).strftime('%Y-%m-%d')
    df_filter_end = (datetime.today() - dt_delta).strftime('%Y-%m-%d')
    dt_filters = f'DATEUPDT:["{dt_filter_start}" TO "{df_filter_end}"]'
    
    ## Sanitize
    filters_sanitized = urllib.parse.quote(dt_filters) 
    data_cols_sanitized = urllib.parse.quote(data_cols) 
    
    url_parameter_list = [
        f'filters={filters_sanitized}',
        f'fields={data_cols_sanitized}',
        'sort_by=DATEUPDT',
        'sort_order=ASC',   ## Use ascending order in case script fails, then don't miss hx data.
        f'limit={limit}',
        f'offset={offset}',
        'format=csv',
        'download=true',
        'filename=data_file'
    ]
    url = url_base + '&'.join(url_parameter_list)
    logging.debug(url)
    return url


def ingest_fdic_api_data(engine: object):
    """
    Function to get FDIC Data using the API.
    """
    logging.info("Ingesting FDIC Data")
    last_update_prev = database_funcs.get_last_update(engine)
    fdic_defs_use_tbl_cols = ','.join(database_setup.get_fdic_extract_tbl_cols())

    flag_check_new_fdic_data = True
    iterations = 0
    increment = 500  ## This can be much larger, limit 10,000. Low for POC. Also infrequent updates.
    num_rows = 0

    while flag_check_new_fdic_data:
        url = create_request_url(
            engine = engine,
            data_cols = fdic_defs_use_tbl_cols, ## TODO: function to get this.
            limit = increment, 
            offset = increment * (iterations)
        )
        response = requests.get(url)
        logging.debug(response.status_code)
        assert response.status_code == 200 
        
        if response.text == "":
            flag_check_new_fdic_data = False
            logging.debug("No more data found.")
            break
        
        url_data = response.content
        fdic_data = pd.read_csv(io.StringIO(url_data.decode('utf-8')))
        fdic_data.drop('ID', axis = 1, inplace = True)  ## N
        with engine.begin() as conn:
            fdic_data.to_sql(c.DB_FDIC_EXTRACT_TBL, conn, if_exists='append', index = False)

        iterations += 1
        num_rows += fdic_data.shape[0]

    last_update_new = database_funcs.get_last_update(engine)
    logging.info(f"Inserted a total of {num_rows} new rows. Used {iterations} iterations of {increment} rows")
    logging.info(f"Adding data to FDIC Table. Previous Last Update: {last_update_prev}, New Last Update: {last_update_new}")

    logging.info("Finished ingesting FDIC Data")
    confirm_last_update(engine)
    return 


def confirm_last_update(engine: object) -> None:
    """confirms the last update on the FDIC table"""
    result = database_funcs.get_last_update(engine)
    msg_last_update = f"Last FDIC Data Update: {result}"
    logging.info(msg_last_update)
    return


##########
#  Main
##########
def main():
    engine = database_funcs.connect_db(c.DB_NAME)
    database_funcs.reset_db(engine)

    logging.info(f"Setting up {c.DB_NAME} database")
    database_setup.setup_extract_tables(engine)
    logging.info(f"Finished setting up {c.DB_NAME} database")


    # database_funcs.del_recent_update_data(engine)  ## Used for testing
    ingest_fdic_api_data(engine)
    return


if __name__ == "__main__":
    main()

