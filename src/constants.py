##########
# Imports 
##########
import os 

DIR_PATH = os.path.dirname(os.path.dirname(__file__))


# ##########
# # Helper Functions 
# ##########
def get_dir(relative_path: str) -> str:
    """Returns the absolute path of the file.
    
    Uses os.path.sep for separation.
    """
    # print(os.path.sep)          ## for Docker image too
    new_relative_path = relative_path.replace('\\', os.path.sep)
    absolute_path = os.path.join(DIR_PATH, new_relative_path)
    return absolute_path



##########
# Database 
##########
DB_NAME = r"data\financial_landing.db"

## Load Tables
DB_FDIC_EXTRACT_TBL = "load_fdic_institutions"
DB_NCUA_PROFILE_EXTRACT_TBL = "load_ncua_profiles"
DB_NCUA_Deposits_EXTRACT_TBL = "load_ncua_shares"

## Data Warehouse
DB_DW_TBL_PROFILES = "dw_financial_institution_profiles"
DB_DW_TBL_MONEY = "dw_financial_institution_money"


## All Tables
DB_ALL_TBLS = (
    DB_FDIC_EXTRACT_TBL,
    DB_NCUA_PROFILE_EXTRACT_TBL,
    DB_NCUA_Deposits_EXTRACT_TBL,
    DB_DW_TBL_PROFILES,
    DB_DW_TBL_MONEY
)


##########
# Data File 
##########

##### FDIC
FN_FDIC_INST_DEFS = get_dir(r"data\Data_Banks\institutions_definitions.xlsx")
FN_FDIC_INST_DATA = get_dir(r"data\Data_Banks\institutions.xlsx")

##### NCUA
DIR_NCUA_DATA_TO_PROCESS =  get_dir(r"data\Data_NCUA\data_to_process")
DIR_NCUA_DATA_PROCESSED =   get_dir(r"data\Data_NCUA\data_processed")

##### LLM Test Dataset

FN_LLM_ACCURACY = get_dir(r"data\llm_accuracy.csv")



##########
# Columns
##########

##### NCUA
NCUA_PROFILE_COLS = "cu_number, CUName, City, State, URL, TotalAssets, date_updated"
NCUA_DEPOSIT_COLS = "Charter,A455,A451,A013B1,A902A,A013,A018,A908B1,A018A,A460,A908A,A013A,A454,ASH0018,A452,A018B1,A902,A908C,A630A,A657A,A630,ASH0013,A657,A966,A644,A880A,A458,A906B2,A911,A453,A906B1,A906A,A908B2,A906C,A880B1,A639,A013B2,A880,ASH0880,A880B2,A457,A643,A911A,A638,A018B2,A631,A641,A630B2,A630B1,A632,A636,date_updated"




##########
# SQL Transform Data Files
##########

FN_SQL_CREATE_TBL_PROFILES = get_dir(r"src\sql\create\create_tbl_profiles.sql")
FN_SQL_CREATE_TBL_MONEY = get_dir(r"src\sql\create\create_tbl_money.sql")

FN_INSERT_PROFILES_BANKS = get_dir(r"src\sql\transforms\insert_profiles_banks.sql")
FN_INSERT_PROFILES_NCUA = get_dir(r"src\sql\transforms\insert_profiles_ncua.sql")

FN_UPDATE_PROFILES_BANKS = get_dir(r"src\sql\transforms\update_profiles_banks.sql")
FN_UPDATE_PROFILES_NCUA = get_dir(r"src\sql\transforms\update_profiles_ncua.sql")

FN_INSERT_MONEY_BANKS = get_dir(r"src\sql\transforms\insert_money_banks.sql")
FN_INSERT_MONEY_NCUA = get_dir(r"src\sql\transforms\insert_money_ncua.sql")

FN_BQ_DECLINE_INST = get_dir(r"src\sql\business_questions\decline_insts.sql")
FN_BQ_ACTIVE_BY_ASSETS = get_dir(r"src\sql\business_questions\active_by_assets.sql")


FN_SQL_LLM_INSTS = get_dir(r"src\sql\llm_tests\get_top_insts.sql")


##########
# Secrets Filname
##########
FN_SECRETS = get_dir("secrets.txt")