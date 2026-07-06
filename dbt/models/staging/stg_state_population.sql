WITH stg_state_population AS (
    SELECT * FROM {{source('sih_raw', 'state_population')}}
)

SELECT
    year,
    state,
    population
FROM stg_state_population