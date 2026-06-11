WITH int_internacoes as(
    SELECT * FROM {{ref('int_internacoes')}}
)
SELECT diag_princ, description, AVG(dias_perm) as avg_days
        FROM int_internacoes 
        GROUP BY diag_princ, description
        ORDER BY avg_days DESC 