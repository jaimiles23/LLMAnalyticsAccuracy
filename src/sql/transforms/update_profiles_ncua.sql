

/**********
Get Data for Existing Credit Unions
**********/
WITH
last_cu_update AS (
    SELECT COALESCE( MAX([last_update]), '0') AS last_update
    FROM dw_financial_institution_profiles WHERE [type] = 'Credit Union'
)

, existing_cus AS (
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
    AND p.date_updated > (SELECT MAX(last_update) FROM last_cu_update)
    AND p.cu_number IN (SELECT * FROM existing_cus)
)

-- SELECT * FROM new_cu_data;


/**********
Update Credit Union Data
**********/
UPDATE dw_financial_institution_profiles
SET 
    web_domain = new.web_domain, 
    city = new.city, 
    state = new.state,
    last_update = new.date_updated
FROM 
    (SELECT * FROM new_cu_data) AS new
WHERE 1=1
    AND new.[inst_id] = dw_financial_institution_profiles.[inst_id]
    AND new.row_num = 1


