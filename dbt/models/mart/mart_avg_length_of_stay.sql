WITH int_internacoes as(
    SELECT * FROM {{ref('int_internacoes')}}
)
SELECT diag_princ, state, admission_year, description, AVG(dias_perm) as avg_days, 
    COUNT(*) as count_cases,
    ANY_VALUE(chapter_description) AS chapter_description
        FROM int_internacoes 
        GROUP BY admission_year, state, diag_princ, description
        ORDER BY avg_days DESC 