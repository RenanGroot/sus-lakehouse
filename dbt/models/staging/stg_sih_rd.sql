WITH stg_sih_rd as (
    SELECT * FROM {{source('sih_raw', 'internacoes')}}
)

SELECT 
    year,
    state,
    DIAG_PRINC as diag_princ, 
    CAST(DIAS_PERM as INT64) as dias_perm, 
    CAST(VAL_TOT AS FLOAT64) AS val_tot, 
    CAST(MORTE AS INT64) AS morte,
    CAST(IDADE AS INT64) AS idade,
    SEXO as sexo,
    MUNIC_RES as munic_res
FROM stg_sih_rd