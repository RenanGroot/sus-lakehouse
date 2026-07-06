WITH stg_ipca_monthly AS(
    SELECT * FROM {{source('sih_raw','ipca_monthly')}}
)
SELECT
    ipca_index,
    year,
    month
FROM stg_ipca_monthly