-- Which banks and credit unions experienced >5% decline in deposits last quarter

WITH compare_money AS (
    SELECT inst_id, 
    total_assets, 
    LAG(total_assets, 1, 0) OVER (
        PARTITION BY inst_id
        ORDER BY last_update ASC 
    ) AS prev_assets, 
    RANK() OVER (
        PARTITION BY inst_id
        ORDER BY last_update ASC 
    ) AS row_num,
    year, quarter
    FROM dw_financial_institution_money
)

, percent_change AS (
    SELECT 
    inst_id, 
    ((prev_assets - total_assets) * 100 )/ prev_assets AS percent_asset_change, 
    year, quarter
    FROM compare_money
    WHERE 
        row_num > 1
)

SELECT 
p.institution_name, 
pc.percent_asset_change
FROM percent_change AS pc
INNER JOIN dw_financial_institution_profiles AS p
    ON p.inst_id = pc.inst_id

WHERE percent_asset_change < -5
;
