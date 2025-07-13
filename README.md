# Kara Solutions ELT Project

This project provides an Extract, Load, and Transform (ELT) pipeline for scraping, storing, and analyzing data, with a focus on Telegram channels and PostgreSQL integration. It uses Docker for containerization and dbt for analytics engineering.

## Folder Structure

```
├── data/                # Raw and processed data storage
├── notebooks/           # Jupyter notebooks for exploration and analysis
├── scripts/             # Python scripts (e.g., scraper.py)
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Multi-container orchestration
├── .env                 # Environment variables (API keys, DB credentials)
└── README.md            # Project documentation
```

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Telegram API credentials (API_ID, API_HASH)
- Python 3.10+ (if running scripts outside Docker)

### Setup
1. Clone the repository and navigate to the project folder.
2. Create a `.env` file with your credentials (see example in repo).
3. Build and start the containers:
   ```sh
   docker-compose up --build
   ```

### Running the Scraper
- The main scraping script is at `scripts/scraper.py`.
- It logs to `logs/scraping.log` and saves data under `data/raw/`.
- To run the scraper inside the container:
  ```sh
  docker-compose exec app python scripts/scraper.py
  ```

### Database
- PostgreSQL runs in the `db` service.
- Connection details are set via `.env` and used by dbt and scripts.

### Analytics
- dbt project files should be placed in a subfolder (e.g., `ethio_medical_dbt/`).
- Use dbt commands inside the container for analytics workflows.

## Notes
- Update `requirements.txt` to add Python dependencies.
- Use the `notebooks/` folder for data exploration and prototyping.
- All logs are stored in the `logs/` directory (created automatically).

## License
MIT License
