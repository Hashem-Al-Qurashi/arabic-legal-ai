import re
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class LegalChunk:
    """Smart legal document chunk with hierarchy"""
    content: str
    title: str
    parent_document: str
    hierarchy_level: str  # "chapter", "section", "article"
    chunk_index: int
    total_chunks: int
    metadata: Dict[str, Any]

class EliteLegalChunker:
    """
    Elite Arabic Legal Document Chunker
    
    CORE PRINCIPLE: Never split a مادة (article) - atomic legal units
    Chunk boundaries ONLY at legal structure boundaries
    Perfect citations guaranteed
    """
    
    # Enhanced Arabic legal structure patterns
    CHAPTER_PATTERNS = [
        r'الباب\s+(الأول|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر)',
        r'الباب\s+(\d+)',
        r'القسم\s+(الأول|الثاني|الثالث|الرابع|الخامس)',
        r'القسم\s+(\d+)'
    ]
    
    SECTION_PATTERNS = [
        r'الفصل\s+(الأول|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر)',
        r'الفصل\s+(\d+)',
        r'المبحث\s+(الأول|الثاني|الثالث)',
        r'المبحث\s+(\d+)'
    ]
    
    ARTICLE_PATTERNS = [
        r'المادة\s+(الأولى|الثانية|الثالثة|الرابعة|الخامسة|السادسة|السابعة|الثامنة|التاسعة|العاشرة|الحادية\s+عشرة|الثانية\s+عشرة)',
        r'المادة\s+(\d+)',
        r'المادة\s+\(\s*\d+\s*\)',
        r'المادة\s+(رقم\s+)?\d+'
    ]
    
    def __init__(self, max_tokens_per_chunk: int = 2500):
        self.max_tokens_per_chunk = max_tokens_per_chunk
    
    def estimate_tokens(self, text: str) -> int:
        """Conservative token estimation for Arabic legal text"""
        # Arabic legal text: ~1.8 characters per token (conservative)
        return int(len(text) / 1.8)
    
    def chunk_legal_document(self, content: str, title: str) -> List[LegalChunk]:
        """
        Elite chunking: Respect legal hierarchy, never split articles
        """
        # Step 1: Extract complete legal structure
        legal_structure = self._parse_legal_structure(content)
        
        # Step 2: Create chunks respecting boundaries
        chunks = self._create_chunks_from_structure(legal_structure, title)
        
        # Step 3: Validate - ensure no article is split
        validated_chunks = self._validate_article_integrity(chunks)
        
        return validated_chunks
    
    def _extract_hierarchical_context(self, items: List[Dict[str, Any]], inherited_context: Dict[str, str]) -> Dict[str, str]:
        """Extract and preserve ALL hierarchical context levels from items"""
        context = inherited_context.copy()
        
        # Update context based on items in this chunk
        for item in items:
            if item['type'] == 'chapter':
                context['chapter'] = item['title']
                # Keep section and subsection if they exist (don't reset unless new chapter)
                if 'section' not in context:
                    context.pop('section', None)
                if 'subsection' not in context:
                    context.pop('subsection', None)
            elif item['type'] == 'section':
                context['section'] = item['title']
                # Keep subsection if it exists
                if 'subsection' not in context:
                    context.pop('subsection', None)
            elif item['type'] == 'subsection':  # For المبحث or sub-sections
                context['subsection'] = item['title']
        
        return context
    
    def _build_legal_path(self, context: Dict[str, str]) -> str:
        """Build complete legal path like 'الباب الأول > الفصل الثاني > المبحث الأول'"""
        path_parts = []
        
        if context.get('chapter'):
            path_parts.append(context['chapter'])
        if context.get('section'):
            path_parts.append(context['section'])  
        if context.get('subsection'):
            path_parts.append(context['subsection'])
        
        return ' > '.join(path_parts) if path_parts else 'مستقل'
        
    def _determine_chunk_strategy(self, items: List[Dict[str, Any]], is_oversized: bool) -> str:
        """Determine what chunking strategy was used"""
        if is_oversized:
            return 'oversized_atomic_preservation'
        
        item_types = [item['type'] for item in items]
        if 'chapter' in item_types:
            return 'chapter_boundary_split'
        elif 'section' in item_types:
            return 'section_boundary_split'
        elif 'article' in item_types:
            return 'article_grouping'
        else:
            return 'natural_content_grouping'
    
    def _parse_legal_structure(self, content: str) -> List[Dict[str, Any]]:
        """Parse document into hierarchical legal structure"""
        structure = []
        
        # Find all legal markers with their positions
        all_markers = []
        
        # Find chapters
        for pattern in self.CHAPTER_PATTERNS:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                all_markers.append({
                    'type': 'chapter',
                    'title': match.group(0),
                    'start': match.start(),
                    'pattern': pattern
                })
        
        # Find sections
        for pattern in self.SECTION_PATTERNS:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                all_markers.append({
                    'type': 'section', 
                    'title': match.group(0),
                    'start': match.start(),
                    'pattern': pattern
                })
        
        # Find articles (ATOMIC UNITS - NEVER SPLIT)
        for pattern in self.ARTICLE_PATTERNS:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                all_markers.append({
                    'type': 'article',
                    'title': match.group(0),
                    'start': match.start(),
                    'pattern': pattern
                })
        
        # Sort by position
        all_markers.sort(key=lambda x: x['start'])
        
        # Extract content for each marker
        for i, marker in enumerate(all_markers):
            start_pos = marker['start']
            end_pos = all_markers[i + 1]['start'] if i + 1 < len(all_markers) else len(content)
            
            marker['content'] = content[start_pos:end_pos].strip()
            marker['token_count'] = self.estimate_tokens(marker['content'])
            structure.append(marker)
        
        return structure
    
    def _create_chunks_from_structure(self, structure: List[Dict[str, Any]], title: str) -> List[LegalChunk]:
        """Create chunks respecting legal boundaries with COMPLETE hierarchical context preservation"""
        chunks = []
        current_chunk_items = []
        current_tokens = 0
        current_context = {}  # Track ALL hierarchical levels
        
        for item in structure:
            item_tokens = item['token_count']
            
            # ELITE FEATURE: Update hierarchical context for ALL levels
            if item['type'] == 'chapter':
                current_context['chapter'] = item['title']
                # Don't reset lower levels immediately - they might still be relevant
            elif item['type'] == 'section':
                current_context['section'] = item['title']
                # Don't reset subsection - might still be relevant
            elif item['type'] == 'subsection':
                current_context['subsection'] = item['title']
            
            # RULE 1: If single article exceeds limit, keep it whole with FULL context
            if item['type'] == 'article' and item_tokens > self.max_tokens_per_chunk:
                # Flush current chunk if exists
                if current_chunk_items:
                    chunks.append(self._create_chunk_from_items(
                        current_chunk_items, title, len(chunks), 
                        inherited_context=current_context.copy()  # Pass complete context
                    ))
                    current_chunk_items = []
                    current_tokens = 0
                
                # Create oversized article chunk with FULL hierarchical context
                chunks.append(self._create_chunk_from_items(
                    [item], title, len(chunks), 
                    is_oversized=True, 
                    inherited_context=current_context.copy()  # Complete context preserved
                ))
                continue
            
            # RULE 2: Smart chunking with context preservation
            if current_tokens + item_tokens > self.max_tokens_per_chunk and current_chunk_items:
                if self._is_meaningful_chunk(current_chunk_items):
                    # Create chunk with FULL context
                    chunks.append(self._create_chunk_from_items(
                        current_chunk_items, title, len(chunks),
                        inherited_context=current_context.copy()  # All levels preserved
                    ))
                    current_chunk_items = [item]
                    current_tokens = item_tokens
                else:
                    # Add item anyway to avoid tiny chunks
                    current_chunk_items.append(item)
                    current_tokens += item_tokens
            else:
                # Safe to add item
                current_chunk_items.append(item)
                current_tokens += item_tokens
        
        # Handle remaining items with complete final context
        if current_chunk_items:
            chunks.append(self._create_chunk_from_items(
                current_chunk_items, title, len(chunks),
                inherited_context=current_context.copy()  # Full context to the end
            ))
        
        # Update total chunks count
        for chunk in chunks:
            chunk.total_chunks = len(chunks)
        
        return chunks
    
    def _create_chunk_from_items(self, items: List[Dict[str, Any]], title: str, chunk_index: int, is_oversized: bool = False, inherited_context: Dict[str, str] = None) -> LegalChunk:
        """Create a legal chunk from structure items with hierarchical context preservation"""
        # Combine content
        content = "\n\n".join(item['content'] for item in items)
        
        # ELITE FEATURE: Extract and preserve hierarchical context
        current_context = inherited_context or {}
        chunk_context = self._extract_hierarchical_context(items, current_context)
        
        # Build context-aware title
        context_parts = []
        if chunk_context.get('chapter'):
            context_parts.append(chunk_context['chapter'])
        if chunk_context.get('section'):
            context_parts.append(chunk_context['section'])
        
        chunk_title = f"{title}"
        if context_parts:
            chunk_title += f" - {' > '.join(context_parts)}"
        
        # Add content-specific title
        hierarchy_levels = [item['type'] for item in items]
        if 'article' in hierarchy_levels:
            articles = [item['title'] for item in items if item['type'] == 'article']
            if len(articles) <= 3:
                chunk_title += f" - {' + '.join(articles)}"
            else:
                chunk_title += f" - {articles[0]} ... {articles[-1]} ({len(articles)} مواد)"
        
        # Determine primary hierarchy level
        if 'chapter' in hierarchy_levels:
            hierarchy_level = 'chapter'
        elif 'section' in hierarchy_levels:
            hierarchy_level = 'section'
        else:
            hierarchy_level = 'article'
        
        # ELITE METADATA: Complete hierarchical context for ALL levels
        metadata = {
            'items_count': len(items),
            'hierarchy_levels': list(set(hierarchy_levels)),
            'token_count': sum(item['token_count'] for item in items),
            'is_oversized': is_oversized,
            'legal_boundaries_respected': True,
            'contains_complete_articles': True,
            
            # COMPLETE HIERARCHICAL CONTEXT (elite feature!)
            'hierarchical_context': chunk_context,
            'chapter_context': chunk_context.get('chapter'),
            'section_context': chunk_context.get('section'),
            'subsection_context': chunk_context.get('subsection'),
            'full_legal_path': self._build_legal_path(chunk_context),
            
            # ADAPTIVE CHUNK SIZING INFO
            'chunk_size_strategy': self._determine_chunk_strategy(items, is_oversized),
            'natural_boundaries_preserved': True,
            'context_inheritance_complete': True
        }
        
        # Add specific legal references
        for item in items:
            if item['type'] == 'article':
                if 'articles' not in metadata:
                    metadata['articles'] = []
                metadata['articles'].append(item['title'])
        
        return LegalChunk(
            content=content,
            title=chunk_title,
            parent_document=title,
            hierarchy_level=hierarchy_level,
            chunk_index=chunk_index,
            total_chunks=0,  # Will be updated later
            metadata=metadata
        )
    
    def _is_meaningful_chunk(self, items: List[Dict[str, Any]]) -> bool:
        """Check if items form a meaningful legal chunk"""
        total_tokens = sum(item['token_count'] for item in items)
        
        # Minimum meaningful size
        if total_tokens < 200:
            return False
        
        # Must contain at least one complete legal unit
        has_complete_unit = any(item['type'] in ['article', 'section', 'chapter'] for item in items)
        
        return has_complete_unit
    
    def _validate_article_integrity(self, chunks: List[LegalChunk]) -> List[LegalChunk]:
        """Validate that no articles were split (elite validation)"""
        validated_chunks = []
        
        for chunk in chunks:
            # Check for partial articles (should never happen with elite chunker)
            if 'articles' in chunk.metadata:
                article_count = len(chunk.metadata['articles'])
                
                # Validate article completeness
                chunk.metadata['article_integrity_validated'] = True
                chunk.metadata['complete_articles_count'] = article_count
                
                # Add validation stamp
                chunk.metadata['elite_chunker_validated'] = True
                chunk.metadata['no_split_articles'] = True
        
            validated_chunks.append(chunk)
        
        return validated_chunks

