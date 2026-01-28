"""Service to fetch and store 10-K reports in RAG when user enters ticker"""

from typing import Dict, Optional
import logging
from app.services.sec_edgar_service import SECEdgarService
from app.services.document_processor import DocumentProcessor, ProcessedDocument, DocumentType, DocumentChunk
from app.core.database import get_db

logger = logging.getLogger(__name__)

class TickerToRAGService:
    def __init__(self):
        self.sec_service = SECEdgarService()
        self.doc_processor = DocumentProcessor()
    
    async def process_ticker_for_rag(self, ticker: str) -> Dict[str, str]:
        """Fetch 10-K for ticker and store in RAG"""
        try:
            # 1. Fetch 10-K data
            filing_data = await self.sec_service.parse_10k_filing(ticker)
            if not filing_data:
                return {"status": "error", "message": f"No 10-K found for {ticker}"}
            
            # 2. Convert to ProcessedDocument
            doc = self._create_processed_document(ticker, filing_data)
            
            # 3. Store in RAG
            await self.doc_processor._store_document_in_chromadb(doc)
            
            return {
                "status": "success", 
                "message": f"10-K for {ticker} stored in RAG",
                "filing_date": filing_data.get("filing_date"),
                "chunks_stored": len(doc.chunks)
            }
            
        except Exception as e:
            logger.error(f"Error processing {ticker} for RAG: {e}")
            return {"status": "error", "message": str(e)}
    
    def _create_processed_document(self, ticker: str, filing_data: Dict) -> ProcessedDocument:
        """Convert 10-K data to ProcessedDocument format"""
        chunks = []
        
        # Create chunks for each section
        sections = {
            "business_overview": filing_data.get("business_overview", ""),
            "risk_factors": filing_data.get("risk_factors", ""),
            "financial_highlights": filing_data.get("financial_highlights", ""),
            "management_discussion": filing_data.get("management_discussion", "")
        }
        
        for section_name, content in sections.items():
            if content:
                chunk = DocumentChunk(
                    id=f"{ticker}_{filing_data['accession_number']}_{section_name}",
                    content=content,
                    metadata={
                        "ticker": ticker,
                        "section": section_name,
                        "filing_date": filing_data["filing_date"],
                        "accession_number": filing_data["accession_number"],
                        "document_type": "10-K"
                    }
                )
                chunks.append(chunk)
        
        return ProcessedDocument(
            document_id=f"{ticker}_{filing_data['accession_number']}",
            document_type=DocumentType.SEC_10K,
            ticker=ticker,
            chunks=chunks,
            metadata={
                "ticker": ticker,
                "filing_date": filing_data["filing_date"],
                "accession_number": filing_data["accession_number"]
            }
        )
