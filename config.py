# config.py
import re
import os

# --- ENDPOINTS ---
NSE_HOME = "https://www.nseindia.com"
NSE_API_ANNOUNCEMENTS = "https://www.nseindia.com/api/corporate-announcements?index=equities"
BSE_API = "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w?categ=Results"

# --- TRADING SETTINGS ---
POLL_INTERVAL = 0.5
KEYWORDS_POSITIVE = {
    "bonus issue", "dividend declared", "stock split", "merger",
    "order win", "patent granted", "acquisition"
}
KEYWORDS_NEGATIVE = {
    "fraud", "resignation", "default", "bankruptcy", "raid", "litigation"
}

# --- BROKER CREDENTIALS ---
# Set these in your shell execution environment:
# export ZERODHA_API_KEY="your_key"
# export ZERODHA_ACCESS_TOKEN="your_token"
# export IBKR_PORT="7497"

# Regex
REGEX_REVENUE = re.compile(r"(?:revenue|sales)\s*(?:up|growth)\s*(\d+(?:\.\d+)?)%", re.IGNORECASE)
REGEX_PROFIT = re.compile(r"(?:profit|pat)\s*(?:up|jump|grew)\s*(\d+(?:\.\d+)?)%", re.IGNORECASE)

# Headers
BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"macOS"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Upgrade-Insecure-Requests": "1"
}
