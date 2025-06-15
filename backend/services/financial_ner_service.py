import logging
from typing import List, Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialNERService:
    """
    金融术语识别服务
    使用词典匹配识别金融术语
    """
    def __init__(self):
        # 常见金融术语词典
        self.financial_terms = {
            "recession": "FINANCIAL_TERM",
            "inflation": "FINANCIAL_TERM",
            "interest rate": "FINANCIAL_TERM",
            "stock market": "FINANCIAL_TERM",
            "bond": "BOND",
            "stock": "STOCK",
            "fund": "FUND",
            "index": "INDEX",
            "exchange": "EXCHANGE",
            "currency": "CURRENCY",
            "dollar": "CURRENCY",
            "euro": "CURRENCY",
            "yen": "CURRENCY",
            "pound": "CURRENCY",
            "dividend": "FINANCIAL_TERM",
            "yield": "FINANCIAL_TERM",
            "portfolio": "FINANCIAL_TERM",
            "asset": "FINANCIAL_TERM",
            "liability": "FINANCIAL_TERM",
            "equity": "FINANCIAL_TERM",
            "derivative": "FINANCIAL_TERM",
            "option": "FINANCIAL_TERM",
            "futures": "FINANCIAL_TERM",
            "swap": "FINANCIAL_TERM",
            "hedge": "FINANCIAL_TERM",
            "leverage": "FINANCIAL_TERM",
            "margin": "FINANCIAL_TERM",
            "capital": "FINANCIAL_TERM",
            "revenue": "FINANCIAL_TERM",
            "profit": "FINANCIAL_TERM",
            "loss": "FINANCIAL_TERM",
            "balance sheet": "FINANCIAL_TERM",
            "income statement": "FINANCIAL_TERM",
            "cash flow": "FINANCIAL_TERM",
            "audit": "FINANCIAL_TERM",
            "tax": "FINANCIAL_TERM",
            "depreciation": "FINANCIAL_TERM",
            "amortization": "FINANCIAL_TERM",
            "goodwill": "FINANCIAL_TERM",
            "intangible": "FINANCIAL_TERM",
            "tangible": "FINANCIAL_TERM"
        }

    def process(self, text: str, term_types: Dict[str, bool]) -> Dict[str, Any]:
        """
        处理输入文本，识别金融术语
        
        Args:
            text: 输入文本
            term_types: 需要识别的术语类型
            
        Returns:
            包含识别出的实体的字典
        """
        logger.info(f"Processing text: {text}")
        
        # 使用词典匹配识别实体
        entities = self._dictionary_match(text)
        
        return {
            "text": text,
            "entities": entities
        }
    
    def _dictionary_match(self, text: str) -> List[Dict[str, Any]]:
        """
        使用词典匹配识别金融术语
        """
        entities = []
        text_lower = text.lower()
        
        for term, entity_type in self.financial_terms.items():
            start = 0
            while True:
                start = text_lower.find(term.lower(), start)
                if start == -1:
                    break
                entities.append({
                    'word': text[start:start+len(term)],
                    'entity_group': entity_type,
                    'start': start,
                    'end': start + len(term),
                    'score': 1.0
                })
                start += len(term)
        
        return entities 