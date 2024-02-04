# /**
#  * @author Jai Miles
#  * @email [jaimiles23@gmail.com]
#  * @create date 2024-01-12 16:06:22
#  * @modify date 2024-01-12 16:06:54
#  * @desc Used to 
#  */



########## 
# Imports
##########

from datetime import date, datetime, timedelta
import bs4
import io
import matplotlib.pyplot as plt
import numpy as np
import os
import logging
import time

import pandas as pd
import requests
import sqlalchemy
import sqlite3
import urllib.parse

from src import *


##########
# Main-
##########
def run_data_pipeline(reset: bool):
    start_time = time.time()
    if reset:       ## For testing
        database_funcs.reset_db()

    ##### Connection
    engine = database_funcs.connect_db(c.DB_NAME)

    ##### Setup database
    database_setup.setup_extract_tables(engine)


    ##### Ingest FDIC Data
    database_funcs.del_recent_update_data(engine)  ## test FDIC API & get data over time
    get_fdic_data.ingest_fdic_api_data(engine)

    ##### Ingest NDIC Data
    get_ncua_data.ingest_all_ncua_data(engine)
    
    #### Transform the data into a single table
    transform_data.transform_fin_inst_data(engine, reset_transforms = False)

    ##### Check Business Result Queries
    check_business_questions.check_all_business_questions(engine, print_text = True)

    ### Wrapup
    completion_msg = f"Completed Pipeline in {time.time() - start_time}"
    logging.info(completion_msg)
    print(completion_msg)
    return



##########
# Main
##########
def main(reset: bool):
    """ Run data pipeline & LLM questions as needed"""
    run_data_pipeline(reset = reset)
    db_chain = setup_llm.get_llm_db_chain()
    
    setup_llm.ask_questions(db_chain)
    return


if __name__ == "__main__":
    reset = True
    main(reset)

