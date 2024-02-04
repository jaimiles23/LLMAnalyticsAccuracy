-- How many banks and credit unions are active by asset tier (e.g. total assets between $500M and $1B)

/**********
Active by assets
**********/
-- Limitations: this data pipeline does NOT check if banks/credit unions are active or not

WITH most_recent_money AS (
    SELECT inst_id, total_assets, 
    RANK() OVER (
        PARTITION BY inst_id
        ORDER BY last_update DESC 
    ) AS row_num
    FROM dw_financial_institution_money
)

SELECT 
p.type, COUNT(*) 
FROM most_recent_money AS m
INNER JOIN dw_financial_institution_profiles AS p
    ON p.inst_id = m.inst_id
WHERE row_num = 1
GROUP BY p.type

