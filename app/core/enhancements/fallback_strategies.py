"""
Fallback Strategies for Islamic Legal AI
Ensures system reliability when primary search methods fail
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class FallbackLevel(Enum):
    """Levels of fallback strategies"""
    PRIMARY = "primary"           # Main search method
    SECONDARY = "secondary"       # Alternative search method
    TERTIARY = "tertiary"        # Basic keyword search
    EMERGENCY = "emergency"       # Hardcoded responses for critical cases


@dataclass
class FallbackResult:
    """Result from fallback strategy"""
    content: str
    confidence: float
    strategy_level: FallbackLevel
    explanation: str
    is_fallback: bool = True


class FallbackStrategy(ABC):
    """Abstract base class for fallback strategies"""
    
    @abstractmethod
    async def execute(self, query: str, concepts: List[Any], context: Dict[str, Any]) -> Optional[FallbackResult]:
        """Execute the fallback strategy"""
        pass
    
    @abstractmethod
    def get_confidence(self) -> float:
        """Get confidence level of this strategy"""
        pass
    
    @abstractmethod
    def can_handle(self, query: str, concepts: List[Any]) -> bool:
        """Check if this strategy can handle the query"""
        pass


class KeywordFallbackStrategy(FallbackStrategy):
    """Keyword-based fallback when vector search fails"""
    
    def __init__(self):
        self.confidence = 0.6
        self.keyword_mappings = {
            # Employment law keywords
            "employment": {
                "keywords": ["موظف", "عامل", "وظيفة", "عمل", "فصل", "راتب", "مستحقات"],
                "response_template": "في الشريعة الإسلامية، حقوق العمال محفوظة ويجب على أصحاب العمل الوفاء بالتزاماتهم. قال تعالى: '{verse}' - {explanation}"
            },
            # Justice keywords
            "justice": {
                "keywords": ["عدالة", "ظلم", "حق", "إنصاف", "قضاء"],
                "response_template": "العدالة أساس الحكم في الإسلام. قال تعالى: '{verse}' - {explanation}"
            },
            # Commercial law keywords
            "commercial": {
                "keywords": ["تجارة", "بيع", "شراء", "عقد", "ربا"],
                "response_template": "في المعاملات التجارية، الإسلام يؤكد على العدل والصدق. قال تعالى: '{verse}' - {explanation}"
            }
        }
        
        # Pre-defined Islamic legal responses for common queries
        self.fallback_responses = {
            "employment_rights": {
                "verse": "إِنَّ اللَّهَ يَأْمُرُكُمْ أَن تُؤَدُّوا الْأَمَانَاتِ إِلَىٰ أَهْلِهَا",
                "reference": "النساء: 58",
                "explanation": "هذه الآية تؤكد على وجوب أداء الأمانات والحقوق لأصحابها، بما في ذلك حقوق العمال"
            },
            "justice_general": {
                "verse": "إِنَّ اللَّهَ يَأْمُرُ بِالْعَدْلِ وَالْإِحْسَانِ",
                "reference": "النحل: 90",
                "explanation": "الله يأمر بالعدل والإحسان في جميع التعاملات والأحكام"
            },
            "commercial_ethics": {
                "verse": "وَأَوْفُوا بِالْعَهْدِ ۖ إِنَّ الْعَهْدَ كَانَ مَسْئُولًا",
                "reference": "الإسراء: 34",
                "explanation": "وجوب الوفاء بالعقود والالتزامات في المعاملات التجارية"
            }
        }
    
    async def execute(self, query: str, concepts: List[Any], context: Dict[str, Any]) -> Optional[FallbackResult]:
        """Execute keyword-based fallback"""
        try:
            query_lower = query.lower()
            
            # Identify relevant domain
            relevant_domain = None
            for domain, data in self.keyword_mappings.items():
                if any(keyword in query_lower for keyword in data["keywords"]):
                    relevant_domain = domain
                    break
            
            if not relevant_domain:
                return None
            
            # Get appropriate response
            response_key = f"{relevant_domain}_rights" if relevant_domain == "employment" else f"{relevant_domain}_general"
            if relevant_domain == "commercial":
                response_key = "commercial_ethics"
            
            if response_key in self.fallback_responses:
                response_data = self.fallback_responses[response_key]
                
                content = f"""
## 🕌 الأساس الشرعي

**الآية الكريمة:**
"{response_data['verse']}"
**المرجع:** {response_data['reference']}

**التفسير والتطبيق:**
{response_data['explanation']}

*هذا الرد مبني على المبادئ الإسلامية العامة. للحصول على استشارة قانونية مفصلة، يرجى مراجعة مختص قانوني.*
"""
                
                return FallbackResult(
                    content=content.strip(),
                    confidence=self.confidence,
                    strategy_level=FallbackLevel.TERTIARY,
                    explanation=f"استخدام الكلمات المفتاحية للمجال: {relevant_domain}",
                    is_fallback=True
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Keyword fallback failed: {e}")
            return None
    
    def get_confidence(self) -> float:
        return self.confidence
    
    def can_handle(self, query: str, concepts: List[Any]) -> bool:
        """Check if any keywords match"""
        query_lower = query.lower()
        for domain_data in self.keyword_mappings.values():
            if any(keyword in query_lower for keyword in domain_data["keywords"]):
                return True
        return False


class EmergencyFallbackStrategy(FallbackStrategy):
    """Emergency fallback for critical system failures"""
    
    def __init__(self):
        self.confidence = 0.3
        self.emergency_response = """
## ⚖️ الاستشارة القانونية

