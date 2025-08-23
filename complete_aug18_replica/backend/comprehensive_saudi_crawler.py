#!/usr/bin/env python3
"""
🇸🇦 COMPREHENSIVE SAUDI LEGAL SITE CRAWLER
==========================================

MISSION: Crawl the entire Saudi legal system with all categories, subcategories,
pagination, and individual laws. Handle the complex navigation structure.

ARCHITECTURE:
- Level 1: Main categories (أنظمة أساسية, أنظمة عادية, etc.)
- Level 2: Domain categories (التجارة والاقتصاد, العمل والرعاية, etc.)
- Level 3: Individual laws with pagination
- Level 4: Individual law documents
"""

import asyncio
import json
import logging
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse
from datetime import datetime
import re
from pathlib import Path
import time

from playwright.async_api import async_playwright, Page, BrowserContext
from bs4 import BeautifulSoup

@dataclass
class LawCategory:
    """Represents a law category in the Saudi legal system"""
    name: str
    url: str
    parent_category: Optional[str] = None
    law_count: int = 0
    subcategories: List[str] = None
    
    def __post_init__(self):
        if self.subcategories is None:
            self.subcategories = []

@dataclass
class LawDocument:
    """Represents an individual law document"""
    title: str
    url: str
    category: str
    subcategory: str
    law_type: str  # "أنظمة أساسية", "أنظمة عادية", etc.
    page_number: int
    extraction_timestamp: datetime = None
    
    def __post_init__(self):
        if self.extraction_timestamp is None:
            self.extraction_timestamp = datetime.now()

