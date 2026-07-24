import os

from dotenv import load_dotenv

load_dotenv()

TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")

TWELVE_DATA_API_URL = "https://api.twelvedata.com"

GOLD_API_URL = "https://api.gold-api.com/price/XAU"

REQUEST_TIMEOUT = 10

OUNCE_TO_GRAM = 31.1035