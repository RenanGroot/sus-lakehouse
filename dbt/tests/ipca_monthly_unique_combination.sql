SELECT month, year, COUNT(*) as n
FROM {{ ref('stg_ipca_monthly') }}
GROUP BY month, year
HAVING COUNT(*) > 1