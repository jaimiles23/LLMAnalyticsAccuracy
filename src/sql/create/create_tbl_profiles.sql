
CREATE TABLE IF NOT EXISTS dw_financial_institution_profiles (
    [inst_id] NVARCHAR NOT NULL,
    [charter_number] INTEGER NOT NULL,
    [type] NVARCHAR,
    [institution_name] NVARCHAR, 
    [web_domain] NVARCHAR, 
    [city] NVARCHAR, 
    [state] NVARCHAR,
    [last_update] TEXT,

    CONSTRAINT [pk_charter_num] PRIMARY KEY ([inst_id])
);
