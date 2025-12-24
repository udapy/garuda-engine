# main.py
import asyncio
import sys
from loguru import logger
from network import NetworkManager
from parsers import parse_nse_json, scan_pdf_content
from config import NSE_API_ANNOUNCEMENTS, POLL_INTERVAL

# Install uvloop policy for speed
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    logger.info("🚀 High-Speed Event Loop: ENABLED (uvloop)")
except ImportError:
    logger.warning("⚠️ High-Speed Event Loop: DISABLED (standard asyncio)")

# --- PERSISTENCE SETUP ---
import csv
import os
from datetime import datetime

# Ensure logs dir exists
os.makedirs("logs", exist_ok=True)
logger.add("logs/garuda_{time:YYYY-MM-DD}.log", rotation="500 MB", retention="10 days", level="INFO")

# Init Signal File
SIGNAL_FILE = "signals.csv"
if not os.path.exists(SIGNAL_FILE):
    with open(SIGNAL_FILE, "w") as f:
        f.write("timestamp,symbol,signal,reason,details\n")

def save_signal(symbol, signal, reason, details):
    """Persists trade signal to CSV for execution engine."""
    with open(SIGNAL_FILE, "a") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), symbol, signal, reason, details])

seen_announcements = set()

async def process_announcement(nm, item, engine=None):
    """
    Decides if an announcement is trade-worthy.
    """
    # Create a unique ID to avoid duplicates
    uid = f"{item.get('symbol')}-{item.get('desc')}"
    if uid in seen_announcements:
        return
    
    seen_announcements.add(uid)
    
    symbol = item.get('symbol')
    desc = item.get('desc', '').lower()
    attachment = item.get('attchment') # NSE typo in API key is real: 'attchment'

    logger.info(f"New: {symbol} | {desc[:50]}...")

    # 1. Quick Text Filter (Zero Latency)
    # If the description itself contains "Bonus", we don't need the PDF.
    if "bonus" in desc or "dividend" in desc:
        logger.success(f"🔥 HIGH SIGNAL: {symbol} - {desc}")
        save_signal(symbol, "BUY", "L1_TEXT_MATCH", desc)
        if engine:
            engine.place_order(symbol, "BUY")
        return

    # 2. Deep Dive (Low Latency)
    # If ambiguous, download the PDF (only if attachment exists)
    if attachment:
        pdf_url = attachment if "http" in attachment else f"https://www.nseindia.com{attachment}"
        pdf_data = await nm.fetch(pdf_url)
        
        if pdf_data:
            sentiment = scan_pdf_content(pdf_data)
            if sentiment == 1:
                logger.success(f"🚀 PDF CONFIRMED BUY: {symbol}")
                save_signal(symbol, "BUY", "L2_PDF_SENTIMENT", "Positive Keywords Found")
                if engine:
                    engine.place_order(symbol, "BUY")
            elif sentiment == -1:
                logger.warning(f"🔻 PDF CONFIRMED SELL: {symbol}")
                save_signal(symbol, "SELL", "L2_PDF_SENTIMENT", "Negative Keywords Found")
                if engine:
                    engine.place_order(symbol, "SELL")

async def main():
    # --- BROKER SELECTION ---
    print("\n🦅 ANTIGRAVITY ENGINE SETUP")
    print("Select Execution Broker:")
    print("[1] Zerodha (Kite)")
    print("[2] Interactive Brokers (IBKR)")
    print("[3] Paper Trading (Log Only)")
    
    choice = input("Enter Choice (1/2/3): ").strip()
    
    engine = None
    from execution import ZerodhaEngine, IBKREngine
    
    if choice == "1":
        engine = ZerodhaEngine()
    elif choice == "2":
        engine = IBKREngine()
    else:
        logger.info("Running in PAPER TRADING mode.")

    if engine:
        await engine.initialize()

    logger.info("Starting High-Frequency News Engine...")
    nm = NetworkManager()
    await nm.initialize()

    try:
        while True:
            # Fetch generic announcements
            raw_data = await nm.fetch(NSE_API_ANNOUNCEMENTS)
            
            if raw_data:
                items = parse_nse_json(raw_data)
                # Process latest 5 items concurrently
                tasks = [process_announcement(nm, item, engine) for item in items[:5]]
                await asyncio.gather(*tasks)
            
            await asyncio.sleep(POLL_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("Stopping...")
        if engine and hasattr(engine, 'ib') and engine.ib:
            engine.ib.disconnect()
    finally:
        await nm.close()

if __name__ == "__main__":
    asyncio.run(main())
