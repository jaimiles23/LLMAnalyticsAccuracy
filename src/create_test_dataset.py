# /**
#  * @author [author]
#  * @email [example@mail.com]
#  * @create date 2024-02-04 11:37:20
#  * @modify date 2024-02-04 11:37:41
#  * @desc Used to create the test dataset. 
#  */


##########
# Imports
##########
import re

import pandas as pd
import numpy as np

import sqlite3
from sqlalchemy import create_engine, text

try:
    import constants as c
    import database_funcs
    import logger
    import setup_llm

except ModuleNotFoundError:
    import src.constants as c
    import src.logger as logger
    import src.database_funcs
    import src.setup_llm


##########
# Objects
##########
class testResults:
    TEST_SIMPLE_WHERE = 'last_update'
    TEST_JOIN_MAX = 'join_max'

    def clean_sql_query(query: str) -> str:
        """Cleans sql string for more efficient storage."""
        result = re.sub('\s+', ' ', query)
        if result[0] == " ":
            result = result[1:]
        return result


class SqlResults(testResults):
    ENGINE = database_funcs.connect_db(c.DB_NAME)

    def __init__(self, test_type: str, entity_name: str):
        self.test_type = test_type
        self.entity_name = entity_name

        self.query = SqlResults.clean_sql_query(self.get_corresponding_query())
        self.result = self.exec_sql()


    def get_corresponding_query(self):
        """sets query of the object"""
        predefined_queries = {
            SqlResults.TEST_SIMPLE_WHERE: f"SELECT last_update FROM dw_financial_institution_profiles AS p WHERE p.institution_name = '{self.entity_name}'", 
            SqlResults.TEST_JOIN_MAX: f"""
                SELECT max(total_assets) FROM dw_financial_institution_money AS m
                LEFT JOIN dw_financial_institution_profiles AS p
                    ON p.inst_id = m.inst_id
                WHERE p.institution_name = '{self.entity_name}'
                """,
        }
        sql = predefined_queries[ self.test_type]
        return sql


    def exec_sql(self) -> None:
        """Returns self of the SQL query"""
        with SqlResults.ENGINE.begin() as conn:
            sql = text(self.query)
            result = conn.execute(sql).fetchall()[0][0]
        
        if self.test_type == SqlResults.TEST_SIMPLE_WHERE:
            result = pd.to_datetime(result)

        return result


#### Test
# test = SqlResults("last_update", "The Southington Bank and Trust Company")
# print(test.result)
# print(test.query)


class LlmResults(testResults):
    DB_CHAIN = setup_llm.get_llm_db_chain()


    def __init__(self, test_type: str, entity_name: str):
        self.test_type = test_type
        self.entity_name = entity_name

        self.user_query = None
        self.sql_query = None
        self.result = None

        self.ask_llm()
        self.clean_result()


    def ask_llm(self):
        """Asks the LLM a naturally generated question & saves query/result."""
        # question = "What top 5 credit unions had the most total assets during quarter 3 in the year 2023"
        questions = {
            LlmResults.TEST_SIMPLE_WHERE: f"What was the last update for {self.entity_name}?", 
            LlmResults.TEST_JOIN_MAX: f"What is the maximum total assets {self.entity_name} ever had?"
        }
        
        question = questions[self.test_type]
        result = LlmResults.DB_CHAIN.invoke(question)

        self.user_query = result['query']
        self.sql_query = SqlResults.clean_sql_query( result['intermediate_steps'][-2]['sql_cmd']) 
             ## self.get_final_sql_step(result['intermediate_steps'])
        self.result = result['result']
        return

    ##### here incase we need to add back.
    # def get_final_sql_step(self, intermediate_steps: list) -> str:
    #     """Outputs the final SQL step from the LLM"""
    #     for i in range(len(intermediate_steps) -1, -1, -1):
    #         try:
    #             step = intermediate_steps[i].get('sql_cmd')
    #         except:
    #             step = intermediate_steps[i]
    #         print(step)

    #         if (
    #             step is not None 
    #             and "select" in step.lower()
    #             and "from" in step.lower()
    #         ):
    #             return step
    #     return "sql not found"


    def clean_result(self):
        if self.test_type == LlmResults.TEST_SIMPLE_WHERE:
            first_idx = self.result.find("'") + 1
            second_idx = self.result.find("'", first_idx)
            self.result = self.result[first_idx: second_idx]

            self.result = pd.to_datetime(self.result)
        elif self.test_type == LlmResults.TEST_JOIN_MAX:
        return


## Test
# test = LlmResults("last_update", "The Southington Bank and Trust Company")
# print(test.user_query, test.sql_query, test.result)


##########
# Dataframes
##########
def init_df_query_comparison() -> pd.DataFrame:
    """Creates a dataframe for comparing query tests"""
    data = {
        "test_type": [], 
        "sql_query": [], 
        "sql_result": [], 
        "llm_user_query": [], 
        "llm_sql_query": [], 
        "llm_result": [], 
        "correct_result": []
    }
    return pd.DataFrame(data)


##########
# Add result to dataframe
##########

def add_row_query_comparison(
        df: pd.DataFrame, 
        test_type: str, 
        sql_info: object, 
        llm_info: object
    ) -> pd.DataFrame:
    """Adds row of query comparison for SQL info & LLM info objects"""
    new_data = [
        test_type, 
        sql_info.query, 
        sql_info.result,
        llm_info.user_query, 
        llm_info.sql_query, 
        llm_info.result,
        int(sql_info.result == llm_info.result)
    ]
    print(new_data)
    df.loc[len(df.index)] = new_data
    return df


##########
# Create Queries
##########

def add_sql_tests(df: pd.DataFrame, entity_name: str) -> pd.DataFrame:
    """Adds testing for Simple SQL WHERE clauses"""
    tests = [
        testResults.TEST_SIMPLE_WHERE, 
        testResults.TEST_JOIN_MAX
    ]

    for test in tests:
        sql_info = SqlResults(test, entity_name)
        llm_info = LlmResults(test, entity_name)
        df = add_row_query_comparison(df, test, sql_info, llm_info)

    return df


def get_df_comparison(save_results: bool = True):
    """Creates & saves the comparison dataset for """
    ##### Create Comparison Dataset
    df = init_df_query_comparison()

    ##### Get Institution Test List
    engine = database_funcs.connect_db(c.DB_NAME)
    test_institutions = pd.read_sql_query("SELECT institution_name FROM dw_financial_institution_profiles LIMIT 10", engine)

    for idx in range(len(test_institutions.index)):
        inst_name = test_institutions['institution_name'].iloc[idx]
        print(inst_name)
        df = add_sql_tests(df, inst_name)

    print(df.shape)
    if save_results: 
        df.to_csv(c.FN_LLM_ACCURACY)
    return df


##########
# Main
##########
def main():
    df = get_df_comparison()

    return 



if __name__ == "__main__":
    main()