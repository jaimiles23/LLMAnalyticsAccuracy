##########
# Imports
##########

import logging
import textwrap

import pandas as pd
import numpy as np
from sqlalchemy import engine, text

try:
    import logger 
    import constants as c
    import database_funcs

except ModuleNotFoundError:
    import src.logger as logger
    import src.constants as c
    import src.database_funcs as database_funcs


##########
# Data Pipeline
##########
def drop_transform_tables(engine: object):
    """Drops transformation tables for reset"""
    logging.info("Dropping transformation tables for reset")
    database_funcs.helper_read_exec_sql_file(c.FN_SQL_CREATE_TBL_PROFILES, engine)
    database_funcs.helper_read_exec_sql_file(c.FN_SQL_CREATE_TBL_PROFILES, engine)
    return


def create_transformed_tables(engine: object):
    """Updates financial institution table."""
    HAS_PROFILES_TBL =  database_funcs.check_tbl_exists(engine, c.DB_DW_TBL_PROFILES)
    HAS_MONEY_TBL = database_funcs.check_tbl_exists(engine, c.DB_DW_TBL_MONEY)

    if not HAS_PROFILES_TBL:
        logging.info(f"Creating {c.DB_DW_TBL_PROFILES} Table")
        database_funcs.helper_read_exec_sql_file(c.FN_SQL_CREATE_TBL_PROFILES, engine)
    
    if not HAS_MONEY_TBL:
        logging.info(f"Creating {c.DB_DW_TBL_MONEY} Table")
        database_funcs.helper_read_exec_sql_file(c.FN_SQL_CREATE_TBL_MONEY, engine)
    return


def insert_new_profiles(engine: object):
    """Updates financial institution table."""
    logging.info("Inserting Transform Table")
    database_funcs.helper_read_exec_sql_file(c.FN_INSERT_PROFILES_BANKS, engine)
    database_funcs.helper_read_exec_sql_file(c.FN_INSERT_PROFILES_NCUA, engine)
    return


def update_new_profiles(engine: object):
    """Updates financial institution table."""
    logging.info("Inserting Transform Table")
    database_funcs.helper_read_exec_sql_file(c.FN_UPDATE_PROFILES_BANKS, engine)
    database_funcs.helper_read_exec_sql_file(c.FN_UPDATE_PROFILES_NCUA, engine)
    return


def insert_new_finances(engine: object):
    """Updates financial institution table."""
    logging.info("Inserting Transform Table")
    database_funcs.helper_read_exec_sql_file(c.FN_INSERT_MONEY_BANKS, engine)
    database_funcs.helper_read_exec_sql_file(c.FN_INSERT_MONEY_NCUA, engine)
    return


def transform_fin_inst_data(engine: object, reset_transforms: bool):
    """
    As needed:
    - Creates transformed tables
    - inserts new profiles into tables
    - updates profiles
    - inserts new financials
    """
    if reset_transforms:
        drop_transform_tables(engine)
    
    create_transformed_tables(engine)
    insert_new_profiles(engine)
    update_new_profiles(engine)
    insert_new_finances(engine)
    return


##########
# Main
##########

def main():
    engine = database_funcs.connect_db(c.DB_NAME)
    transform_fin_inst_data(engine, True)
    return


if __name__ == "__main__":
    main()


