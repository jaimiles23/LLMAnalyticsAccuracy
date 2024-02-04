# FDIC & NCUA Data Pipeline

- [FDIC \& NCUA Data Pipeline](#fdic--ncua-data-pipeline)
- [About](#about)
- [Setup](#setup)
- [Data](#data)
  - [FDIC Data](#fdic-data)
  - [NCUA Data](#ncua-data)
    - [Automating Data Downloads](#automating-data-downloads)
    - [Custom Query Download](#custom-query-download)
- [Architectural Design](#architectural-design)
  - [Tech Stack](#tech-stack)
  - [Data Pipeline](#data-pipeline)
    - [Data Lineage](#data-lineage)
    - [Data Model](#data-model)
    - [Data Governance](#data-governance)
- [TODOs:](#todos)


# About
American Financial Institutions are primarily regulated by 2 major external bodies:
- FDIC (Federal Deposit Insurance Corporation)
- NCUA (National Credit Union Administration)

This project ingests data from these two sources into a SQL database. The database has the following instituion data:
- Type: Bank or Credit Union
- Charter Number:
- Web Domain
- City
- State
- Total Assets
- Total Deposits

**Note: total amounts are measured at the end of each calendar quarter**

# Setup
*note*: example commands for windows cmd

1. Clone repo to local files
2. Open CMD in cwd
3. run: `python -m venv venv `
4. run: `pip install -r requirements.txt`
5. Update `constants.py` to use your system's absolute path
6. Insert an openAI API Key into a "secrets.txt" file in the main folder
7. run: `python -m main.py`


# Data
Both regulating organizations make their data publicly available:
- FDIC 
    - [API Documenation](https://banks.data.fdic.gov/docs/)
- Credit Unions:
    - [Reports of all Data](https://ncua.gov/analysis/credit-union-corporate-call-report-data/quarterly-data) 
    - [Custom Query Tool](https://webapps2.ncua.gov/CustomQuery/CUSelect.aspx)

This data pipeline ingests data from both sources into a SQLite database. This pipeline can be run multiple over time to:
- retrieve most updated data from the FDIC API
- integrate new NCUA data from custom query data files

## FDIC Data
Data is retrieved from the FDIC API every time the script is run. The pipeline dynamically queries the API for records that have a more recent update date, `DATEUPDT`, than the last FDIC data update in the database. Below is an example UYRL that will download relevant data from `2024-01-04` to `2024-01-13`. Reference `src/get_fdic_data.py`.
    > Example [download](https://banks.data.fdic.gov/api/institutions?filters=DATEUPDT%3A%5B%222024-01-04%22%20TO%20%222024-01-13%22%5D&fields=ASSET%2CCERT%2CCHARTER%2CCITY%2CDATEUPDT%2CDEP%2CREPDTE%2CRISDATE%2CRUNDATE%2CSTALP%2CUNINUM%2CWEBADDR%2CNAME&sort_by=DATEUPDT&sort_order=ASC&limit=50&offset=0&format=csv&download=true&filename=data_file)

API queries are written dynamically with the look up table in `data/Data_Banks/institutions_definitions.xlsx`

## NCUA Data
Quarterly data can be downloaded on the National Credit Union Administration website [here](https://ncua.gov/analysis/credit-union-corporate-call-report-data/quarterly-data)

### Automating Data Downloads
The zip files are hosted on the website and can be downloaded via accessing the URLs. The URLS have have the folloiwng consistent format since 2015: 
- https://ncua.gov/files/publications/analysis/call-report-data-2023-03.zip
 
Here is an example HTML element scraped from the NCUA website. Further automation might check all <td> elements for the <href> to prograatically download the call report. Please refer to `src/scrape_ncua_data.py` for a proof of concept on scraping the `.zip` files from the website. This solution uses the custom query to: (1) prioritize development and (2) have a more readily understandable data model

```HTML
<td><div class="lr-label">March</div><a href="/files/publications/analysis/call-report-data-2023-03.zip" title="See first quarter 2023 data">Select</a></td>
 ```

### Custom Query Download
This _current pipeline_ integration uses exports from the NCUA's custom query, using the steps shown in the images below. This helps minimize unnecessary data ingestion and simplify the data model. 

Custom Query [here](https://webapps2.ncua.gov/CustomQuery/CUSelect.aspx)

**Step 1: Filter for all Credit Unions**
![Step 1](https://raw.githubusercontent.com/jaimiles23/FDIC_NCUA_DataPipeline/main/lib/README%20Images/NCUA_CustomQuery_Step1.png)

**Step 2: Select only needed info**
![Step 2](https://raw.githubusercontent.com/jaimiles23/FDIC_NCUA_DataPipeline/main/lib/README%20Images/NCUA_CustomQuery_Step2.png)

Then, drop the downloaded file into the directory: `data/Data_NCUA/data_to_process/`. After the pipeline ingests the data, it will move the file to `data/Data_NCUA/processed/`


# Architectural Design

## Tech Stack
This data pipeline uses python and sqlite. 
- **Python** versatility proves invaluable for the data pipeline and allows for functionalities including: (1) connecting to an API, (2) webscraping HTML code, (3) sending commands to a SQL database, and (4) implementing an LLM interface. 
- **SQLite**: SQLlite is the most used database in the world. It provides a single file on desk, with zero latency. This provides portability and low latency for rapid development. Additionally, there are fewer services to setup/configure. There are a few drawbacks, including needing to explore better accessibility for the database in the future and fewer features, e.g., stored procedures and SQL agents. This means that the python script needs to facilitate running some SQL transformations. Further reasons to use SQLite are listed [here](https://www.sqlite.org/whentouse.html). Note that SQLite can handle up to 100k concurrent users, has low computing, is stored on the disk, and ultimatley no cost when run on a local machine.
- **LangChain**: [LangChain](https://www.langchain.com/) is used to instantiate an LLM with which users can query the database with natural language. LangChain is developed by OpenAI and the current leading LLM developer. Additionally, there are packages readily available in python


## Data Pipeline
This solution uses an ELT (Extract, Load, Transform) data pipeline. Generally, the pipeline:
1. Extracts publicly available data from regulator's websites.
2. Loads the data into a database
3. Transforms the data into normalized, appended tables.


### Data Lineage
The diagram provides a conceptual organization of the data flow and data lineage.
![Data Lineage](https://raw.githubusercontent.com/jaimiles23/FDIC_NCUA_DataPipeline/main/lib/Data%20Goverance/DataLineage.drawio.png)


### Data Model
Below is the data model for the transformed data from the data pipeline. Tables in the database are prefixed with "dw" to represent data warehouse. In a different database system, these tables might be stored in a different schema or an entirely different database.

![Data Model](https://raw.githubusercontent.com/jaimiles23/FDIC_NCUA_DataPipeline/main/lib/Data%20Goverance/DataModel.drawio.png)


### Data Governance
Note that all data presented here is publicly available and contains no PII. The LLM selected, `chat-gpt-3.5`, is only granted access to the finalized tables in our database. Thus, the data pipeline can be adjusted to ingest other data without making it accessible and potentially exposed via the LLM. This is specified by the `include_tables` keyword below.
```python
db = SQLDatabase.from_uri(
    f"sqlite+pysqlite:///{c.DB_NAME}",
    include_tables = [ 
        c.DB_DW_TBL_PROFILES,
        c.DB_DW_TBL_MONEY
    ]
)
```

# TODOs:
Below are a list of TODO items to explore/unpack further:
- **Dynamic Directories**: Currently, directories are hard coded in the constants module. This should be dynamic for a parent machine.




