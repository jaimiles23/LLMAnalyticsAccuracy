

/**********
Get Data for Existing Banks
**********/
WITH
last_bank_update AS (
    SELECT COALESCE( MAX([last_update]), '0') AS last_update
    FROM dw_financial_institution_profiles WHERE [type] = 'Bank'
)

, existing_banks AS (
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
Update Bank Data
**********/
UPDATE dw_financial_institution_profiles
SET 
    web_domain = new.web_domain, 
    city = new.city, 
    state = new.state,
    last_update = new.date_updated
FROM 
    (SELECT * FROM new_bank_data) AS new
WHERE 1=1
    AND new.[inst_id] = dw_financial_institution_profiles.[inst_id]
    AND new.row_num = 1
