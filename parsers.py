# parsers.py
import fitz  # PyMuPDF
import orjson
import io
from loguru import logger
from config import KEYWORDS_POSITIVE, KEYWORDS_NEGATIVE

def parse_nse_json(raw_bytes):
    """Fast JSON parse using orjson."""
    try:
        data = orjson.loads(raw_bytes)
        # NSE structure usually: [ {desc: "...", attchment: "url"}, ... ]
        return data
    except Exception as e:
        logger.error(f"JSON Parse Error: {e}")
        try:
            logger.debug(f"Failed Data Snippet: {raw_bytes[:100]}")
        except:
            pass
        return []

def scan_pdf_content(pdf_bytes):
    """
    Downloads PDF in memory and scans first page only (Speed > Accuracy).
    Returns a sentiment score: 1 (Buy), -1 (Sell), 0 (Neutral).
    """
    try:
        # Open PDF from memory bytes
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # Only read the first page (that's where the headline is)
        if len(doc) < 1: return 0
        text = doc[0].get_text().lower()
        
        # Check Keywords
        if any(w in text for w in KEYWORDS_POSITIVE):
            return 1
        if any(w in text for w in KEYWORDS_NEGATIVE):
            return -1
            
        doc.close()
    except Exception as e:
        logger.error(f"PDF Parse Error: {e}")
    
    return 0
