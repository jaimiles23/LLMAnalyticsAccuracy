
##########
# Imports 
##########
from datetime import datetime
import logging 
import os
import textwrap

import pandas as pd
import sqlite3
from sqlalchemy import create_engine, text

try:
    import constants as c
    import logger
except ModuleNotFoundError:
    import src.constants as c
    import src.logger as logger
    pass


##########
# Connect to Database
##########
def connect_db(name: str) -> object:
    """Connects to the database and returns data base connection"""
    logging.info(f"Connecting to {c.DB_NAME}")
    # con = sqlite3.connect(
    #     database = name, 
    #     isolation_level = None,
    #     # autocommit = True
    # )
    # cur = con.cursor()
    
    db_connection_name = f'sqlite+pysqlite:///{name}'
    db_connection_name = f'sqlite:///{name}'
    engine = create_engine(
        db_connection_name, 
        echo=True
        )
    # db_connection = engine.connect()   
    return engine


##########
# Setup
##########
def check_tbl_exists(engine: object, tbl_name: str):
    """Checks if table exists in the SQLite db"""
    with engine.connect() as conn:
        sql = text(f"SELECT name FROM sqlite_master WHERE name = '{tbl_name}'")
        res = conn.execute(sql)
        conn.commit()
    flag_exists = True if res.fetchone() != None else False
    
    ## TODO: Add unit tests, e.g., below
    # assert check_tbl_exists(cur, "movie") == True
    # assertcheck_tbl_exists(cur, "obviouslyFakeTableName") == False
    logging.debug(f"{tbl_name} exists: {flag_exists}")
    return flag_exists


def create_tbl(engine: object, tbl_name: str, cols: str):
    """Creates a table in the data base. """
    with engine.begin() as conn:
        sql_create_tbl = text(f"CREATE TABLE {tbl_name}({cols})")
        conn.execute(sql_create_tbl)
    
    flag_created = check_tbl_exists(engine, tbl_name)
    assert flag_created == True
    logging.debug(f"Created table {tbl_name}")
    return flag_created


def check_tbl( engine: object, tbl_name: str):
    """Checks if table exists in the SQLite db"""
    with engine.begin() as conn:
        sql = text(f"SELECT * FROM {tbl_name} LIMIT 5")
        df_rows = pd.read_sql(sql, conn)
    logging.debug(f"f{tbl_name} shape: {df_rows.shape}")
    return df_rows


def get_last_update(engine: object, flag_dt: bool = True):
    """Returns the date of the FDIC update
    
    TODO: generalize this function more; NEVER use constants.
    """

    with engine.begin() as conn:
        sql = text(f"SELECT MAX(DATEUPDT) FROM {c.DB_FDIC_EXTRACT_TBL} LIMIT 5")          
        ## TODO: modulate this more, e.g., tbl as param, can have LUT of update cols in a dict
        res = conn.execute(sql)
        result = res.fetchone()[0]

    if flag_dt:
        # result = datetime.strptime(result, '%Y-%m-%d %H:%M:%S')
        result = pd.to_datetime(result)
    return result

##########
# SQL Files
##########

def helper_read_exec_sql_file(fn: str, engine: object) -> None:
    """Reads & Executes a SQL file"""
    with open(fn, 'r') as f_in:
        lines = f_in.read()
        sql_command = textwrap.dedent("""{}""".format(lines))
        logging.debug(sql_command)
    
    with engine.begin() as conn:
        sql = text(sql_command)
        result = conn.execute(sql)
    return result

##########
# Reset data 
##########
def del_tbl(engine: object, tbl_name: str):
    """Deletes passed table"""
    # tbl_exists = check_tbl_exists(engine, tbl_name)
    # if not tbl_exists:
    #     logging.debug(f"Tried deleting table {tbl_name} but does not exist!")
    #     return 

    with engine.begin() as conn:
        tbl_exists = check_tbl_exists(engine, tbl_name)
        if not tbl_exists: 
            logging.debug(f"{tbl_name} does not exist!")
            return
    
    with engine.begin() as conn:
        sql = text(f"DROP TABLE {tbl_name}")
        res = conn.execute(sql)
        assert check_tbl_exists(engine, tbl_name) == False

    logging.debug(f"Deleted table {tbl_name}")
    return


def reset_db():
    """Drops all tables in the database"""
    # logging.info(f"Deleting all tables in {c.DB_NAME}")
    # for tbl in c.DB_ALL_TBLS:
    #     del_tbl(engine, tbl)

    logging.info(f"Deleting {c.DB_NAME}")
    try:
        os.remove(c.DB_NAME)
    except FileNotFoundError:
        logging.info(f"{c.DB_NAME} does not exist; cannot delte")
    return 


def del_recent_update_data(engine: object):
    """Deletes recent update data; this allows testing of the API"""
    last_update_prev = get_last_update(engine)

    with engine.begin() as conn:
        sql = text(f"DELETE FROM {c.DB_FDIC_EXTRACT_TBL} WHERE DATEUPDT >= '2023-01-01'")       ## TODO: make this a dynamic call
        res = conn.execute(sql)

    last_update_new = get_last_update(engine)
    logging.info(f'Deleting data from table. Prev update: {last_update_prev}, new update: {last_update_new}')
    return


##########
# Main 
##########
def main():
    """ Runs all database setup"""
    engine = connect_db(c.DB_NAME)

    with engine.begin() as conn:
        test_code = text(f'SELECT * FROM sqlite_master')
        result = conn.execute(test_code)
     
    for r in result.fetchall():
        print(r)
    
    return


if __name__ == "__main__":
    main()

