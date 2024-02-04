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