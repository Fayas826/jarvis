import os
import logging
from typing import Dict, Any, List

try:
    import PyPDF2
except ImportError:
    logging.warning("PyPDF2 not found. Please install via: python -m pip install PyPDF2")
    PyPDF2 = None

class LegalParsingAgent:
    """
    JARVIS Specialized Swarm Member: The Attorney.
    Reads massive PDF contracts, extracts raw text, and highlights
    legal liabilities, clauses, and required signatures using NLP.
    """
    
    def __init__(self):
        if not PyPDF2:
            logging.error("[Legal Agent] PyPDF2 library missing. PDF parsing is disabled.")
            
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Reads a .pdf file and extracts all text."""
        if not os.path.exists(file_path):
            logging.error(f"[Legal Agent] File not found: {file_path}")
            return ""
            
        text = ""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                total_pages = len(reader.pages)
                logging.info(f"[Legal Agent] Analyzing {total_pages}-page contract: {file_path}")
                
                for page_num in range(total_pages):
                    page = reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                        
            logging.info(f"[Legal Agent] Successfully extracted {len(text)} characters of legal text.")
            return text
        except Exception as e:
            logging.error(f"[Legal Agent] Failed to parse PDF: {e}")
            return ""

    def analyze_contract_liabilities(self, file_path: str) -> Dict[str, Any]:
        """
        Extracts text from a contract and simulates feeding it to an LLM 
        to find specific legal liabilities.
        """
        raw_text = self._extract_text_from_pdf(file_path)
        
        if not raw_text:
            return {"status": "failed", "message": "Could not extract text from document."}
            
        logging.info("[Legal Agent] Feeding contract to NLP engine for liability extraction...")
        
        # In a real swarm, this text is passed to the NLPAgent (e.g. Llama-3 or GPT-4)
        # We simulate the NLP response here for the architecture.
        
        mock_nlp_response = {
            "status": "success",
            "document_type": "Terms of Service / End User License Agreement",
            "critical_liabilities_found": [
                "Clause 4.2: User waives the right to a jury trial and agrees to binding arbitration.",
                "Clause 7.1: Company reserves the right to terminate the account without prior notice.",
                "Clause 9.4: User grants irrevocable license to all uploaded intellectual property."
            ],
            "risk_score": "HIGH",
            "recommendation": "Do not sign without renegotiating Clause 9.4 regarding IP rights."
        }
        
        logging.warning(f"⚖️ [Legal Agent] Contract Audit Complete. Risk Level: {mock_nlp_response['risk_score']}")
        return mock_nlp_response
