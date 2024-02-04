
CREATE TABLE IF NOT EXISTS dw_financial_institution_money (
    [row_id] INTEGER PRIMARY KEY AUTOINCREMENT, 
    [inst_id] TEXT,
    [total_assets] INTEGER,
    [total_deposits] INTEGER, 
    [last_update] TEXT,
    [year] INTEGER, 
    [quarter] INTEGER,

    FOREIGN KEY ([inst_id]) REFERENCES [dw_financial_institution_profiles] ([inst_id])
);

