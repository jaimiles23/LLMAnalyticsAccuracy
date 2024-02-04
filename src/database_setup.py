﻿
##########
# Imports 
##########
from datetime import datetime
import sqlite3
import pandas as pd
import logging

try:
    import logger 
    import constants as c
    import database_funcs 

except ModuleNotFoundError:
    import src.logger as logger
    import src.constants as c
    import src.database_funcs as database_funcs


##########
# FDIC Extract Tables 
##########
def get_fdic_extract_tbl_cols() -> str:
    """
    Returns the table columns for the FDIC extract.
    """
    df_fdic_defs = pd.read_excel(c.FN_FDIC_INST_DEFS)
    df_fdic_defs_USE = df_fdic_defs[df_fdic_defs["Use"] == 1]        ## TODO: define constants above.
    df_fdic_defs_use_tbl_cols = df_fdic_defs_USE['Variable Name']
    return df_fdic_defs_use_tbl_cols


def setup_fdic_extract_table(
        engine: object
        ):
    """
    Creates landing tables for the FDIC banking data. 
    
    Input: database consor.
    """
    logging.info(f"Creating FDIC Extract Tables")
    ### Get relevant data                ## TODO: might modulate this further too
    df_fdic_defs_use_tbl_cols = get_fdic_extract_tbl_cols()
    fdic_defs_use_tbl_cols: str = ','.join(df_fdic_defs_use_tbl_cols)
   
    ## Create Table
    database_funcs.create_tbl(engine, c.DB_FDIC_EXTRACT_TBL, fdic_defs_use_tbl_cols)
    assert database_funcs.check_tbl_exists(engine, c.DB_FDIC_EXTRACT_TBL) == True

    ## Insert Hx Data
    df_fdic_data_hx = pd.read_excel(c.FN_FDIC_INST_DATA)
    df_fdic_data_hx_use = df_fdic_data_hx[df_fdic_defs_use_tbl_cols]
    with engine.begin() as conn:
        df_fdic_data_hx_use.to_sql(c.DB_FDIC_EXTRACT_TBL, conn, if_exists='replace', index = False)
        
    
    df_result = database_funcs.check_tbl(engine, c.DB_FDIC_EXTRACT_TBL)
    logging.debug(df_result.shape)
    assert df_result.shape[0] == 5      ### TODO: add asserts about the count of the database. 

    return


##########
# NCUA Extract Tables 
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
    logging.debug(f"Date from {fn}: {date}")
    return date


def get_ncua_data(fn: str, ws: str) -> pd.DataFrame:
    """Returns dataframe of NCUA Data"""
    logging.info(f"Reading NCUA {ws} data")
    df_ncua_data = pd.read_excel(fn, sheet_name = ws)
    fn_date = get_date_from_ncua_fn(fn)
    df_ncua_data['date_updated'] = fn_date
    return df_ncua_data


##########
# Setup Extract Tables 
##########
def setup_extract_tables(engine: object):
    """Sets up extract tables if they do not exist"""

    ## FDIC Tables
    HAS_FDIC_INST_LAND_TBL = database_funcs.check_tbl_exists(engine, c.DB_FDIC_EXTRACT_TBL)
    if not HAS_FDIC_INST_LAND_TBL:
        logging.info(f"Creating {c.DB_FDIC_EXTRACT_TBL}")
        setup_fdic_extract_table(engine)
    else:
        logging.info(f"{c.DB_FDIC_EXTRACT_TBL} already exists")
    
    ## NCUA Tables
    HAS_NCUA_PROFILE_LAND_TBL = database_funcs.check_tbl_exists(engine, c.DB_NCUA_PROFILE_EXTRACT_TBL)
    if not HAS_NCUA_PROFILE_LAND_TBL:
        logging.info(f"Creating {c.DB_NCUA_PROFILE_EXTRACT_TBL}")
        database_funcs.create_tbl(engine, c.DB_NCUA_PROFILE_EXTRACT_TBL, c.NCUA_PROFILE_COLS)
        database_funcs.check_tbl(engine, c.DB_NCUA_PROFILE_EXTRACT_TBL)
    else:
        logging.info(f"{c.DB_NCUA_PROFILE_EXTRACT_TBL} already exists")
    
    HAS_NCUA_DEPOSIT_LAND_TBL = database_funcs.check_tbl_exists(engine, c.DB_NCUA_Deposits_EXTRACT_TBL)
    if not HAS_NCUA_DEPOSIT_LAND_TBL:
        logging.info(f"Creating {c.DB_NCUA_Deposits_EXTRACT_TBL}")
        database_funcs.create_tbl(engine, c.DB_NCUA_Deposits_EXTRACT_TBL, c.NCUA_DEPOSIT_COLS)
        database_funcs.check_tbl(engine, c.DB_NCUA_Deposits_EXTRACT_TBL)
    else:
        logging.info(f"{c.DB_NCUA_Deposits_EXTRACT_TBL} already exists")
    
    logging.info(f"Finished setting up {c.DB_NAME} database")
    return


##########
# Main 
##########
def main():
    """Runs all database setup"""
    engine = database_funcs.connect_db(c.DB_NAME)
    database_funcs.reset_db(engine)

    setup_extract_tables(engine)
    return



if __name__ == "__main__":
    main()

