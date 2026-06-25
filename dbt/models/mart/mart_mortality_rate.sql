WITH int_internacoes as(
    SELECT * FROM {{ref('int_internacoes')}}
)
SELECT diag_princ, description, ROUND(AVG(morte) * 100, 2) as avg_morte, COUNT(*) as count_cases
        FROM int_internacoes 
        GROUP BY year, state, diag_princ, description
        ORDER BY avg_morte DESC 