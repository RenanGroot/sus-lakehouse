WITH int_internacoes as(
    SELECT * FROM {{ref('int_internacoes')}}
)
SELECT diag_princ, state, admission_year, description, ROUND(AVG(morte) * 100, 2) as avg_morte, COUNT(*) as count_cases
        FROM int_internacoes 
        GROUP BY admission_year, state, diag_princ, description
        ORDER BY avg_morte DESC 