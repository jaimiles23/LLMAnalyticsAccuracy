
/**********
Get all new data
**********/

WITH existing_cus AS (
    SELECT cu_number FROM dw_financial_institution_profiles 
    WHERE [type] = 'Credit Union'
)

, new_cu_data AS (
SELECT
    'Credit Union' AS [type], 
    ('c_' || p.cu_number) AS [inst_id],
    p.CUName as [institution_name],
    p.cu_number AS [charter_number],
    p.URL AS [web_domain],
    p.City AS [city],
    p.State AS [state],
    p.date_updated AS [date_updated],
    RANK() OVER (
        PARTITION BY [cu_number]
        ORDER BY p.[date_updated] DESC
    ) AS row_num
FROM load_ncua_profiles AS p
WHERE 1=1
    AND p.cu_number NOT IN (SELECT * FROM existing_cus)
)

-- SELECT * FROM new_cu_data;


/**********
Insert New Data
**********/
INSERT INTO dw_financial_institution_profiles (
    [inst_id],
    [charter_number],
    [type],
    [institution_name],
    [web_domain],
    [city],
    [state],
    [last_update]
)
SELECT 
    [inst_id],
    [charter_number],
    [type], 
    [institution_name],
    [web_domain], 
    [city], 
    [state], 
    [date_updated]
FROM new_cu_data
WHERE row_num = 1