نعتذر، نواجه صعوبة تقنية مؤقتة في الوصول للمصادر الشرعية المفصلة.

**المبادئ الإسلامية العامة:**
- العدالة أساس الحكم في الإسلام
- وجوب الوفاء بالعقود والالتزامات
- حفظ حقوق الناس وعدم الظلم

**للحصول على استشارة قانونية دقيقة:**
- راجع مختص في القانون السعودي
- استشر علماء الشريعة المعتبرين
- ارجع للمصادر الرسمية للنظام السعودي

*نعمل على حل المشكلة التقنية في أقرب وقت ممكن.*
"""
    
    async def execute(self, query: str, concepts: List[Any], context: Dict[str, Any]) -> Optional[FallbackResult]:
        """Execute emergency fallback"""
        return FallbackResult(
            content=self.emergency_response.strip(),
            confidence=self.confidence,
            strategy_level=FallbackLevel.EMERGENCY,
            explanation="استجابة طوارئ لفشل النظام",
            is_fallback=True
        )
    
    def get_confidence(self) -> float:
        return self.confidence
    
    def can_handle(self, query: str, concepts: List[Any]) -> bool:
        """Emergency strategy can always handle requests"""
        return True


class GeneralIslamicPrinciplesFallback(FallbackStrategy):
    """Fallback to general Islamic principles when specific verses aren't found"""
    
    def __init__(self):
        self.confidence = 0.5
        self.general_principles = {
            "justice": {
                "principle": "العدالة",
                "description": "العدالة مبدأ أساسي في الإسلام ويجب تطبيقها في جميع جوانب الحياة",
                "applications": ["في القضاء", "في المعاملات", "في العمل", "في الحكم"]
            },
            "rights": {
                "principle": "حفظ الحقوق",
                "description": "الإسلام يؤكد على ضرورة حفظ حقوق الناس وعدم التعدي عليها",
                "applications": ["حقوق العمال", "حقوق المتعاقدين", "حقوق الأفراد"]
            },
            "covenant": {
                "principle": "الوفاء بالعهود",
                "description": "الوفاء بالعقود والالتزامات مبدأ شرعي أساسي",
                "applications": ["عقود العمل", "العقود التجارية", "الالتزامات القانونية"]
            }
        }
    
    async def execute(self, query: str, concepts: List[Any], context: Dict[str, Any]) -> Optional[FallbackResult]:
        """Execute general principles fallback"""
        try:
            # Identify relevant principles
            relevant_principles = []
            query_lower = query.lower()
            
            if any(word in query_lower for word in ["عدالة", "ظلم", "إنصاف", "قضاء"]):
                relevant_principles.append(self.general_principles["justice"])
            
            if any(word in query_lower for word in ["حق", "حقوق", "مستحقات"]):
                relevant_principles.append(self.general_principles["rights"])
            
            if any(word in query_lower for word in ["عقد", "التزام", "عهد", "اتفاق"]):
                relevant_principles.append(self.general_principles["covenant"])
            
            if not relevant_principles:
                # Default to justice principle
                relevant_principles.append(self.general_principles["justice"])
            
            # Build response
            content_parts = ["## 🕌 المبادئ الإسلامية ذات الصلة\n"]
            
            for principle in relevant_principles:
                content_parts.append(f"**{principle['principle']}:**")
                content_parts.append(f"{principle['description']}\n")
                content_parts.append("**التطبيقات:**")
                for app in principle['applications']:
                    content_parts.append(f"- {app}")
                content_parts.append("")
            
            content_parts.append("*للحصول على تفاصيل أكثر من المصادر الشرعية المحددة، يرجى مراجعة مختص.*")
            
            content = "\n".join(content_parts)
            
            return FallbackResult(
                content=content,
                confidence=self.confidence,
                strategy_level=FallbackLevel.SECONDARY,
                explanation="استخدام المبادئ الإسلامية العامة",
                is_fallback=True
            )
            
        except Exception as e:
            logger.error(f"General principles fallback failed: {e}")
            return None
    
    def get_confidence(self) -> float:
        return self.confidence
    
    def can_handle(self, query: str, concepts: List[Any]) -> bool:
        """Can handle any legal query with general principles"""
        return True


class FallbackOrchestrator:
    """
    Orchestrates fallback strategies when primary search fails
    """
    
    def __init__(self):
        self.strategies = [
            GeneralIslamicPrinciplesFallback(),
            KeywordFallbackStrategy(),
            EmergencyFallbackStrategy()
        ]
    
    async def execute_fallback(self, query: str, concepts: List[Any], 
                             context: Dict[str, Any]) -> Optional[FallbackResult]:
        """
        Execute fallback strategies in order of preference
        """
        logger.warning("Executing fallback strategies - primary search failed")
        
        for strategy in self.strategies:
            try:
                if strategy.can_handle(query, concepts):
                    result = await strategy.execute(query, concepts, context)
                    if result:
                        logger.info(f"Fallback successful with {strategy.__class__.__name__}")
                        return result
            except Exception as e:
                logger.error(f"Fallback strategy {strategy.__class__.__name__} failed: {e}")
                continue
        
        logger.error("All fallback strategies failed")
        return None
    
    def get_available_strategies(self) -> List[str]:
        """Get list of available fallback strategies"""
        return [strategy.__class__.__name__ for strategy in self.strategies]


# Factory function for easy integration
def create_fallback_orchestrator() -> FallbackOrchestrator:
    """
    Factory function to create configured fallback orchestrator
    """
    return FallbackOrchestrator()