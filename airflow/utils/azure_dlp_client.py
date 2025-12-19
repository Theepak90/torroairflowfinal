import os
import logging
from typing import Dict, List, Optional
from pathlib import Path
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from dotenv import load_dotenv

# Load .env from project root (parent of airflow directory)
# azure_dlp_client.py is in airflow/utils/, so we need to go up 3 levels to reach project root
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

# Azure AI Language (PII Detection) configuration
AZURE_AI_LANGUAGE_ENDPOINT = os.getenv("AZURE_AI_LANGUAGE_ENDPOINT", "")
AZURE_AI_LANGUAGE_KEY = os.getenv("AZURE_AI_LANGUAGE_KEY", "")


class AzureDLPClient:
    """Client for Azure AI Language PII detection"""
    
    def __init__(self, endpoint: Optional[str] = None, key: Optional[str] = None):
        self.endpoint = endpoint or AZURE_AI_LANGUAGE_ENDPOINT
        self.key = key or AZURE_AI_LANGUAGE_KEY
        
        if not self.endpoint or not self.key:
            logger.warning('FN:AzureDLPClient.__init__ endpoint:{} key_configured:{}'.format(self.endpoint, bool(self.key)))
            self.client = None
        else:
            try:
                # Remove trailing slash if present (TextAnalyticsClient expects no trailing slash)
                endpoint_clean = self.endpoint.rstrip('/')
                credential = AzureKeyCredential(self.key)
                self.client = TextAnalyticsClient(endpoint=endpoint_clean, credential=credential)
                logger.info('FN:AzureDLPClient.__init__ endpoint:{}'.format(endpoint_clean))
            except Exception as e:
                logger.error('FN:AzureDLPClient.__init__ endpoint:{} error:{}'.format(self.endpoint, str(e)))
                self.client = None
    
    def detect_pii_in_text(self, text: str, language: str = "en") -> Dict:
        """
        Detect PII in a text string using Azure AI Language service
        
        Args:
            text: Text to analyze
            language: Language code (default: "en")
        
        Returns:
            Dict with pii_detected (bool), pii_types (list), and confidence scores
        """
        if not self.client or not text:
            return {
                "pii_detected": False,
                "pii_types": [],
                "entities": []
            }
        
        try:
            # Azure AI Language API has a limit of 5120 characters per document
            # For column names, this should be fine, but we'll truncate if needed
            text_to_analyze = text[:5120] if len(text) > 5120 else text
            
            # Call PII detection API
            result = self.client.recognize_pii_entities([text_to_analyze], language=language)
            
            if not result or len(result) == 0:
                return {
                    "pii_detected": False,
                    "pii_types": [],
                    "entities": []
                }
            
            document_result = result[0]
            
            # Check for errors
            if document_result.is_error:
                logger.warning('FN:detect_pii_in_text text_length:{} language:{} error:{}'.format(len(text_to_analyze), language, document_result.error))
                return {
                    "pii_detected": False,
                    "pii_types": [],
                    "entities": []
                }
            
            # Extract PII entities
            entities = []
            pii_types = []
            
            for entity in document_result.entities:
                entities.append({
                    "text": entity.text,
                    "category": entity.category,
                    "subcategory": entity.subcategory,
                    "confidence_score": entity.confidence_score,
                    "offset": entity.offset,
                    "length": entity.length
                })
                
                # Add category to pii_types if not already present
                category = entity.subcategory or entity.category
                if category and category not in pii_types:
                    pii_types.append(category)
            
            return {
                "pii_detected": len(entities) > 0,
                "pii_types": pii_types,
                "entities": entities
            }
            
        except Exception as e:
            logger.error('FN:detect_pii_in_text text_length:{} language:{} error:{}'.format(len(text) if text else 0, language, str(e)))
            return {
                "pii_detected": False,
                "pii_types": [],
                "entities": []
            }
    
    def detect_pii_in_column_name(self, column_name: str) -> Dict:
        """
        Detect PII in a column name (optimized for column name analysis)
        
        Args:
            column_name: Column name to analyze
        
        Returns:
            Dict with pii_detected (bool) and pii_types (list)
        """
        if not column_name:
            return {
                "pii_detected": False,
                "pii_types": []
            }
        
        # Analyze the column name
        result = self.detect_pii_in_text(column_name)
        
        return {
            "pii_detected": result["pii_detected"],
            "pii_types": result["pii_types"]
        }


# Global instance (initialized on first use)
_dlp_client = None


def get_dlp_client() -> Optional[AzureDLPClient]:
    """Get or create the global Azure DLP client instance"""
    global _dlp_client
    if _dlp_client is None:
        _dlp_client = AzureDLPClient()
    return _dlp_client


def detect_pii_in_column(column_name: str) -> Dict:
    """
    Convenience function to detect PII in a column name using Azure DLP
    Falls back to pattern matching if Azure DLP is not available
    
    Args:
        column_name: Column name to analyze
    
    Returns:
        Dict with pii_detected (bool) and pii_types (list)
    """
    # Try Azure DLP first
    client = get_dlp_client()
    if client and client.client:  # Azure DLP is configured and available
        try:
            result = client.detect_pii_in_column_name(column_name)
            if result.get("pii_detected"):
                logger.info('FN:detect_pii_in_column column_name:{} azure_dlp_detected:True'.format(column_name))
                return result
            # If Azure DLP returns no PII, fall through to pattern matching
        except Exception as e:
            logger.warning('FN:detect_pii_in_column azure_dlp_error:{} falling_back_to_pattern'.format(str(e)))
            # Fall through to pattern matching on error
    
    # Fallback: Pattern matching for common PII column names
    if not column_name:
        return {"pii_detected": False, "pii_types": []}
    
    column_lower = column_name.lower().strip()
    pii_types = []
    
    # Pattern matching for common PII column names
    pii_patterns = {
        "email": ["Email"],
        "e-mail": ["Email"],
        "mail": ["Email"],
        "phone": ["PhoneNumber"],
        "telephone": ["PhoneNumber"],
        "mobile": ["PhoneNumber"],
        "cell": ["PhoneNumber"],
        "ssn": ["SSN"],
        "social": ["SSN"],
        "social_security": ["SSN"],
        "credit_card": ["CreditCardNumber"],
        "creditcard": ["CreditCardNumber"],
        "card_number": ["CreditCardNumber"],
        "cardnumber": ["CreditCardNumber"],
        "cc": ["CreditCardNumber"],
        "passport": ["PassportNumber"],
        "passport_number": ["PassportNumber"],
        "driver": ["DriverLicense"],
        "license": ["DriverLicense"],
        "dl": ["DriverLicense"],
        "bank_account": ["BankAccount"],
        "account_number": ["BankAccount"],
        "accountnumber": ["BankAccount"],
        "address": ["Address"],
        "street": ["Address"],
        "city": ["Address"],
        "zip": ["Address"],
        "postal": ["Address"],
    }
    
    # Check for exact matches or partial matches
    for pattern, types in pii_patterns.items():
        if pattern in column_lower:
            pii_types.extend(types)
    
    # Remove duplicates
    pii_types = list(set(pii_types))
    
    if pii_types:
        logger.info('FN:detect_pii_in_column column_name:{} pattern_matching_detected:True types:{}'.format(column_name, pii_types))
    
    return {
        "pii_detected": len(pii_types) > 0,
        "pii_types": pii_types
    }
