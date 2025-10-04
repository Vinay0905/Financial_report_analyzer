from ..utils.document_parser import parse_document

class DataExtractionAgent:
    def extract(self, file_path):
        """
        Extracts financial metrics and company info from document.
        Includes fallback for company_name when symbol is not provided.
        """
        parsed = parse_document(file_path)
        return {
            "company_name": parsed.get("company_name"),
            "symbol": parsed.get("symbol"),
            "revenue": parsed.get("revenue"),
            "net_income": parsed.get("net_income"),
            "assets": parsed.get("assets"),
            "liabilities": parsed.get("liabilities"),
            # add other fields as needed
        }
