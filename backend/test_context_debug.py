#!/usr/bin/env python3
"""
Debug script for context classification
"""

import sys
sys.path.append('/home/sakr_quraish/Desktop/arabic_legal_ai/backend')

from app.core.contextual_filter_engine import ContextualFilterEngine

def debug_classification():
    """Debug classification issues"""
    
    config_path = "/home/sakr_quraish/Desktop/arabic_legal_ai/backend/config/context_classification_rules.yaml"
    engine = ContextualFilterEngine(config_path)
    
    test_queries = [
        "هل يلزم العامل رد رسوم المرافقين؟",
        "ما حقوق الموظف في قانون العمل؟", 
        "كيف يتم احتساب مكافأة نهاية الخدمة؟",
        "ما هي إجراءات فصل الموظف؟"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        result = engine.classify_query_context(query)
        
        print(f"   Primary Context: {result.primary_context.value}")
        print(f"   Confidence: {result.confidence_score:.3f}")
        print(f"   Level: {result.confidence_level.value}")
        print(f"   Indicators Found: {result.indicators_found}")
        print(f"   Raw Scores: {result.raw_scores}")
        print(f"   Decision Factors: {result.decision_factors}")

if __name__ == "__main__":
    debug_classification()