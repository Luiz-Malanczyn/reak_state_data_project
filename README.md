# Real Estate Data Project

A data pipeline project that scrapes real estate listings from OLX, processes the data, and loads it into Google BigQuery.

## Project Structure

```
├── config/
│   └── config.yaml         # Configuration settings
├── connection/
│   └── gcp_connection.py   # Google Cloud Platform connection
├── pipeline/
│   ├── extract/           # Data extraction modules
│   ├── transform/         # Data transformation modules
│   ├── load/             # Data loading modules
│   └── flow.py           # Prefect pipeline flow
├── util/
│   └── logger.py         # Logging configuration
└── secret/               # Credentials (not tracked in git)
```

## Prerequisites

- Python 3.12+
- Poetry for dependency management
- Google Cloud Platform account with BigQuery access
- Playwright for web scraping

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd real_state_data_project
```

2. Install dependencies with Poetry:
```bash
poetry install
```

3. Install Playwright browsers:
```bash
poetry run playwright install chromium
```

4. Set up GCP credentials:
- Place your `gcp_credentials.json` in the `secret/` directory
- Update configuration in `config/config.yaml`

## Usage

Run the pipeline:
```bash
poetry run python main.py
```

## Docker

Build the container:
```bash
docker build -t real-estate-pipeline .
```

Run the container:
```bash
docker run real-estate-pipeline
```

## Tech Stack

- **Web Scraping**: Playwright
- **Data Processing**: Pandas
- **Pipeline Orchestration**: Prefect
- **Data Warehouse**: Google BigQuery
- **Logging**: Loguru