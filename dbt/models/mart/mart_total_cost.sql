WITH int_internacoes as(
    SELECT * FROM {{ref('int_internacoes')}}
)
SELECT diag_princ, state, admission_year, description, SUM(val_tot_corrected) as sum_total_cost_corrected 
        FROM int_internacoes 
        GROUP BY admission_year, state, diag_princ, description
        ORDER BY sum_total_cost_corrected DESC 
