WITH int_internacoes as(
    SELECT * FROM {{ref('int_internacoes')}}
)
SELECT diag_princ, description, SUM(val_tot) as sum_totalval 
        FROM int_internacoes 
        GROUP BY diag_princ, description
        ORDER BY sum_totalval DESC 
