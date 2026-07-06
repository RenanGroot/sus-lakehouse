SELECT state, year, COUNT(*) as n
FROM {{ ref('stg_state_population') }}
GROUP BY state, year
HAVING COUNT(*) > 1