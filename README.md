# sus-lakehouse

## What is this?
It is a Data Engineering project, aiming into getting data from SUS (Unique Healthcare System), more specific about Hospitalizations. Process and store this data in a Datawarehouse and get some insights with a dashboard.
## Data source
Data Source: SIH/SUS

The SIH/SUS (Sistema de Informações Hospitalares do Sistema Único de Saúde) is Brazil's National Hospital Information System. It serves as a centralized database capturing all hospitalizations managed under the Unified Health System (SUS).

    Governance: Managed by the Ministry of Health's Secretariat of Specialized Health Care.

    Core Entities & Attributes:

        Patient Data: Demographics and anonymized identifiers.

        Clinical Data: Diagnoses (ICD codes) and medical procedures performed.

        Financial Data: Payout values, billing information, and hospital reimbursements.

    Project Utility: Essential for tracking hospital metrics, generating public health statistics, and driving analytical research.
**Table used:** RD (Reduzida) — contains one row per hospitalization
**Access:** Publicly available via FTP at `ftp.datasus.gov.br` 
under `dissemin/publicos/SIHSUS/200801_/Dados/`
## Architecture
## Setup
### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — for dependency management
- A GCP account with billing enabled

### GCP Setup
1. Create a GCP project at [console.cloud.google.com](https://console.cloud.google.com)
2. Enable the following APIs:
   - Cloud Storage API
   - BigQuery API
3. Create a service account with the following roles:
   - Storage Object Admin
   - BigQuery Admin
4. Download the JSON key file and store it somewhere safe outside the project folder (e.g. `~/.gcp/sus-lakehouse-sa.json`)
5. Create a GCS bucket in your desired region
6. Create a BigQuery dataset named `sih_raw` in the same region
### Local Setup
```bash
git clone https://github.com/your-username/sus-lakehouse
cd sus-lakehouse
uv sync
cp .env.example .env
# Fill in the values in .env
```
## How to run

```bash
make download   # download SIH/RD files from DATASUS FTP
make upload     # upload parquet files to GCS
make bq-create  # create BigQuery external table
make run        # start the Streamlit dashboard
```
## Technical notes
### Data source known issues
At first I tried getting the data directly by a python library available called "pysus", but I faced a lot of issues when trying to get specific data for SIH. A lot of avilable files retrieved by using the "sih" function, were data related to SP(Serviços Profissionais), instead of RD (Reduzida). Because of that I decided using ftp directly and using pysus to convert the .dbc files into parquet.
### Architecture Decisions
I decided by using external tables in BigQuery instead of the native BigQuery tables, due storing the data in the GCS is cheaper and enough for this project scope. Letting the processing in to BigQuery where it is necessary.
I'm also currently using DuckDB for the dashboard queries instead of BigQuery, because Streamlit's @st.cache_data decorator caches the BigQuery result in memory, so DuckDB queries run locally without additional cloud costs. In future phases, when dbt mart tables are ready, queries will be pushed down to BigQuery directly.
### Known limitations
- Currently just taking data from SP state and 2024
- There are hardcoded values in early git commits (GCP identifiers)
- GOOGLE_APPLICATION_CREDENTIALS must be a full absolute path