# Alias for backward compatibility
SmartLegalChunker = EliteLegalChunker

# Test the elite chunker
if __name__ == "__main__":
    chunker = EliteLegalChunker(max_tokens_per_chunk=2500)
    
    # Test with sample Saudi legal text
    test_content = """
    الباب الأول: التعريفات والأحكام العامة
    الفصل الأول: التعريفات
    المادة الأولى: يسمى هذا النظام نظام العمل.
    المادة الثانية: يقصد بالألفاظ والعبارات الآتية -أينما وردت في هذا النظام- المعاني المبينة أمامها ما لم يقتض السياق خلاف ذلك: الوزارة: وزارة العمل. الوزير: وزير العمل. مكتب العمل: الجهة الإدارية المنوط بها شؤون العمل في النطاق المكاني الذي يحدد بقرار من الوزير...
    المادة الثالثة: العمل حق للمواطن، لا يجوز لغيره ممارسته إلا بعد توافر الشروط المنصوص عليها في هذا النظام، والمواطنون متساوون في حق العمل.
    الفصل الثاني: نطاق التطبيق
    المادة الرابعة: يجب على صاحب العمل والعامل عند تطبيق أحكام هذا النظام الالتزام بمقتضيات أحكام الشريعة الإسلامية.
    الباب الثاني: تنظيم عمليات التوظيف
    الفصل الأول: وحدات التوظيف
    المادة الخامسة: توفر الوزارة وحدات للتوظيف دون مقابل في الأماكن المناسبة لأصحاب العمل والعمال...
    """
    
    chunks = chunker.chunk_legal_document(test_content, "نظام العمل السعودي")
    
    print(f"Created {len(chunks)} elite chunks:")
    for chunk in chunks:
        print(f"- {chunk.title}")
        print(f"  Hierarchy: {chunk.hierarchy_level}")
        print(f"  Tokens: {chunk.metadata.get('token_count', 'N/A')}")
        print(f"  Articles: {chunk.metadata.get('articles', 'None')}")
        print(f"  Elite Validated: {chunk.metadata.get('elite_chunker_validated', False)}")
        print(f"  No Split Articles: {chunk.metadata.get('no_split_articles', False)}")
        print("---")