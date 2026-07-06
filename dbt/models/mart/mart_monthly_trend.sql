WITH int_internacoes AS (
    SELECT * FROM {{ref('int_internacoes')}}
)

SELECT admission_year, state, admission_month, population,
    COUNT(*) as total_hospitalizations,
    SUM(morte) as total_deaths,
    SUM(val_tot_corrected) as sum_total_cost_corrected
    FROM int_internacoes
    GROUP BY admission_year, state, admission_month, population