class ComprehensiveSaudiLegalCrawler:
    """
    🇸🇦 Complete Saudi Legal System Crawler
    
    Handles the complex multi-level navigation:
    1. Main categories (4 buttons)
    2. Domain categories (18+ per main category)  
    3. Pagination (multiple pages per domain)
    4. Individual law documents
    """
    
    def __init__(self, base_url: str = "https://laws.boe.gov.sa", max_concurrent: int = 3):
        self.base_url = base_url
        self.max_concurrent = max_concurrent
        self.discovered_urls: Set[str] = set()
        self.processed_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        
        # Results storage
        self.categories: List[LawCategory] = []
        self.law_documents: List[LawDocument] = []
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        # Navigation selectors for Saudi legal site
        self.selectors = {
            'main_categories': '.law-categories .category-button',  # Adjust based on actual HTML
            'domain_categories': '.domain-list .domain-item a',
            'law_links': '.law-list .law-item a',
            'pagination': '.pagination a',
            'next_page': '.pagination .next-page',
        }
    
    def _setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('saudi_comprehensive_crawler.log'),
                logging.StreamHandler()
            ]
        )
    
    async def crawl_comprehensive(self) -> Dict[str, any]:
        """
        🚀 MAIN CRAWLER: Complete Saudi legal system crawl
        """
        self.logger.info("🇸🇦 Starting comprehensive Saudi legal system crawl...")
        
        start_time = datetime.now()
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            try:
                # Phase 1: Discover main categories
                await self._discover_main_categories(context)
                
                # Phase 2: Discover domain categories  
                await self._discover_domain_categories(context)
                
                # Phase 3: Crawl all laws with pagination
                await self._crawl_all_laws_with_pagination(context)
                
                # Phase 4: Extract individual law documents
                await self._extract_law_documents(context)
                
            finally:
                await browser.close()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Generate comprehensive report
        report = self._generate_comprehensive_report(duration)
        self._save_comprehensive_results(report)
        
        return report
    
    async def _discover_main_categories(self, context: BrowserContext):
        """
        Phase 1: Discover main categories (أنظمة أساسية, أنظمة عادية, etc.)
        """
        self.logger.info("📋 Phase 1: Discovering main categories...")
        
        page = await context.new_page()
        
        try:
            await page.goto(f"{self.base_url}/BoeLaws/Laws")
            await page.wait_for_load_state('networkidle')
            
            # Extract main categories - adjust selectors based on actual HTML
            main_categories = await self._extract_main_categories(page)
            
            self.logger.info(f"✅ Found {len(main_categories)} main categories")
            
            for category in main_categories:
                self.categories.append(LawCategory(
                    name=category['name'],
                    url=category['url'],
                    parent_category=None
                ))
                
        except Exception as e:
            self.logger.error(f"❌ Failed to discover main categories: {e}")
        finally:
            await page.close()
    
    async def _extract_main_categories(self, page: Page) -> List[Dict[str, str]]:
        """Extract main categories from the page"""
        
        # Method 1: Try to find category buttons/links
        categories = []
        
        # Look for the 4 main category buttons you mentioned
        main_category_names = [
            "أنظمة أساسية",
            "أنظمة عادية", 
            "لوائح وما في حكمها",
            "تنظيمات، وترتيبات تنظيمية"
        ]
        
        for category_name in main_category_names:
            # Try to find links/buttons containing these category names
            category_element = await page.query_selector(f'text="{category_name}"')
            if category_element:
                # Get the URL - might be in href or onclick
                url = await category_element.get_attribute('href')
                if not url:
                    # Try to find parent link
                    parent_link = await category_element.query_selector('xpath=.//ancestor::a[1]')
                    if parent_link:
                        url = await parent_link.get_attribute('href')
                
                if url:
                    categories.append({
                        'name': category_name,
                        'url': urljoin(self.base_url, url)
                    })
                    self.logger.info(f"✅ Found category: {category_name} -> {url}")
        
        # Method 2: Generic category discovery if specific names don't work
        if not categories:
            self.logger.info("🔍 Trying generic category discovery...")
            category_elements = await page.query_selector_all('a[href*="Laws"]')
            
            for element in category_elements[:10]:  # Limit to reasonable number
                text = await element.inner_text()
                href = await element.get_attribute('href')
                
                if text and href and len(text.strip()) > 3:
                    categories.append({
                        'name': text.strip(),
                        'url': urljoin(self.base_url, href)
                    })
        
        return categories
    
    async def _discover_domain_categories(self, context: BrowserContext):
        """
        Phase 2: For each main category, discover domain categories
        (التجارة والاقتصاد, العمل والرعاية, etc.)
        """
        self.logger.info("🏢 Phase 2: Discovering domain categories...")
        
        for main_category in self.categories:
            self.logger.info(f"🔍 Exploring domains in: {main_category.name}")
            
            page = await context.new_page()
            
            try:
                await page.goto(main_category.url)
                await page.wait_for_load_state('networkidle')
                
                # Extract domain categories
                domain_categories = await self._extract_domain_categories(page, main_category.name)
                
                self.logger.info(f"✅ Found {len(domain_categories)} domains in {main_category.name}")
                
                # Add domain categories
                for domain in domain_categories:
                    self.categories.append(LawCategory(
                        name=domain['name'],
                        url=domain['url'],
                        parent_category=main_category.name
                    ))
                    
            except Exception as e:
                self.logger.error(f"❌ Failed to discover domains in {main_category.name}: {e}")
            finally:
                await page.close()
    
    async def _extract_domain_categories(self, page: Page, main_category: str) -> List[Dict[str, str]]:
        """Extract domain categories from a main category page"""
        
        domains = []
        
        # Domain names you mentioned for "أنظمة عادية"
        if main_category == "أنظمة عادية":
            known_domains = [
                "الإعلام والثقافة والنشر",
                "الأمن الداخلي والأحوال المدنية والأنظمة الجنائية", 
                "التجارة والاقتصاد والاستثمار",
                "التشريفات والمراسم والسلك الدبلوماسي",
                "التعليم والعلوم",
                "الحج والشؤون الإسلامية",
                "الخدمات البلدية والتخطيط والتطوير الحضري",
                "الخدمة العسكرية",
                "الخدمة المدنية", 
                "الزراعة والمياه والثروات الحية",
                "السلطة القضائية وحقوق الإنسان",
                "السياحة والآثار",
                "الشباب والرياضة",
                "الصحة",
                "الطاقة والصناعة والتعدين",
                "العمل والرعاية الاجتماعية",
                "المال والرقابة",
                "المواصلات والاتصالات"
            ]
            
            # Try to find links for these domains
            for domain_name in known_domains:
                domain_element = await page.query_selector(f'text="{domain_name}"')
                if domain_element:
                    # Try to get URL
                    url = await domain_element.get_attribute('href')
                    if not url:
                        parent_link = await domain_element.query_selector('xpath=.//ancestor::a[1]')
                        if parent_link:
                            url = await parent_link.get_attribute('href')
                    
                    if url:
                        domains.append({
                            'name': domain_name,
                            'url': urljoin(self.base_url, url)
                        })
        
        # Generic domain discovery
        if not domains:
            self.logger.info("🔍 Trying generic domain discovery...")
            
            # Look for common link patterns
            domain_links = await page.query_selector_all('a[href*="category"], a[href*="domain"], .category-link, .domain-link')
            
            for link in domain_links:
                text = await link.inner_text()
                href = await link.get_attribute('href')
                
                if text and href and len(text.strip()) > 5:
                    domains.append({
                        'name': text.strip(), 
                        'url': urljoin(self.base_url, href)
                    })
        
        return domains
    
    async def _crawl_all_laws_with_pagination(self, context: BrowserContext):
        """
        Phase 3: For each domain category, crawl all laws across all pages
        """
        self.logger.info("📚 Phase 3: Crawling all laws with pagination...")
        
        domain_categories = [cat for cat in self.categories if cat.parent_category]
        
        for domain in domain_categories:
            self.logger.info(f"📖 Crawling laws in domain: {domain.name}")
            
            page = await context.new_page()
            
            try:
                current_page = 1
                has_more_pages = True
                
                while has_more_pages:
                    self.logger.info(f"📄 Processing page {current_page} of {domain.name}")
                    
                    # Navigate to current page
                    page_url = self._build_page_url(domain.url, current_page)
                    await page.goto(page_url)
                    await page.wait_for_load_state('networkidle')
                    
                    # Extract laws from current page
                    laws = await self._extract_laws_from_page(page, domain, current_page)
                    
                    self.logger.info(f"✅ Found {len(laws)} laws on page {current_page}")
                    
                    # Add laws to collection
                    self.law_documents.extend(laws)
                    
                    # Check for next page
                    has_more_pages = await self._has_next_page(page)
                    current_page += 1
                    
                    # Safety limit
                    if current_page > 20:  # Adjust based on expected pages
                        self.logger.warning(f"⚠️ Reached page limit for {domain.name}")
                        break
                        
            except Exception as e:
                self.logger.error(f"❌ Failed to crawl laws in {domain.name}: {e}")
            finally:
                await page.close()
    
    def _build_page_url(self, base_url: str, page_number: int) -> str:
        """Build URL for specific page number"""
        if page_number == 1:
            return base_url
        
        # Common pagination patterns
        if '?' in base_url:
            return f"{base_url}&page={page_number}"
        else:
            return f"{base_url}?page={page_number}"
    
    async def _extract_laws_from_page(self, page: Page, domain: LawCategory, page_number: int) -> List[LawDocument]:
        """Extract individual law links from a domain page"""
        
        laws = []
        
        # Look for law links - adjust selectors based on actual HTML
        law_selectors = [
            'a[href*="LawDetails"]',  # Most likely pattern
            '.law-item a',
            '.law-link', 
            'a[href*="Laws/Law"]',
            'a[href*="/Laws/"]'
        ]
        
        for selector in law_selectors:
            law_links = await page.query_selector_all(selector)
            
            if law_links:
                self.logger.info(f"✅ Found {len(law_links)} law links using selector: {selector}")
                
                for link in law_links:
                    try:
                        title = await link.inner_text()
                        href = await link.get_attribute('href')
                        
                        if title and href and len(title.strip()) > 3:
                            laws.append(LawDocument(
                                title=title.strip(),
                                url=urljoin(self.base_url, href),
                                category=domain.parent_category or "Unknown",
                                subcategory=domain.name,
                                law_type=domain.parent_category or "Unknown",
                                page_number=page_number
                            ))
                            
                    except Exception as e:
                        self.logger.error(f"❌ Failed to extract law link: {e}")
                
                break  # Use first successful selector
        
        return laws
    
    async def _has_next_page(self, page: Page) -> bool:
        """Check if there's a next page in pagination"""
        
        # Look for next page indicators
        next_selectors = [
            '.pagination .next',
            '.pagination a[href*="page"]',
            'a:has-text("التالي")',
            'a:has-text("Next")',
            '.next-page'
        ]
        
        for selector in next_selectors:
            next_element = await page.query_selector(selector)
            if next_element:
                # Check if it's clickable (not disabled)
                is_disabled = await next_element.get_attribute('disabled')
                classes = await next_element.get_attribute('class') or ""
                
                if not is_disabled and 'disabled' not in classes:
                    return True
        
        return False
    
    async def _extract_law_documents(self, context: BrowserContext):
        """
        Phase 4: Extract individual law documents (optional - depends on needs)
        """
        self.logger.info("📄 Phase 4: Extracting law documents...")
        
        # For now, just log the count - actual extraction can be done separately
        self.logger.info(f"📊 Ready to extract {len(self.law_documents)} individual law documents")
        
        # Uncomment if you want to extract all documents immediately
        # for law_doc in self.law_documents[:10]:  # Extract first 10 as test
        #     await self._extract_single_law_document(context, law_doc)
    
    def _generate_comprehensive_report(self, duration: float) -> Dict[str, any]:
        """Generate comprehensive crawling report"""
        
        main_categories = [cat for cat in self.categories if not cat.parent_category]
        domain_categories = [cat for cat in self.categories if cat.parent_category]
        
        # Group laws by category
        laws_by_category = {}
        for law in self.law_documents:
            if law.category not in laws_by_category:
                laws_by_category[law.category] = []
            laws_by_category[law.category].append(law)
        
        return {
            'crawl_summary': {
                'total_duration_seconds': duration,
                'crawl_timestamp': datetime.now().isoformat(),
                'base_url': self.base_url,
                'max_concurrent': self.max_concurrent
            },
            'discovery_results': {
                'main_categories_found': len(main_categories),
                'domain_categories_found': len(domain_categories),
                'total_law_documents_found': len(self.law_documents),
                'failed_urls': len(self.failed_urls)
            },
            'categories': {
                'main_categories': [cat.name for cat in main_categories],
                'domain_categories': [cat.name for cat in domain_categories],
                'category_breakdown': laws_by_category
            },
            'pagination_analysis': {
                'max_pages_per_domain': max([law.page_number for law in self.law_documents] or [1]),
                'total_pages_crawled': len(set((law.subcategory, law.page_number) for law in self.law_documents)),
            },
            'law_documents': [asdict(law) for law in self.law_documents],
            'quality_metrics': {
                'successful_categories': len([cat for cat in self.categories if cat.name]),
                'coverage_percentage': (len(self.law_documents) / max(len(self.discovered_urls), 1)) * 100,
                'error_rate': len(self.failed_urls) / max(len(self.discovered_urls), 1) * 100
            }
        }
    
    def _save_comprehensive_results(self, report: Dict[str, any]):
        """Save comprehensive crawling results"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_dir = Path(f'saudi_comprehensive_crawl_{timestamp}')
        results_dir.mkdir(exist_ok=True)
        
        # Save main report
        with open(results_dir / 'comprehensive_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        # Save law documents list for easy processing
        law_urls = [law.url for law in self.law_documents]
        with open(results_dir / 'law_urls.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(law_urls))
        
        # Save categories
        with open(results_dir / 'categories.json', 'w', encoding='utf-8') as f:
            json.dump([asdict(cat) for cat in self.categories], f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"📁 Results saved to: {results_dir}")
        self.logger.info(f"🎯 COMPREHENSIVE CRAWL COMPLETE!")
        self.logger.info(f"   📋 Categories: {len(self.categories)}")
        self.logger.info(f"   📚 Law Documents: {len(self.law_documents)}")

# Usage example
async def main():
    """Run comprehensive Saudi legal crawler"""
    
    crawler = ComprehensiveSaudiLegalCrawler(
        base_url="https://laws.boe.gov.sa",
        max_concurrent=3
    )
    
    results = await crawler.crawl_comprehensive()
    
    print("🇸🇦 COMPREHENSIVE SAUDI LEGAL CRAWL COMPLETED!")
    print(f"📊 Categories found: {results['discovery_results']['main_categories_found']} main, {results['discovery_results']['domain_categories_found']} domains")
    print(f"📚 Law documents found: {results['discovery_results']['total_law_documents_found']}")
    print(f"⏱️ Duration: {results['crawl_summary']['total_duration_seconds']:.1f} seconds")

if __name__ == "__main__":
    asyncio.run(main())