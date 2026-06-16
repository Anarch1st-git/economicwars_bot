import os
from dotenv import load_dotenv

load_dotenv()

PROVIDER_TOKEN = os.getenv("PROVIDER_TOKEN", "")
TEST_PROVIDER_TOKEN = os.getenv("TEST_PROVIDER_TOKEN", "")
CURRENCY = os.getenv("PAYMENT_CURRENCY", "RUB")
