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
## How to run
*Coming soon — Makefile with `make download`, `make run`*
## Technical notes
At first I tried getting the data directly by a python library available called "pysus", but I faced a lot of issues when trying to get specific data for SIH. A lot of avilable files retrieved by using the "sih" function, were data related to SP(Serviços Profissionais), instead of RD (Reduzida). Because of that I decided using ftp directly and using pysus to convert the .dbc files into parquet