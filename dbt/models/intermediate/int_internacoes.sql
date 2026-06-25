WITH stg_sih_rd AS (
    SELECT * FROM {{ ref('stg_sih_rd') }}
),
cid10_chapters AS(
    SELECT * FROM {{ref('cid10_chapters')}}
)
SELECT 
    s.year,
    s.state,
    s.diag_princ, 
    s.dias_perm, 
    s.val_tot, 
    s.morte,
    s.idade,
    s.sexo,
    s.munic_res,
    ROUND(s.val_tot / NULLIF(s.dias_perm, 0),2)  as cost_per_day,
    CASE 
        WHEN s.dias_perm < 3 THEN "short"
        WHEN s.dias_perm BETWEEN 3 AND 10  THEN "medium"
        ELSE "long"
    END as length_category,
    c.description

FROM stg_sih_rd as s
LEFT JOIN cid10_chapters as c ON SUBSTR(diag_princ, 1, 3) BETWEEN c.range_start AND c.range_end