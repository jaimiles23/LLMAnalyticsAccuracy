
/**********
Insert New Bank Profiles
**********/

WITH
last_bank_update AS (
    SELECT COALESCE( MAX([last_update]), '0') AS last_update
    FROM dw_financial_institution_money WHERE substr(inst_id, 1, 1) = 'c'
)


, new_bank_money_data AS (
SELECT
    ('c_' || p.[cu_number]) AS [inst_id],
    p.[TotalAssets] AS [total_assets], 
    s.[A018] AS [total_deposits], 
    p.[date_updated] AS [last_update],
    substr(p.[date_updated], 1, 4) AS [year],
    CASE 
        WHEN CAST(substr(p.[date_updated], 6, 2) AS INTEGER) <= 3 THEN '3'
        WHEN CAST(substr(p.[date_updated], 6, 2) AS INTEGER) <= 6 THEN '4'
        WHEN CAST(substr(p.[date_updated], 6, 2) AS INTEGER) <= 9 THEN '1'
        WHEN CAST(substr(p.[date_updated], 6, 2) AS INTEGER) <= 12 THEN '2'
        ELSE 'Error'
    END AS [quarter]
FROM load_ncua_profiles AS p
LEFT JOIN load_ncua_shares AS s
    ON s.Charter = p.cu_number
    AND s.date_updated = p.date_updated
WHERE p.date_updated > (SELECT MAX(last_update) FROM last_bank_update)
)

-- SELECT * FROM new_bank_money_data;


/**********
Insert New Data
**********/
INSERT INTO dw_financial_institution_money (
    [inst_id],
    total_assets, 
    [total_deposits],
    [last_update]
)
SELECT 
    [inst_id],
    total_assets, 
    [total_deposits],
    [last_update]
FROM new_bank_money_data

