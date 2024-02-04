

/**********
Insert New Bank Profiles
**********/

WITH existing_banks AS (
    SELECT charter_number FROM dw_financial_institution_profiles 
    WHERE [type] = 'Bank'
)


, new_bank_data AS (
SELECT
    'Bank' AS [type], 
    ('b_' || b.UNINUM) AS [inst_id],
    b.NAME as [institution_name],
    b.UNINUM AS [charter_number],
    b.WEBADDR AS [web_domain],
    b.CITY AS [city],
    b.STALP AS [state],
    b.DATEUPDT AS [date_updated],
    RANK() OVER (
        PARTITION BY b.[UNINUM]
        ORDER BY b.[DATEUPDT] DESC
    ) AS row_num
FROM load_fdic_institutions AS b
WHERE 1=1
    AND b.UNINUM NOT IN (SELECT * FROM existing_banks)
)

-- SELECT * FROM new_bank_data;


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
FROM new_bank_data
WHERE row_num = 1
