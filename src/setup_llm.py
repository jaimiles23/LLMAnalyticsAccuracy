
##########
# Imports
##########

from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain_openai import OpenAI

try:
    import logger 
    import constants as c

except ModuleNotFoundError:
    import src.logger as logger
    import src.constants as c



##########
# LLM
##########

def get_open_api_key() -> str:
    """Reads open api key from the secrets.txt file.
    
    To use this, you must create your own "secrets.txt" file with your open API key.
    """
    
    with open(c.FN_SECRETS, 'r') as f_in:
        open_api_key = f_in.read()
    return open_api_key




def get_llm_db_chain():
    """Returns LLM Database chain"""
    OPEN_API_KEY = get_open_api_key()
    
    db_connection_name = f'sqlite+pysqlite:///{c.DB_NAME}'
    db = SQLDatabase.from_uri(
        db_connection_name,
        include_tables = [ 
            c.DB_DW_TBL_PROFILES,
            c.DB_DW_TBL_MONEY
        ]
    )
    llm = OpenAI(temperature=0, verbose=True, openai_api_key=OPEN_API_KEY)
    db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)
    return db_chain


def ask_questions(db_chain: object):
    """asks the LLM a question"""
    # question = "What top 5 credit unions had the most total assets during quarter 3 in the year 2023"
    question = "Start"
    while question.lower() != "quit":
        question = input("Enter your question or type 'quit': ")
        if question != 'quit': 
            db_chain.invoke(question)
    return


##########
# Main
##########
def main():
    """Instantiate LLM and have user ask it a question"""
    db_chain = get_llm_db_chain()


    # question = "describe the available data"
    ask_questions(db_chain) 
    return



if __name__ == "__main__":
    main()

