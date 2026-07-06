WITH int_internacoes AS (
    SELECT * FROM {{ref('int_internacoes')}}
)

SELECT state, admission_year, population,
        COUNT(*) as total_hospitalizations,
        (COUNT(*) / population)* 100000 AS hospitalizations_per_100k 
        FROM int_internacoes 
        GROUP BY state, admission_year, population