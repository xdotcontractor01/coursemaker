"""
PDF Citation Utility
Verifies quotes exist in PDF and returns page numbers and context.
Supports keyword search for spec references (e.g., "subsection 102.04").
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    from pdfminer.high_level import extract_text
    from pdfminer.layout import LAParams
    PDFMINER_AVAILABLE = True
except ImportError:
    PDFMINER_AVAILABLE = False


@dataclass
class CitationResult:
    """Result of a citation verification"""
    found: bool
    page_number: Optional[int] = None
    page_numbers: List[int] = None  # Multiple matches
    context: Optional[str] = None
    match_text: Optional[str] = None
    confidence: float = 0.0  # 0.0 to 1.0


class PDFCitationVerifier:
    """Verifies citations against PDF content"""
    
    # Common spec reference patterns
    SPEC_PATTERNS = [
        r'subsection\s*(\d+\.?\d*)',
        r'section\s*(\d+\.?\d*)',
        r'spec(?:ification)?\s*(\d+\.?\d*)',
        r'item\s*(\d+)',
        r'article\s*(\d+)',
    ]
    
    def __init__(self, pdf_path: Path):
        self.pdf_path = Path(pdf_path)
        self._text_cache: Dict[int, str] = {}  # page -> text
        self._full_text: Optional[str] = None
    
    def verify_quote(self, quote: str, fuzzy_match: bool = True) -> CitationResult:
        """Verify that a quote exists in the PDF"""
        if not self.pdf_path.exists():
            return CitationResult(found=False, context="PDF file not found")
        
        # Load PDF text if not cached
        self._load_pdf_text()
        
        if not self._full_text:
            return CitationResult(found=False, context="Could not extract PDF text")
        
        # Normalize quote for matching
        normalized_quote = self._normalize_text(quote)
        
        # Try exact match first
        result = self._find_exact_match(normalized_quote)
        if result.found:
            return result
        
        # Try fuzzy match if exact fails
        if fuzzy_match:
            result = self._find_fuzzy_match(normalized_quote)
        
        return result
    
    def search_spec_reference(self, spec_ref: str) -> CitationResult:
        """Search for a specification reference (e.g., "subsection 102.04")"""
        if not self.pdf_path.exists():
            return CitationResult(found=False, context="PDF file not found")
        
        self._load_pdf_text()
        
        if not self._full_text:
            return CitationResult(found=False, context="Could not extract PDF text")
        
        # Extract the number from the reference
        for pattern in self.SPEC_PATTERNS:
            match = re.search(pattern, spec_ref, re.IGNORECASE)
            if match:
                spec_num = match.group(1)
                break
        else:
            spec_num = spec_ref
        
        # Search for the spec reference in PDF
        search_patterns = [
            rf'subsection\s*{re.escape(spec_num)}',
            rf'section\s*{re.escape(spec_num)}',
            rf'{re.escape(spec_num)}',
        ]
        
        for pattern in search_patterns:
            for page_num, page_text in self._text_cache.items():
                normalized = self._normalize_text(page_text)
                if re.search(pattern, normalized, re.IGNORECASE):
                    # Find context
                    match = re.search(rf'.{{0,100}}{pattern}.{{0,100}}', normalized, re.IGNORECASE)
                    context = match.group(0) if match else None
                    
                    return CitationResult(
                        found=True,
                        page_number=page_num,
                        context=context,
                        match_text=spec_num,
                        confidence=0.9
                    )
        
        return CitationResult(found=False, context=f"Spec reference '{spec_ref}' not found in PDF")
    
    def get_page_text(self, page_number: int) -> Optional[str]:
        """Get text from a specific page"""
        self._load_pdf_text()
        return self._text_cache.get(page_number)
    
    def search_keyword(self, keyword: str) -> List[CitationResult]:
        """Search for all occurrences of a keyword"""
        if not self.pdf_path.exists():
            return []
        
        self._load_pdf_text()
        
        results = []
        normalized_keyword = self._normalize_text(keyword)
        
        for page_num, page_text in self._text_cache.items():
            normalized_page = self._normalize_text(page_text)
            
            # Find all matches
            for match in re.finditer(re.escape(normalized_keyword), normalized_page, re.IGNORECASE):
                # Get context
                start = max(0, match.start() - 50)
                end = min(len(normalized_page), match.end() + 50)
                context = normalized_page[start:end]
                
                results.append(CitationResult(
                    found=True,
                    page_number=page_num,
                    context=f"...{context}...",
                    match_text=match.group(0),
                    confidence=1.0
                ))
        
        return results
    
    def _load_pdf_text(self):
        """Load PDF text into cache"""
        if self._full_text is not None:
            return
        
        if PYMUPDF_AVAILABLE:
            self._load_with_pymupdf()
        elif PDFMINER_AVAILABLE:
            self._load_with_pdfminer()
        else:
            # No PDF library available
            self._full_text = ""
            print("Warning: No PDF library available (install pymupdf or pdfminer.six)")
    
    def _load_with_pymupdf(self):
        """Load PDF using PyMuPDF"""
        try:
            doc = fitz.open(str(self.pdf_path))
            full_text_parts = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                self._text_cache[page_num + 1] = text  # 1-indexed pages
                full_text_parts.append(text)
            
            self._full_text = "\n".join(full_text_parts)
            doc.close()
        except Exception as e:
            print(f"Error loading PDF with PyMuPDF: {e}")
            self._full_text = ""
    
    def _load_with_pdfminer(self):
        """Load PDF using pdfminer"""
        try:
            text = extract_text(str(self.pdf_path), laparams=LAParams())
            self._full_text = text
            # pdfminer doesn't give per-page access easily, store all in page 1
            self._text_cache[1] = text
        except Exception as e:
            print(f"Error loading PDF with pdfminer: {e}")
            self._full_text = ""
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for matching"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove common OCR artifacts
        text = text.replace('\n', ' ').replace('\r', ' ')
        return text.strip().lower()
    
    def _find_exact_match(self, normalized_quote: str) -> CitationResult:
        """Find exact match in PDF"""
        for page_num, page_text in self._text_cache.items():
            normalized_page = self._normalize_text(page_text)
            
            if normalized_quote in normalized_page:
                # Find context
                idx = normalized_page.find(normalized_quote)
                start = max(0, idx - 50)
                end = min(len(normalized_page), idx + len(normalized_quote) + 50)
                context = normalized_page[start:end]
                
                return CitationResult(
                    found=True,
                    page_number=page_num,
                    context=f"...{context}...",
                    match_text=normalized_quote,
                    confidence=1.0
                )
        
        return CitationResult(found=False)
    
    def _find_fuzzy_match(self, normalized_quote: str) -> CitationResult:
        """Find fuzzy match using key phrases"""
        # Extract key phrases (3+ word sequences)
        words = normalized_quote.split()
        
        if len(words) < 3:
            return CitationResult(found=False)
        
        # Try matching key phrases
        for i in range(len(words) - 2):
            phrase = ' '.join(words[i:i+3])
            
            for page_num, page_text in self._text_cache.items():
                normalized_page = self._normalize_text(page_text)
                
                if phrase in normalized_page:
                    # Find context
                    idx = normalized_page.find(phrase)
                    start = max(0, idx - 50)
                    end = min(len(normalized_page), idx + len(phrase) + 50)
                    context = normalized_page[start:end]
                    
                    return CitationResult(
                        found=True,
                        page_number=page_num,
                        context=f"...{context}...",
                        match_text=phrase,
                        confidence=0.7
                    )
        
        return CitationResult(found=False)


def verify_pdf_citation(pdf_path: Path, quote: str) -> CitationResult:
    """Convenience function to verify a citation"""
    verifier = PDFCitationVerifier(pdf_path)
    return verifier.verify_quote(quote)


def search_pdf_spec(pdf_path: Path, spec_ref: str) -> CitationResult:
    """Convenience function to search for a spec reference"""
    verifier = PDFCitationVerifier(pdf_path)
    return verifier.search_spec_reference(spec_ref)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python pdf_citations.py <pdf_path> <quote_or_spec>")
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1])
    search_text = sys.argv[2]
    
    verifier = PDFCitationVerifier(pdf_path)
    
    # Try spec reference first
    if re.match(r'.*\d+\.\d+.*', search_text):
        result = verifier.search_spec_reference(search_text)
    else:
        result = verifier.verify_quote(search_text)
    
    print(f"Found: {result.found}")
    if result.found:
        print(f"Page: {result.page_number}")
        print(f"Context: {result.context}")
        print(f"Confidence: {result.confidence}")


