# /**
#  * @author [author]
#  * @email [example@mail.com]
#  * @create date 2024-01-15 22:02:40
#  * @modify date 2024-01-15 22:02:40
#  * @desc Script used to generate author information
#  */


##########
# Imports
##########
from datetime import datetime
import logging 
import os

import pandas as pd
import sqlite3
from sqlalchemy import create_engine, text

try:
    import constants as c
    import logger
    import database_funcs
except ModuleNotFoundError:
    import src.constants as c
    import src.logger as logger
    import src.database_funcs as database_funcs


##########
# Business Questions
##########
def check_active_institutions_by_tier(engine:object, print_text:bool = True):
    """
    How many banks and credit unions are active by asset tier, total assets between $500M and $1B

    TODO: not hard code this.    
    """
    result = pd.DataFrame(database_funcs.helper_exec_sql_file(c.FN_BQ_ACTIVE_BY_ASSETS, engine).fetchall())
    msg = "Active institutions by tier"

    logging.debug(msg)
    logging.debug(result)

    if print_text:
        print(msg)
        print(result.head())
    return result


def check_declining_instituions(engine:object, print_text:bool = True):
    """
    Check institutions that declined in the last quarter
    """
    result = pd.DataFrame(database_funcs.helper_exec_sql_file(c.FN_BQ_DECLINE_INST, engine).fetchall())
    msg = "Declining Institutions"

    logging.debug(msg)
    logging.debug(result)
    
    if print_text:
        print(msg)
        print(result.head())
    return result


def check_all_business_questions(engine, print_text: bool = True): 
    """Checks all defined business questions"""
    check_active_institutions_by_tier(engine, print_text)
    check_declining_instituions(engine, print_text)
    return


##########
# Main
##########
def main():
    """ Runs all database setup"""
    engine = database_funcs.connect_db(c.DB_NAME)

    check_all_business_questions(engine, print_text= True)
    return


if __name__ == "__main__":
    main()

