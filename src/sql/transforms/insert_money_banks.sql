

/**********
Insert New Bank Profiles
**********/

WITH
last_bank_update AS (
    SELECT COALESCE( MAX([last_update]), '0') AS last_update
    FROM dw_financial_institution_money WHERE substr(inst_id, 1, 1) = 'b'
)
-- SELECT * FROM last_bank_update


, new_bank_money_data AS (
SELECT
    ('b_' || b.UNINUM) AS [inst_id],
    b.ASSET AS [total_assets], 
    b.DEP AS [total_deposits], 
    b.DATEUPDT AS [last_update],
    substr(b.DATEUPDT, 1, 4) AS [year],
    CASE 
        WHEN CAST(substr(b.DATEUPDT, 6, 2) AS INTEGER) <= 3 THEN '3'
        WHEN CAST(substr(b.DATEUPDT, 6, 2) AS INTEGER) <= 6 THEN '4'
        WHEN CAST(substr(b.DATEUPDT, 6, 2) AS INTEGER) <= 9 THEN '1'
        WHEN CAST(substr(b.DATEUPDT, 6, 2) AS INTEGER) <= 12 THEN '2'
        ELSE 'Error'
    END AS [quarter]
FROM load_fdic_institutions AS b
WHERE b.DATEUPDT > (SELECT MAX(last_update) FROM last_bank_update)
)

-- SELECT * FROM new_bank_money_data;


/**********
Insert New Data
**********/
INSERT INTO dw_financial_institution_money (
    [inst_id],
    total_assets, 
    [total_deposits],
    [last_update], 
    [year], 
    [quarter]
)
SELECT 
    [inst_id],
    total_assets, 
    [total_deposits],
    [last_update],
    [year], 
    [quarter]
FROM new_bank_money_data
