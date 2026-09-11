FROM python:3.12-slim

WORKDIR /dbt

RUN pip install --no-cache-dir dbt-bigquery==1.9.0

COPY . .

COPY profiles.prod.yml /root/.dbt/profiles.yml

CMD ["sh", "-c", "dbt run --target prod && dbt test --target prod"]
