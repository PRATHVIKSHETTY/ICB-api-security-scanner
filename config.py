import os

class Config:

    DEBUG = True
    REQUEST_TIMEOUT = 5
    REPORT_PATH = "reports/report.json"

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")