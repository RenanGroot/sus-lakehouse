WITH stg_sih_rd AS (
    SELECT * FROM {{ ref('stg_sih_rd') }}
),
cid10_chapters AS(
    SELECT * FROM {{ref('cid10_chapters')}}
),
pop AS(
    SELECT * FROM {{ref('stg_state_population')}}
),
ipca as (
    SELECT * FROM {{ref('stg_ipca_monthly')}}
),

latest_ipca_index as(
    SELECT ipca_index as value FROM {{ref('stg_ipca_monthly')}}
    QUALIFY ROW_NUMBER() OVER (ORDER BY year DESC, month DESC) = 1
),
latest_population AS (
    SELECT state, population
    FROM {{ref('stg_state_population')}}
    QUALIFY ROW_NUMBER() OVER (PARTITION BY state ORDER BY year DESC) = 1
)

SELECT 
    s.year as partition_year,
    s.admission_year,
    s.admission_month,
    s.state,
    s.diag_princ, 
    s.dias_perm, 
    s.val_tot * (
        (SELECT value FROM latest_ipca_index) / COALESCE(ipca.ipca_index, (SELECT value FROM latest_ipca_index))
        ) as val_tot_corrected, 
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
    c.description,
    COALESCE(pop.population, lp.population) as population

FROM stg_sih_rd as s
LEFT JOIN cid10_chapters as c ON SUBSTR(diag_princ, 1, 3) BETWEEN c.range_start AND c.range_end
LEFT JOIN pop ON s.state = pop.state AND s.admission_year = pop.year
LEFT JOIN latest_population lp ON s.state = lp.state
LEFT JOIN ipca ON s.admission_month = ipca.month AND s.admission_year = ipca.year