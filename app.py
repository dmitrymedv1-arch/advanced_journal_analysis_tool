import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote
import re
from collections import Counter, defaultdict
import json
from datetime import datetime, timedelta
import io
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import base64
import os
import random
import seaborn as sns
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict, Any, Optional, Union, Type
from dataclasses import dataclass
from enum import Enum
import logging
from pydantic import BaseModel, validator
import httpx
import asyncio
from contextlib import asynccontextmanager
import diskcache
from functools import wraps

# Import translation manager
from languages import translation_manager

# =============================================================================
# ENHANCED CACHE MANAGEMENT
# =============================================================================

# Additional caching layers for performance optimization
_issn_normalization_cache = {}
_journal_search_cache = {}
_author_extraction_cache = {}
_doi_validity_cache = {}
_metrics_calculation_cache = {}
_excel_format_cache = {}
_ror_search_cache = {}
_orcid_search_cache = {}
_article_data_cache = {}
_journal_info_cache = {}

def cached_extract_article_data(metadata):
    """Кэшированное извлечение всех данных статьи"""
    if not metadata:
        return {'authors': [], 'affiliations': [], 'countries': []}
    
    cache_key = hash(json.dumps(metadata, sort_keys=True) if isinstance(metadata, dict) else str(metadata))
    if cache_key in _article_data_cache:
        return _article_data_cache[cache_key]
    
    authors, affiliations, countries = extract_affiliations_and_countries(metadata.get('openalex'))
    
    result = {
        'authors': authors,
        'affiliations': affiliations, 
        'countries': countries
    }
    
    _article_data_cache[cache_key] = result
    return result

def cached_extract_journal_info(metadata):
    """Кэшированное извлечение информации о журнале"""
    if not metadata:
        return {'issn': [], 'journal_name': '', 'publisher': ''}
    
    cache_key = hash(json.dumps(metadata, sort_keys=True) if isinstance(metadata, dict) else str(metadata))
    if cache_key in _journal_info_cache:
        return _journal_info_cache[cache_key]
    
    result = extract_journal_info(metadata)
    _journal_info_cache[cache_key] = result
    return result

def clear_old_cache():
    """Clear outdated caches to free memory"""
    current_time = time.time()
    cache_dicts = [
        _issn_normalization_cache, _journal_search_cache, _author_extraction_cache,
        _doi_validity_cache, _metrics_calculation_cache, _excel_format_cache,
        _ror_search_cache, _orcid_search_cache
    ]
    
    for cache_dict in cache_dicts:
        try:
            # Remove entries older than 1 hour
            keys_to_remove = [k for k, v in cache_dict.items() 
                             if hasattr(v, 'timestamp') and current_time - v.timestamp > 3600]
            for key in keys_to_remove:
                del cache_dict[key]
        except Exception:
            # If cache doesn't have timestamps, skip
            pass

def cached_normalize_issn(issn):
    """Cached version of ISSN normalization"""
    if issn in _issn_normalization_cache:
        return _issn_normalization_cache[issn]
    result = normalize_issn_for_comparison(issn)
    _issn_normalization_cache[issn] = result
    return result

def cached_get_journal_name(issn):
    """Cached journal name lookup"""
    cache_key = f"journal_name_{issn}"
    if cache_key in _journal_search_cache:
        return _journal_search_cache[cache_key]
    result = get_journal_name(issn)
    _journal_search_cache[cache_key] = result
    return result

def cached_extract_authors(openalex_data):
    """Cached author extraction"""
    if not openalex_data:
        return [], [], []
    
    cache_key = hash(json.dumps(openalex_data, sort_keys=True) if isinstance(openalex_data, dict) else str(openalex_data))
    if cache_key in _author_extraction_cache:
        return _author_extraction_cache[cache_key]
    
    result = extract_affiliations_and_countries(openalex_data)
    _author_extraction_cache[cache_key] = result
    return result

def is_valid_doi_cached(doi):
    """Cached DOI validation"""
    if doi in _doi_validity_cache:
        return _doi_validity_cache[doi]
    
    is_valid = doi and doi.startswith('10.') and '/' in doi and len(doi) > 10
    _doi_validity_cache[doi] = is_valid
    return is_valid

# =============================================================================
# PARALLEL PROCESSING FUNCTIONS
# =============================================================================

def get_optimal_workers():
    """Determine optimal number of threads based on system resources"""
    cpu_count = os.cpu_count() or 4
    # Leave 1-2 cores for system
    return max(2, cpu_count - 2)

def parallel_metadata_loading(doi, state):
    """Parallel loading of Crossref and OpenAlex metadata"""
    if not doi or doi == 'N/A':
        return {'crossref': None, 'openalex': None}
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_crossref = executor.submit(get_crossref_metadata, doi, state)
        future_openalex = executor.submit(get_openalex_metadata, doi, state)
        
        return {
            'crossref': future_crossref.result(),
            'openalex': future_openalex.result()
        }

def parallel_metrics_calculation(analyzed_metadata, citing_metadata, state, journal_issn):
    """Parallel calculation of all metrics"""
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Basic metrics
        future_basic = executor.submit(enhanced_stats_calculation, analyzed_metadata, citing_metadata, state)
        
        # Fast metrics
        future_fast = executor.submit(calculate_all_fast_metrics, analyzed_metadata, citing_metadata, state, journal_issn)
        
        # Citation timing
        future_timing = executor.submit(calculate_citation_timing, analyzed_metadata, state)
        
        # Overlap analysis
        future_overlap = executor.submit(analyze_overlaps, analyzed_metadata, citing_metadata, state)
        
        return {
            'basic': future_basic.result(),
            'fast': future_fast.result(),
            'timing': future_timing.result(),
            'overlap': future_overlap.result()
        }

def parallel_analyses(analyzed_metadata, citing_metadata, state, citation_timing_data, analyzed_stats=None, citing_stats=None):
    """Parallel execution of independent analyses - ИСПРАВЛЕНО: гарантированное выполнение всех анализов"""
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Title keywords analysis - ВСЕГДА выполняем
        future_keywords = executor.submit(parallel_title_keywords_analysis, analyzed_metadata, citing_metadata)
        
        # Citation seasonality - ВСЕГДА выполняем
        future_seasonality = executor.submit(analyze_citation_seasonality, analyzed_metadata, state, citation_timing_data)
        
        # Potential reviewers - ВСЕГДА выполняем
        future_reviewers = executor.submit(find_potential_reviewers, analyzed_metadata, citing_metadata, [], state)
        
        # Special analysis metrics (if needed)
        if state.is_special_analysis:
            future_special = executor.submit(calculate_special_analysis_metrics, analyzed_metadata, citing_metadata, state)
        else:
            future_special = None
        
        # ROR data processing (if needed)
        if state.include_ror_data:
            analyzed_affiliations = []
            citing_affiliations = []
            
            for item in analyzed_metadata:
                if item and item.get('openalex'):
                    _, affiliations, _ = extract_affiliations_and_countries(item.get('openalex'))
                    analyzed_affiliations.extend(affiliations)
            
            for item in citing_metadata:
                if item and item.get('openalex'):
                    _, affiliations, _ = extract_affiliations_and_countries(item.get('openalex'))
                    citing_affiliations.extend(affiliations)
            
            affiliations_list = list(set(analyzed_affiliations + citing_affiliations))
            future_ror = executor.submit(process_ror_data_parallel, affiliations_list, state)
        else:
            future_ror = None
        
        # Collect results - ИСПРАВЛЕНО: гарантируем получение всех результатов
        try:
            keywords_result = future_keywords.result()
        except Exception as e:
            print(f"Warning: Title keywords analysis failed: {e}")
            keywords_result = {'analyzed': {'content_words': [], 'compound_words': [], 'scientific_words': [], 'total_titles': 0}, 
                             'citing': {'content_words': [], 'compound_words': [], 'scientific_words': [], 'total_titles': 0}}
        
        try:
            seasonality_result = future_seasonality.result()
        except Exception as e:
            print(f"Warning: Citation seasonality analysis failed: {e}")
            seasonality_result = {'citation_months': {}, 'publication_months': {}, 'optimal_publication_months': [], 'total_citations_by_month': 0}
        
        try:
            reviewers_result = future_reviewers.result()
        except Exception as e:
            print(f"Warning: Potential reviewers analysis failed: {e}")
            reviewers_result = {'potential_reviewers': [], 'total_journal_authors': 0, 'total_overlap_authors': 0, 'total_potential_reviewers': 0}
        
        results = {
            'title_keywords': keywords_result,  # ИСПРАВЛЕНО: правильное имя ключа
            'citation_seasonality': seasonality_result,  # ИСПРАВЛЕНО: правильное имя ключа
            'potential_reviewers': reviewers_result  # ИСПРАВЛЕНО: правильное имя ключа
        }
        
        if future_special:
            try:
                results['special_analysis_metrics'] = future_special.result()  # ИСПРАВЛЕНО: правильное имя ключа
            except Exception as e:
                print(f"Warning: Special analysis metrics failed: {e}")
                results['special_analysis_metrics'] = {}
        else:
            results['special_analysis_metrics'] = {}  # ИСПРАВЛЕНО: добавляем пустой словарь даже если не в special mode
            
        if future_ror:
            try:
                results['ror_data'] = future_ror.result()
            except Exception as e:
                print(f"Warning: ROR data processing failed: {e}")
                results['ror_data'] = {}
        
        return results

def parallel_title_keywords_analysis(analyzed_metadata, citing_metadata):
    """Parallel analysis of title keywords"""
    analyzer = TitleKeywordsAnalyzer()
    
    analyzed_titles = extract_titles_from_metadata(analyzed_metadata)
    citing_titles = extract_titles_from_metadata(citing_metadata)
    
    return analyzer.analyze_titles(analyzed_titles, citing_titles)

def parallel_excel_preparation(data_dict):
    """Parallel preparation of Excel sheets"""
    sheets_data = {}
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Main sheets
        future_analyzed = executor.submit(prepare_analyzed_sheet_data, data_dict['analyzed'])
        future_citing = executor.submit(prepare_citing_sheet_data, data_dict['citing'])
        future_stats = executor.submit(prepare_statistics_sheet_data, data_dict['stats'])
        future_metrics = executor.submit(prepare_metrics_sheet_data, data_dict['metrics'])
        
        sheets_data['analyzed'] = future_analyzed.result()
        sheets_data['citing'] = future_citing.result()
        sheets_data['stats'] = future_stats.result()
        sheets_data['metrics'] = future_metrics.result()
    
    return sheets_data

def prepare_analyzed_sheet_data(analyzed_data):
    """Prepare data for analyzed articles sheet"""
    # Implementation details...
    return analyzed_data
    
def calculate_basic_metrics(analyzed_metadata, citing_metadata):
    """Calculate basic metrics - wrapper for enhanced_stats_calculation"""
    state = get_analysis_state()
    return enhanced_stats_calculation(analyzed_metadata, citing_metadata, state)
    
def prepare_citing_sheet_data(citing_data):
    """Prepare data for citing works sheet"""
    # Implementation details...
    return citing_data

def prepare_statistics_sheet_data(stats_data):
    """Prepare data for statistics sheet"""
    # Implementation details...
    return stats_data

def prepare_metrics_sheet_data(metrics_data):
    """Prepare data for metrics sheet"""
    # Implementation details...
    return metrics_data

def smart_batch_processing(items, batch_type="metadata"):
    """Adaptive batching based on data type and size"""
    if not items:
        return []
    
    if batch_type == "metadata":
        # Smaller batches for API-heavy operations
        batch_size = min(10, max(5, len(items) // 10))
    elif batch_type == "calculation":
        # Larger batches for CPU-heavy operations
        batch_size = min(50, max(20, len(items) // 5))
    else:
        batch_size = 20
    
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]

# =============================================================================
# LAZY EVALUATION CLASSES
# =============================================================================

class LazyMetricsCalculator:
    """Lazy evaluation for expensive metrics calculations"""
    
    def __init__(self, analyzed_metadata, citing_metadata, state, journal_issn):
        self._analyzed = analyzed_metadata
        self._citing = citing_metadata
        self._state = state
        self._journal_issn = journal_issn
        self._cache = {}
    
    def __getattr__(self, name):
        if name not in self._cache:
            if name == 'author_gini':
                self._cache[name] = calculate_author_gini_fast(self._analyzed)
            elif name == 'dbi':
                self._cache[name] = calculate_dbi_fast(self._analyzed)
            elif name == 'elite_index':
                self._cache[name] = calculate_elite_index_fast(self._analyzed)
            elif name == 'fwci':
                self._cache[name] = calculate_fwci_fast(self._analyzed)
            elif name == 'jscr':
                self._cache[name] = calculate_jscr_fast(self._citing, self._journal_issn)
            else:
                raise AttributeError(f"Unknown metric: {name}")
        return self._cache[name]
    
    def preload_common_metrics(self):
        """Preload most commonly used metrics"""
        common_metrics = ['author_gini', 'dbi', 'elite_index', 'fwci']
        for metric in common_metrics:
            getattr(self, metric)

# =============================================================================
# PROGRESSIVE LOADING FUNCTIONS
# =============================================================================

def progressive_analysis(analyzed_metadata, citing_metadata, state, journal_issn):
    """Progressive analysis - show basic metrics first, then advanced"""
    # Phase 1: Quick metrics (show immediately)
    basic_metrics = calculate_basic_metrics(analyzed_metadata, citing_metadata)
    
    # Phase 2: Start background tasks for advanced metrics
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_advanced = executor.submit(calculate_advanced_metrics, analyzed_metadata, citing_metadata, state)
        future_timing = executor.submit(calculate_citation_timing, analyzed_metadata, state)
        future_fast = executor.submit(calculate_all_fast_metrics, analyzed_metadata, citing_metadata, state, journal_issn)
    
    return {
        'basic': basic_metrics,
        'future_advanced': future_advanced,
        'future_timing': future_timing,
        'future_fast': future_fast
    }

def calculate_advanced_metrics(analyzed_metadata, citing_metadata, state):
    """Calculate advanced metrics (can be slow)"""
    # Implementation of advanced metrics calculation
    enhanced_stats = enhanced_stats_calculation(analyzed_metadata, citing_metadata, state)
    overlap_details = analyze_overlaps(analyzed_metadata, citing_metadata, state)
    
    return {
        'enhanced_stats': enhanced_stats,
        'overlap_details': overlap_details
    }

# =============================================================================
# PREDICTIVE CACHING
# =============================================================================

def predictive_cache_warmup(issn, years=None):
    """Preload data based on usage patterns"""
    if years is None:
        current_year = datetime.now().year
        years = range(current_year-2, current_year+1)
    
    warmup_tasks = []
    
    for year in years:
        # Warm up journal name cache
        warmup_tasks.append((f"journal_{issn}", cached_get_journal_name(issn)))
        
        # Warm up common ISSN normalizations
        sample_issns = [issn, issn.replace('-', '')]
        for sample_issn in sample_issns:
            warmup_tasks.append((f"issn_norm_{sample_issn}", cached_normalize_issn(sample_issn)))
    
    # Start warmup in background
    if warmup_tasks:
        threading.Thread(target=background_warmup, args=(warmup_tasks,), daemon=True).start()

def background_warmup(tasks):
    """Background task for cache warming"""
    for cache_key, value in tasks:
        # Values are already computed, this just ensures they're in cache
        pass

# =============================================================================
# OPTIMIZED VERSIONS OF EXISTING FUNCTIONS
# =============================================================================

def optimized_extract_affiliations_and_countries(openalex_data):
    """Optimized version with caching"""
    return cached_extract_authors(openalex_data)

def optimized_get_journal_name(issn):
    """Optimized journal name lookup with caching"""
    return cached_get_journal_name(issn)

def optimized_normalize_issn(issn):
    """Optimized ISSN normalization with caching"""
    return cached_normalize_issn(issn)

def process_data_in_chunks(data, chunk_size=500, process_func=None):
    """Обработка данных блоками для уменьшения потребления памяти"""
    if not data:
        return []
        
    results = []
    total_chunks = (len(data) + chunk_size - 1) // chunk_size
    
    for chunk_idx in range(total_chunks):
        start_idx = chunk_idx * chunk_size
        end_idx = min((chunk_idx + 1) * chunk_size, len(data))
        chunk = data[start_idx:end_idx]
        
        print(f"📦 Processing chunk {chunk_idx + 1}/{total_chunks} ({len(chunk)} items)")
        
        if process_func:
            chunk_results = process_func(chunk)
            results.extend(chunk_results)
        else:
            results.extend(chunk)
    
    return results

# =============================================================================
# CONFIGURATION AND SETTINGS (ORIGINAL)
# =============================================================================

class AppSettings(BaseModel):
    """Application settings with validation"""
    email: str = "your.email@example.com"
    max_workers: int = 5
    retries: int = 3
    delays: List[float] = [0.2, 0.5, 0.7, 1.0, 1.3, 1.5, 2.0]
    api_timeouts: Dict[str, int] = {
        'crossref': 15,
        'openalex': 10,
        'batch': 30
    }
    batch_sizes: Dict[str, int] = {
        'metadata': 10,
        'citations': 5
    }
    cache_ttl: int = 3600  # 1 hour
    max_cache_size: int = 1000
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v
    
    @validator('max_workers')
    def validate_max_workers(cls, v):
        if v < 1 or v > 20:
            raise ValueError('max_workers must be between 1 and 20')
        return v

class AnalysisConfig:
    """Configuration manager for the application"""
    def __init__(self):
        self.settings = AppSettings()
        self._load_environment_variables()
    
    def _load_environment_variables(self):
        """Load settings from environment variables"""
        if hasattr(st, 'secrets'):
            self.settings.email = st.secrets.get("EMAIL", self.settings.email)
    
    def get_settings(self) -> AppSettings:
        return self.settings

# =============================================================================
# DATA MODELS (ORIGINAL)
# =============================================================================

class ArticleMetadata(BaseModel):
    """Model for article metadata"""
    doi: Optional[str] = None
    title: Optional[str] = None
    authors: List[str] = []
    affiliations: List[str] = []
    countries: List[str] = []
    publication_date: Optional[datetime] = None
    journal_name: Optional[str] = None
    publisher: Optional[str] = None
    issn: List[str] = []
    reference_count: int = 0
    citation_count: int = 0
    work_type: Optional[str] = None
    concepts: List[Dict[str, Any]] = []
    open_access: bool = False
    
    class Config:
        arbitrary_types_allowed = True

class JournalMetrics(BaseModel):
    """Model for journal metrics"""
    h_index: int = 0
    total_citations: int = 0
    avg_citations_per_article: float = 0.0
    articles_with_citations: int = 0
    articles_without_citations: int = 0
    self_citation_rate: float = 0.0
    international_collaboration_rate: float = 0.0
    reference_age_median: Optional[float] = None
    jscr: float = 0.0
    cited_half_life: Optional[float] = None
    fwci: float = 0.0
    citation_velocity: float = 0.0
    oa_impact_premium: float = 0.0
    elite_index: float = 0.0
    author_gini: float = 0.0
    dbi: float = 0.0

class AnalysisResult(BaseModel):
    """Complete analysis result model"""
    journal_name: str
    issn: str
    analysis_period: str
    analyzed_articles: List[ArticleMetadata] = []
    citing_articles: List[ArticleMetadata] = []
    metrics: JournalMetrics
    timestamp: datetime = datetime.now()
    additional_data: Dict[str, Any] = {}
    
    class Config:
        arbitrary_types_allowed = True

# =============================================================================
# CACHE MANAGEMENT (ORIGINAL)
# =============================================================================

class CacheManager:
    """Unified cache management with disk persistence"""
    
    def __init__(self, cache_dir: str = "./journal_cache", ttl: int = 3600):
        self.cache = diskcache.Cache(cache_dir)
        self.ttl = ttl
        self._setup_cleanup()
    
    def _setup_cleanup(self):
        """Setup cache cleanup on application start"""
        try:
            self.cache.expire()
        except Exception:
            pass
    
    def get(self, key: str) -> Any:
        """Retrieve value from cache"""
        try:
            return self.cache.get(key)
        except Exception:
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store value in cache"""
        try:
            self.cache.set(key, value, expire=ttl or self.ttl)
            return True
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            self.cache.delete(key)
            return True
        except Exception:
            return False
    
    def clear(self) -> bool:
        """Clear entire cache"""
        try:
            self.cache.clear()
            return True
        except Exception:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            return {
                'size': len(self.cache),
                'directory': self.cache.directory,
                'ttl': self.ttl
            }
        except Exception:
            return {'size': 0, 'directory': 'unknown', 'ttl': self.ttl}

# =============================================================================
# ERROR HANDLING AND RETRY MECHANISM (ORIGINAL)
# =============================================================================

class AnalysisError(Exception):
    """Custom exception for analysis errors"""
    pass

class APIError(AnalysisError):
    """Exception for API-related errors"""
    pass

class DataValidationError(AnalysisError):
    """Exception for data validation errors"""
    pass

def retry_on_exception(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception]] = (Exception,),
    logger: Optional[logging.Logger] = None
):
    """
    Retry decorator with exponential backoff
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        if logger:
                            logger.warning(
                                f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {str(e)}. "
                                f"Retrying in {current_delay}s..."
                            )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        if logger:
                            logger.error(
                                f"All {max_retries} attempts failed for {func.__name__}: {str(e)}"
                            )
            
            raise last_exception
        return wrapper
    return decorator

def handle_analysis_errors(func):
    """
    Decorator to handle analysis errors gracefully
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            st.error(f"API Error in {func.__name__}: {str(e)}")
            return None
        except DataValidationError as e:
            st.error(f"Data Validation Error in {func.__name__}: {str(e)}")
            return None
        except AnalysisError as e:
            st.error(f"Analysis Error in {func.__name__}: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Unexpected Error in {func.__name__}: {str(e)}")
            return None
    return wrapper

# =============================================================================
# LOGGING CONFIGURATION (ORIGINAL)
# =============================================================================

class AnalysisLogger:
    """Enhanced logging for journal analysis"""
    
    def __init__(self, name: str = "journal_analysis"):
        self.logger = logging.getLogger(name)
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        if not self.logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # Stream handler for Streamlit
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)
            
            # File handler for persistence
            try:
                file_handler = logging.FileHandler('journal_analysis.log')
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            except Exception:
                pass
            
            self.logger.setLevel(logging.INFO)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)

# =============================================================================
# API CLIENTS (ORIGINAL)
# =============================================================================

class APIClientBase:
    """Base class for API clients"""
    
    def __init__(self, config: AnalysisConfig, logger: AnalysisLogger, cache: CacheManager):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.settings = config.get_settings()
    
    @retry_on_exception(max_retries=3, delay=1.0, backoff=2.0)
    def _make_request(self, url: str, headers: Optional[Dict] = None, timeout: int = 30) -> Optional[Dict]:
        """Make HTTP request with retry logic"""
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed for {url}: {str(e)}")
            raise APIError(f"Failed to fetch data from {url}: {str(e)}")

class CrossrefClient(APIClientBase):
    """Client for Crossref API"""
    
    def __init__(self, config: AnalysisConfig, logger: AnalysisLogger, cache: CacheManager):
        super().__init__(config, logger, cache)
        self.base_url = "https://api.crossref.org"
        self.headers = {'User-Agent': f"JournalAnalyzer/1.0 (mailto:{self.settings.email})"}
    
    def get_article_metadata(self, doi: str) -> Optional[Dict]:
        """Get article metadata from Crossref"""
        cache_key = f"crossref_metadata_{doi}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data
        
        url = f"{self.base_url}/works/{quote(doi)}"
        data = self._make_request(url, self.headers, self.settings.api_timeouts['crossref'])
        
        if data and 'message' in data:
            self.cache.set(cache_key, data['message'])
            return data['message']
        
        return None
    
    def get_journal_articles(self, issn: str, from_date: str, until_date: str) -> List[Dict]:
        """Get journal articles by ISSN and date range"""
        cache_key = f"crossref_journal_{issn}_{from_date}_{until_date}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data
        
        articles = []
        cursor = "*"
        params = {
            'filter': f'issn:{issn},from-pub-date:{from_date},until-pub-date:{until_date}',
            'rows': 1000,
            'cursor': cursor,
            'mailto': self.settings.email
        }
        
        while cursor:
            params['cursor'] = cursor
            url = f"{self.base_url}/works"
            
            try:
                data = self._make_request(url, self.headers, params=params)
                if data and 'message' in data:
                    new_items = data['message'].get('items', [])
                    articles.extend(new_items)
                    cursor = data['message'].get('next-cursor')
                    
                    if not new_items:
                        break
            except APIError:
                break
        
        if articles:
            self.cache.set(cache_key, articles)
        
        return articles

class OpenAlexClient(APIClientBase):
    """Client for OpenAlex API"""
    
    def __init__(self, config: AnalysisConfig, logger: AnalysisLogger, cache: CacheManager):
        super().__init__(config, logger, cache)
        self.base_url = "https://api.openalex.org"
    
    def get_article_metadata(self, doi: str) -> Optional[Dict]:
        """Get article metadata from OpenAlex"""
        cache_key = f"openalex_metadata_{doi}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data
        
        normalized_doi = doi if doi.startswith('http') else f"https://doi.org/{doi}"
        url = f"{self.base_url}/works/{quote(normalized_doi)}"
        
        data = self._make_request(url, timeout=self.settings.api_timeouts['openalex'])
        
        if data:
            self.cache.set(cache_key, data)
            return data
        
        return None
    
    def get_citing_works(self, work_id: str, per_page: int = 100) -> List[Dict]:
        """Get works that cite the given work"""
        cache_key = f"openalex_citing_{work_id}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data
        
        citing_works = []
        cursor = "*"
        url = f"{self.base_url}/works?filter=cites:{work_id}&per-page={per_page}"
        
        while cursor:
            try:
                full_url = f"{url}&cursor={cursor}"
                data = self._make_request(full_url, timeout=self.settings.api_timeouts['batch'])
                
                if data and 'results' in data:
                    citing_works.extend(data['results'])
                    cursor = data.get('meta', {}).get('next_cursor')
                    
                    if not data['results']:
                        break
                else:
                    break
            except APIError:
                break
        
        if citing_works:
            self.cache.set(cache_key, citing_works)
        
        return citing_works
    
    def get_journal_info(self, issn: str) -> Optional[Dict]:
        """Get journal information by ISSN"""
        cache_key = f"openalex_journal_{issn}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data
        
        url = f"{self.base_url}/sources?filter=issn:{issn}"
        data = self._make_request(url, timeout=self.settings.api_timeouts['openalex'])
        
        if data and data.get('meta', {}).get('count', 0) > 0:
            journal_data = data['results'][0]
            self.cache.set(cache_key, journal_data)
            return journal_data
        
        return None

# =============================================================================
# DATA PROCESSORS (ORIGINAL)
# =============================================================================

class DataProcessor:
    """Processor for data extraction and transformation"""
    
    def __init__(self, logger: AnalysisLogger):
        self.logger = logger
    
    def extract_article_metadata(self, crossref_data: Optional[Dict], openalex_data: Optional[Dict]) -> ArticleMetadata:
        """Extract unified article metadata from Crossref and OpenAlex data"""
        metadata = ArticleMetadata()
        
        # Extract from Crossref
        if crossref_data:
            metadata.doi = crossref_data.get('DOI')
            metadata.title = crossref_data.get('title', [''])[0] if crossref_data.get('title') else None
            metadata.publication_date = self._extract_publication_date(crossref_data)
            metadata.journal_name = crossref_data.get('container-title', [''])[0] if crossref_data.get('container-title') else None
            metadata.publisher = crossref_data.get('publisher')
            metadata.issn = crossref_data.get('ISSN', [])
            metadata.reference_count = crossref_data.get('reference-count', 0)
            metadata.citation_count = crossref_data.get('is-referenced-by-count', 0)
            metadata.work_type = crossref_data.get('type')
            
            # Extract authors from Crossref
            metadata.authors = self._extract_crossref_authors(crossref_data)
        
        # Extract from OpenAlex
        if openalex_data:
            # Use OpenAlex data to supplement or override
            if not metadata.title:
                metadata.title = openalex_data.get('title')
            
            if not metadata.publication_date:
                pub_date = openalex_data.get('publication_date')
                if pub_date:
                    try:
                        metadata.publication_date = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                    except ValueError:
                        pass
            
            # Extract authors, affiliations, and countries from OpenAlex
            authors, affiliations, countries = self._extract_openalex_authors_affiliations(openalex_data)
            if authors:
                metadata.authors = authors
            metadata.affiliations = affiliations
            metadata.countries = countries
            
            # Extract concepts
            metadata.concepts = openalex_data.get('concepts', [])
            
            # Extract open access info
            metadata.open_access = openalex_data.get('open_access', {}).get('is_oa', False)
            
            # Use OpenAlex citation count if higher
            oa_citations = openalex_data.get('cited_by_count', 0)
            if oa_citations > metadata.citation_count:
                metadata.citation_count = oa_citations
        
        return metadata
    
    def _extract_publication_date(self, crossref_data: Dict) -> Optional[datetime]:
        """Extract publication date from Crossref data"""
        date_parts = crossref_data.get('published', {}).get('date-parts', [[]])[0]
        if date_parts and len(date_parts) >= 1:
            try:
                year = date_parts[0]
                month = date_parts[1] if len(date_parts) > 1 else 1
                day = date_parts[2] if len(date_parts) > 2 else 1
                return datetime(year, month, day)
            except (ValueError, TypeError):
                pass
        return None
    
    def _extract_crossref_authors(self, crossref_data: Dict) -> List[str]:
        """Extract authors from Crossref data"""
        authors = []
        for author in crossref_data.get('author', []):
            family_name = author.get('family', '').strip()
            given_name = author.get('given', '').strip()
            if family_name or given_name:
                author_name = f"{given_name} {family_name}".strip()
                authors.append(author_name)
        return authors
    
    def _extract_openalex_authors_affiliations(self, openalex_data: Dict) -> Tuple[List[str], List[str], List[str]]:
        """Extract authors, affiliations and countries from OpenAlex data"""
        authors = []
        affiliations = set()
        countries = set()
        
        try:
            for authorship in openalex_data.get('authorships', []):
                author_name = authorship.get('author', {}).get('display_name', '')
                if author_name and author_name != 'Unknown':
                    authors.append(author_name)
                
                # Extract affiliations and countries
                for institution in authorship.get('institutions', []):
                    inst_name = institution.get('display_name')
                    country_code = institution.get('country_code')
                    
                    if inst_name:
                        affiliations.add(inst_name)
                    if country_code:
                        countries.add(country_code.upper())
        except (KeyError, TypeError, AttributeError) as e:
            self.logger.warning(f"Error extracting OpenAlex authorships: {str(e)}")
        
        return authors, list(affiliations), list(countries)
    
    def validate_and_clean_articles(self, items: List[Dict]) -> List[Dict]:
        """Validate and clean article data"""
        validated = []
        skipped_count = 0
        
        for item in items:
            if not item.get('DOI'):
                skipped_count += 1
                continue
            
            doi = item['DOI'].lower().strip()
            if not doi.startswith('10.'):
                skipped_count += 1
                continue
            
            # Validate publication date
            date_parts = item.get('created', {}).get('date-parts', [[]])[0]
            if not date_parts or date_parts[0] < 1900:
                skipped_count += 1
                continue
            
            item['DOI'] = doi
            validated.append(item)
        
        if skipped_count > 0:
            self.logger.warning(f"Skipped {skipped_count} invalid articles")
        
        return validated

# =============================================================================
# METRICS CALCULATORS (ORIGINAL)
# =============================================================================

class MetricsCalculator:
    """Calculator for journal metrics"""
    
    def __init__(self, logger: AnalysisLogger):
        self.logger = logger
    
    def calculate_basic_metrics(self, analyzed_articles: List[ArticleMetadata], citing_articles: List[ArticleMetadata]) -> Dict[str, Any]:
        """Calculate basic journal metrics"""
        if not analyzed_articles:
            return {}
        
        # Citation metrics
        citation_counts = [article.citation_count for article in analyzed_articles]
        citation_counts.sort(reverse=True)
        
        # H-index calculation
        h_index = 0
        for i, count in enumerate(citation_counts):
            if count >= i + 1:
                h_index = i + 1
            else:
                break
        
        # Basic statistics
        total_articles = len(analyzed_articles)
        total_citations = sum(citation_counts)
        articles_with_citations = len([c for c in citation_counts if c > 0])
        articles_without_citations = total_articles - articles_with_citations
        
        avg_citations = total_citations / total_articles if total_articles > 0 else 0
        
        return {
            'h_index': h_index,
            'total_citations': total_citations,
            'avg_citations_per_article': avg_citations,
            'articles_with_citations': articles_with_citations,
            'articles_without_citations': articles_without_citations,
            'max_citations': max(citation_counts) if citation_counts else 0,
            'min_citations': min(citation_counts) if citation_counts else 0
        }
    
    def calculate_reference_age(self, analyzed_articles: List[ArticleMetadata], crossref_client: CrossrefClient) -> Dict[str, Any]:
        """Calculate reference age metrics"""
        ref_ages = []
        current_year = datetime.now().year
        
        for article in analyzed_articles:
            if not article.publication_date:
                continue
            
            pub_year = article.publication_date.year
            
            # This would need actual reference data from Crossref
            # For now, return placeholder
            pass
        
        if not ref_ages:
            return {
                'ref_median_age': None,
                'ref_mean_age': None,
                'ref_ages_25_75': [None, None],
                'total_refs_analyzed': 0
            }
        
        return {
            'ref_median_age': float(np.median(ref_ages)),
            'ref_mean_age': float(np.mean(ref_ages)),
            'ref_ages_25_75': [float(np.percentile(ref_ages, 25)), float(np.percentile(ref_ages, 75))],
            'total_refs_analyzed': len(ref_ages)
        }
    
    def calculate_jscr(self, citing_articles: List[ArticleMetadata], journal_issn: str) -> Dict[str, Any]:
        """Calculate Journal Self-Citation Rate"""
        if not citing_articles:
            return {
                'JSCR': 0.0,
                'self_cites': 0,
                'total_cites': 0
            }
        
        self_cites = 0
        total_processed = 0
        journal_issn_clean = journal_issn.replace('-', '').upper() if journal_issn else ""
        
        for citing_article in citing_articles:
            # Check if citing article is from the same journal
            if journal_issn_clean and any(
                issn.replace('-', '').upper() == journal_issn_clean 
                for issn in citing_article.issn
            ):
                self_cites += 1
            total_processed += 1
        
        jscr = round(self_cites / total_processed * 100, 2) if total_processed > 0 else 0.0
        
        return {
            'JSCR': jscr,
            'self_cites': self_cites,
            'total_cites': total_processed
        }
    
    def calculate_international_collaboration(self, analyzed_articles: List[ArticleMetadata]) -> Dict[str, Any]:
        """Calculate international collaboration metrics"""
        if not analyzed_articles:
            return {
                'single_country_articles': 0,
                'multi_country_articles': 0,
                'no_country_articles': 0,
                'single_country_pct': 0.0,
                'multi_country_pct': 0.0,
                'no_country_pct': 0.0
            }
        
        single_country = 0
        multi_country = 0
        no_country = 0
        
        for article in analyzed_articles:
            unique_countries = set(article.countries)
            if not unique_countries:
                no_country += 1
            elif len(unique_countries) == 1:
                single_country += 1
            else:
                multi_country += 1
        
        total_articles = len(analyzed_articles)
        
        return {
            'single_country_articles': single_country,
            'multi_country_articles': multi_country,
            'no_country_articles': no_country,
            'single_country_pct': (single_country / total_articles * 100) if total_articles > 0 else 0.0,
            'multi_country_pct': (multi_country / total_articles * 100) if total_articles > 0 else 0.0,
            'no_country_pct': (no_country / total_articles * 100) if total_articles > 0 else 0.0
        }

# =============================================================================
# STATE MANAGEMENT (ORIGINAL)
# =============================================================================
  
class AnalysisState:
    """Enhanced state management for analysis"""
    
    def __init__(self):
        self.crossref_cache = {}
        self.openalex_cache = {}
        self.unified_cache = {}
        self.citing_cache = defaultdict(list)
        self.institution_cache = {}
        self.journal_cache = {}
        self.analysis_results = None
        self.current_progress = 0
        self.progress_text = ""
        self.analysis_complete = False
        self.excel_buffer = None
        self.if_data = None
        self.cs_data = None
        self.is_special_analysis = False
        self.include_ror_data = False  # NEW: Flag for ROR data inclusion
        self.ror_cache = {}  # NEW: In-memory cache for ROR data
        self.include_author_id_data = False  # NEW: Flag for Author ID data inclusion
        self.author_id_cache = {}  # NEW: In-memory cache for Author ID data
        
        # Initialize components
        self.config = AnalysisConfig()
        self.logger = AnalysisLogger()
        self.cache_manager = CacheManager()
        self.crossref_client = CrossrefClient(self.config, self.logger, self.cache_manager)
        self.openalex_client = OpenAlexClient(self.config, self.logger, self.cache_manager)
        self.data_processor = DataProcessor(self.logger)
        self.metrics_calculator = MetricsCalculator(self.logger)

# =============================================================================
# ORIGINAL CODE (PRESERVED)
# =============================================================================

# --- Page Configuration ---
st.set_page_config(
    page_title="Advanced Journal Analysis Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Global Settings ---
EMAIL = st.secrets.get("EMAIL", "your.email@example.com") if hasattr(st, 'secrets') else "your.email@example.com"
MAX_WORKERS = 5
RETRIES = 3
DELAYS = [0.2, 0.5, 0.7, 1.0, 1.3, 1.5, 2.0]

# --- State Storage Classes ---
class OriginalAnalysisState:
    def __init__(self):
        self.crossref_cache = {}
        self.openalex_cache = {}
        self.unified_cache = {}
        self.citing_cache = defaultdict(list)
        self.institution_cache = {}
        self.journal_cache = {}
        self.analysis_results = None
        self.current_progress = 0
        self.progress_text = ""
        self.analysis_complete = False
        self.excel_buffer = None
        self.if_data = None
        self.cs_data = None
        self.is_special_analysis = False  # New flag for Special Analysis mode

# --- Terms Dictionary ---
class JournalAnalysisGlossary:
    def __init__(self):
        self.terms = {
            'H-index': {
                'definition': translation_manager.get_text('h_index_tooltip'),
                'calculation': 'Articles are sorted in descending order of citations, the maximum number h is found where the h-th article has at least h citations',
                'interpretation': 'Higher = better. Shows both productivity and influence of author/journal',
                'category': 'Citations',
                'example': 'H-index 10 means that a scientist/journal has 10 articles, each of which has been cited at least 10 times'
            },
            'Reference Age': {
                'definition': 'Average age of references in journal articles (median value)',
                'calculation': 'Difference between article publication year and publication years of cited works',
                'interpretation': 'Low age = journal cites contemporary works. High age = reliance on classical works',
                'category': 'References',
                'example': 'Reference Age 8 years means that half of references in articles are younger than 8 years, half are older'
            },
            'JSCR': {
                'definition': 'Journal Self-Citation Rate - percentage of journal self-citations',
                'calculation': '(Number of citations to articles of this same journal / Total number of citations) × 100%',
                'interpretation': 'Normal: 10-20%. Above 30% may indicate isolation. Below 5% - wide citability',
                'category': 'Citations',
                'example': 'JSCR 15% means that 15% of all journal citations are to its own articles'
            },
            'Cited Half-Life': {
                'definition': 'Citation half-life - time during which an article receives half of all its citations',
                'calculation': 'Years from publication to moment when 50% of total citations are accumulated',
                'interpretation': 'Short half-life = quick return (technical sciences). Long = long-term influence (fundamental sciences)',
                'category': 'Citations',
                'example': 'Cited Half-Life 4 years means that in the first 4 years the article receives half of all its citations'
            },
            'FWCI': {
                'definition': 'Field-Weighted Citation Impact - field-weighted citation index',
                'calculation': 'Actual citations / Expected citations for this field',
                'interpretation': '1.0 = average level. >1.2 = above average. >1.5 = significantly above average',
                'category': 'Citations',
                'example': 'FWCI 1.8 means that articles are cited 80% more often than average in their field'
            },
            'Citation Velocity': {
                'definition': 'Citation velocity - average number of citations per year for first 2 years after publication',
                'calculation': 'Number of citations in first 2 years / 2',
                'interpretation': 'Higher = faster recognition by scientific community. Depends on discipline',
                'category': 'Citations',
                'example': 'Velocity 3.5 means that on average an article receives 3.5 citations per year in first two years'
            },
            'OA Impact Premium': {
                'definition': 'Open Access premium - difference in citations between OA and non-OA articles',
                'calculation': '((Average OA citations - Average non-OA citations) / Average non-OA citations) × 100%',
                'interpretation': 'Positive premium = OA articles are cited more frequently. Usually +10% to +50%',
                'category': 'Citations',
                'example': 'OA Premium 25% means that open access articles are cited 25% more frequently'
            },
            'Elite Index': {
                'definition': 'Percentage of journal articles in top-10% most cited works in their field',
                'calculation': 'Number of articles in top-10% by citations / Total number of articles × 100%',
                'interpretation': 'Higher = more high-performance articles. Excellent indicator >20%',
                'category': 'Citations',
                'example': 'Elite Index 15% means that 15% of journal articles are in 10% most cited in their field'
            },
            'Author Gini': {
                'definition': 'Gini index for authors - measure of inequality in publication distribution among authors',
                'calculation': 'Statistical indicator from 0 to 1, where 0 = complete equality, 1 = maximum inequality',
                'interpretation': 'Low (0.1-0.3) = uniform distribution. High (0.6+) = few authors dominate',
                'category': 'Authors',
                'example': 'Gini 0.4 means moderate inequality - some authors publish significantly more frequently than others'
            },
            'DBI': {
                'definition': 'Diversity Balance Index - thematic diversification index',
                'calculation': 'Normalized Shannon index by thematic concepts of articles',
                'interpretation': '0-1, where 0 = one theme, 1 = uniform distribution across many themes',
                'category': 'Themes',
                'example': 'DBI 0.7 means good diversification across several thematic directions'
            },
            'Self-Cites': {
                'definition': 'Self-citations - references to other articles of the same journal in bibliography',
                'calculation': 'Number of references with DOI prefix of this journal',
                'interpretation': 'Moderate self-citations are normal. Excessive may artificially inflate metrics',
                'category': 'References',
                'example': '15 self-citations out of 100 references = 15% self-citations'
            },
            'International Collaboration': {
                'definition': 'International collaboration - percentage of articles with authors from different countries',
                'calculation': 'Articles with authors from ≥2 countries / All articles × 100%',
                'interpretation': 'Higher = more international journal. Indicator of research globalization',
                'category': 'Authors',
                'example': '60% international articles means that in most works authors from different countries participate'
            },
            'ISSN': {
                'definition': 'International Standard Serial Number - unique identifier for serial publications',
                'calculation': '8-digit code format XXXX-XXXX, assigned to journals',
                'interpretation': 'Used for unambiguous journal identification in international databases',
                'category': 'Journal',
                'example': 'ISSN 2411-1414 identifies journal Chimica Techno Acta'
            },
            'DOI': {
                'definition': 'Digital Object Identifier - permanent link to digital object',
                'calculation': 'Unique identifier format 10.XXXX/XXXXX for scientific articles',
                'interpretation': 'Provides permanent availability and citability of scientific works',
                'category': 'Technical',
                'example': 'DOI 10.15826/chimtech.2024.11.1.01 unambiguously identifies specific article'
            },
            'Crossref': {
                'definition': 'System of mutual references between scientific publications',
                'calculation': 'Database of references between articles with metadata',
                'interpretation': 'Main source of citation data and article metadata',
                'category': 'Databases',
                'example': 'Crossref contains information about 140+ million scientific works'
            },
            'OpenAlex': {
                'definition': 'Open database of scientific publications, authors and institutions',
                'calculation': 'Alternative to Scopus/WoS with open access to data',
                'interpretation': 'Provides extended metrics and connections between scientific objects',
                'category': 'Databases',
                'example': 'OpenAlex contains data about 200+ million scientific works'
            }
        }
        
        self.category_colors = {
            'Citations': '🔵',
            'References': '🟢',
            'Authors': '🟠',
            'Themes': '🟣',
            'Journal': '🔴',
            'Technical': '⚫',
            'Databases': '🟤'
        }
    
    def get_tooltip(self, term):
        """Generate text for tooltip"""
        if term not in self.terms:
            return f"Term '{term}' not found in dictionary"
        
        info = self.terms[term]
        tooltip = f"**{term}**\n\n{info['definition']}"
        
        if 'calculation' in info:
            tooltip += f"\n\n**Calculation:** {info['calculation']}"
        if 'interpretation' in info:
            tooltip += f"\n\n**Interpretation:** {info['interpretation']}"
            
        return tooltip
    
    def get_detailed_info(self, term):
        """Complete term information for extended tooltips"""
        if term not in self.terms:
            return None
        
        info = self.terms[term]
        category_icon = self.category_colors.get(info['category'], '⚪')
        
        detailed = {
            'term': term,
            'definition': info['definition'],
            'calculation': info.get('calculation', 'Not specified'),
            'interpretation': info.get('interpretation', 'Not specified'),
            'category': f"{category_icon} {info['category']}",
            'example': info.get('example', 'Example not provided')
        }
        
        return detailed
    
    def get_terms_by_category(self, category):
        """Get all terms of category"""
        return [term for term, info in self.terms.items() if info['category'] == category]
    
    def get_random_term(self):
        """Random term for learning"""
        return random.choice(list(self.terms.keys()))

# Initialize global dictionary
glossary = JournalAnalysisGlossary()

# --- State Initialization ---
def initialize_analysis_state():
    if 'analysis_state' not in st.session_state:
        st.session_state.analysis_state = AnalysisState()
    
    # Initialize learned terms
    if 'learned_terms' not in st.session_state:
        st.session_state.learned_terms = set()
    
    # Initialize viewed terms in this session
    if 'viewed_terms' not in st.session_state:
        st.session_state.viewed_terms = set()

def get_analysis_state():
    return st.session_state.analysis_state

# --- Rate Limiter ---
class RateLimiter:
    def __init__(self, calls_per_second=5):
        self.calls_per_second = calls_per_second
        self.timestamps = []
        self.lock = threading.Lock()
    
    def wait_if_needed(self):
        with self.lock:
            now = time.time()
            self.timestamps = [ts for ts in self.timestamps if now - ts < 1.0]
            
            if len(self.timestamps) >= self.calls_per_second:
                sleep_time = 1.0 - (now - self.timestamps[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                self.timestamps = self.timestamps[1:]
            
            self.timestamps.append(now)

rate_limiter = RateLimiter(calls_per_second=8)

# --- Adaptive Delay ---
class AdaptiveDelayer:
    def __init__(self):
        self.lock = threading.Lock()
        self.delay_index = 0

    def wait(self, success=True):
        with self.lock:
            if success:
                self.delay_index = 0
            else:
                self.delay_index = min(self.delay_index + 1, len(DELAYS) - 1)
            delay = DELAYS[self.delay_index]
            time.sleep(delay)
            return delay

delayer = AdaptiveDelayer()

# --- Configuration ---
class JournalAnalyzerConfig:
    def __init__(self):
        self.email = EMAIL
        self.max_workers = MAX_WORKERS
        self.retries = RETRIES
        self.delays = DELAYS
        self.timeouts = {
            'crossref': 15,
            'openalex': 10,
            'batch': 30
        }
        self.batch_sizes = {
            'metadata': 10,
            'citations': 5
        }

config = JournalAnalyzerConfig()

# --- Helper Functions ---
def update_progress(progress, text):
    state = get_analysis_state()
    state.current_progress = progress
    state.progress_text = text

# --- Period Validation and Parsing ---
def parse_period(period_str):
    years = set()
    parts = [p.strip() for p in period_str.replace(' ', '').split(',') if p.strip()]
    for part in parts:
        if '-' in part:
            try:
                s, e = map(int, part.split('-'))
                if 1900 <= s <= 2100 and 1900 <= e <= 2100 and s <= e:
                    years.update(range(s, e + 1))
                else:
                    st.warning(translation_manager.get_text('range_out_of_bounds').format(part=part))
            except ValueError:
                st.warning(translation_manager.get_text('range_parsing_error').format(part=part))
        else:
            try:
                y = int(part)
                if 1900 <= y <= 2100:
                    years.add(y)
                else:
                    st.warning(translation_manager.get_text('year_out_of_bounds').format(year=y))
            except ValueError:
                st.warning(translation_manager.get_text('not_a_year').format(part=part))
    if not years:
        st.error(translation_manager.get_text('no_correct_years'))
        return []
    return sorted(years)

# --- Data Validation ---
def validate_and_clean_data(items):
    validated = []
    skipped_count = 0
    
    for item in items:
        if not item.get('DOI'):
            skipped_count += 1
            continue
            
        doi = item['DOI'].lower().strip()
        if not doi.startswith('10.'):
            skipped_count += 1
            continue
            
        date_parts = item.get('created', {}).get('date-parts', [[]])[0]
        if not date_parts or date_parts[0] < 1900:
            skipped_count += 1
            continue
            
        item['DOI'] = doi
        validated.append(item)
    
    if skipped_count > 0:
        st.warning(translation_manager.get_text('articles_skipped').format(count=skipped_count))
    return validated

# === 1. Journal Name ===
def get_journal_name(issn):
    state = get_analysis_state()
    if issn in state.crossref_cache.get('journals', {}):
        return state.crossref_cache['journals'][issn]
    url = f"https://api.openalex.org/sources?filter=issn:{issn}"
    for _ in range(RETRIES):
        try:
            rate_limiter.wait_if_needed()
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data['meta']['count'] > 0:
                    name = data['results'][0]['display_name']
                    if 'journals' not in state.crossref_cache:
                        state.crossref_cache['journals'] = {}
                    state.crossref_cache['journals'][issn] = name
                    delayer.wait(success=True)
                    return name
        except:
            pass
        delayer.wait(success=False)
    return translation_manager.get_text('journal_not_found')

# === 2. Crossref Metadata Retrieval ===
def get_crossref_metadata(doi, state):
    if doi in state.crossref_cache:
        return state.crossref_cache[doi]
    if not doi or doi == 'N/A':
        return None
    url = f"https://api.crossref.org/works/{quote(doi)}"
    headers = {'User-Agent': f"YourApp/1.0 (mailto:{EMAIL})"}
    for _ in range(RETRIES):
        try:
            rate_limiter.wait_if_needed()
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()['message']
                state.crossref_cache[doi] = data
                delayer.wait(success=True)
                return data
        except:
            pass
        delayer.wait(success=False)
    return None

# === 3. OpenAlex Metadata Retrieval ===
def get_openalex_metadata(doi, state):
    if doi in state.openalex_cache:
        return state.openalex_cache[doi]
    if not doi or doi == 'N/A':
        return None
    normalized = doi if doi.startswith('http') else f"https://doi.org/{doi}"
    url = f"https://api.openalex.org/works/{quote(normalized)}"
    for _ in range(RETRIES):
        try:
            rate_limiter.wait_if_needed()
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                state.openalex_cache[doi] = data
                delayer.wait(success=True)
                return data
        except:
            pass
        delayer.wait(success=False)
    return None

# === 4. Unified Metadata ===
def get_unified_metadata(args):
    doi, state = args
    if doi in state.unified_cache:
        return state.unified_cache[doi]
    
    if not doi or doi == 'N/A':
        return {'crossref': None, 'openalex': None}
    
    cr_data = get_crossref_metadata(doi, state)
    oa_data = get_openalex_metadata(doi, state)
    
    result = {'crossref': cr_data, 'openalex': oa_data}
    state.unified_cache[doi] = result
    return result

# === 5. Citing DOI Retrieval and Their Metadata ===
def get_citing_dois_and_metadata(args):
    analyzed_doi, state = args
    if analyzed_doi in state.citing_cache:
        return state.citing_cache[analyzed_doi]
    citing_list = []
    oa_data = get_openalex_metadata(analyzed_doi, state)
    if not oa_data or oa_data.get('cited_by_count', 0) == 0:
        state.citing_cache[analyzed_doi] = citing_list
        return citing_list
    work_id = oa_data['id'].split('/')[-1]
    url = f"https://api.openalex.org/works?filter=cites:{work_id}&per-page=100"
    cursor = "*"
    
    while cursor:
        success = False
        for _ in range(RETRIES):
            try:
                rate_limiter.wait_if_needed()
                resp = requests.get(f"{url}&cursor={cursor}", timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    for w in data.get('results', []):
                        c_doi = w.get('doi')
                        if c_doi:
                            if c_doi not in state.crossref_cache:
                                get_crossref_metadata(c_doi, state)
                            if c_doi not in state.openalex_cache:
                                get_openalex_metadata(c_doi, state)
                            citing_list.append({
                                'doi': c_doi,
                                'pub_date': w.get('publication_date'),
                                'crossref': state.crossref_cache.get(c_doi),
                                'openalex': state.openalex_cache.get(c_doi)
                            })
                    cursor = data['meta'].get('next_cursor')
                    delayer.wait(success=True)
                    success = True
                    break
            except:
                pass
            delayer.wait(success=False)
        if not success:
            break
    state.citing_cache[analyzed_doi] = citing_list
    return citing_list

# === 6. Affiliation and Country Extraction ===
def extract_affiliations_and_countries(openalex_data):
    affiliations = set()
    countries = set()
    authors_list = []
    
    if not openalex_data:
        return authors_list, list(affiliations), list(countries)
    
    # Check for 'authorships' key
    if 'authorships' not in openalex_data:
        return authors_list, list(affiliations), list(countries)
    
    try:
        for auth in openalex_data['authorships']:
            author_name = auth.get('author', {}).get('display_name', 'Unknown')
            authors_list.append(author_name)
            
            # Check for 'institutions' key
            if 'institutions' in auth:
                for inst in auth.get('institutions', []):
                    inst_name = inst.get('display_name')
                    country_code = inst.get('country_code')
                    
                    if inst_name:
                        affiliations.add(inst_name)
                    if country_code:
                        countries.add(country_code.upper())
    except (KeyError, TypeError, AttributeError) as e:
        # Log error but continue execution
        print(f"Warning in extract_affiliations_and_countries: {e}")
        pass
    
    return authors_list, list(affiliations), list(countries)

# === 7. Journal Information Extraction ===
def extract_journal_info(metadata):
    journal_info = {
        'issn': [],
        'journal_name': '',
        'publisher': ''
    }
    
    if not metadata:
        return journal_info
    
    cr = metadata.get('crossref')
    if cr:
        journal_info['issn'] = cr.get('ISSN', [])
        journal_info['journal_name'] = cr.get('container-title', [''])[0] if cr.get('container-title') else ''
        journal_info['publisher'] = cr.get('publisher', '')
    
    oa = metadata.get('openalex')
    if oa:
        host_venue = oa.get('host_venue', {})
        if host_venue:
            if not journal_info['journal_name']:
                journal_info['journal_name'] = host_venue.get('display_name', '')
            if not journal_info['publisher']:
                journal_info['publisher'] = host_venue.get('publisher', '')
            if not journal_info['issn']:
                journal_info['issn'] = host_venue.get('issn', [])
    
    return journal_info

# === 8. Article Retrieval from Crossref ===
def fetch_articles_by_issn_period(issn, from_date, until_date):
    base_url = "https://api.crossref.org/works"
    items = []
    cursor = "*"
    params = {
        'filter': f'issn:{issn},from-pub-date:{from_date},until-pub-date:{until_date}',
        'rows': 1000,
        'cursor': cursor,
        'mailto': EMAIL
    }
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    progress_container = st.container()
    
    with progress_container:
        st.info("📥 " + translation_manager.get_text('loading_articles') + " **Crossref** " + translation_manager.get_text('and') + " **OpenAlex**. " + translation_manager.get_text('analysis_may_take_time') + " " + translation_manager.get_text('reduce_period_recommended'))
    
    while cursor:
        params['cursor'] = cursor
        success = False
        for _ in range(RETRIES):
            try:
                rate_limiter.wait_if_needed()
                resp = requests.get(base_url, params=params, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    new_items = data['message']['items']
                    items.extend(new_items)
                    cursor = data['message'].get('next-cursor')
                    
                    status_text.text(f"📥 {translation_manager.get_text('loaded_articles').format(count=len(items))}")
                    if cursor:
                        progress = min(len(items) / (len(items) + 100), 0.95)
                        progress_bar.progress(progress)
                    
                    delayer.wait(success=True)
                    success = True
                    break
            except Exception as e:
                st.error(translation_manager.get_text('loading_error').format(error=e))
            delayer.wait(success=False)
        if not success:
            break
        if not new_items:
            break
    
    progress_bar.progress(1.0)
    status_text.text(f"✅ {translation_manager.get_text('articles_loaded').format(count=len(items))}")
    time.sleep(0.5)
    progress_bar.empty()
    status_text.empty()
    progress_container.empty()
    
    return items

# === 9. DOI Prefix Extraction ===
def normalize_doi(doi):
    """Нормализует DOI в единый формат (без https://doi.org/)"""
    if not doi or doi == 'N/A':
        return ""
    
    # Приводим к строке и очищаем
    doi_str = str(doi).strip().lower()
    
    # Удаляем различные префиксы
    prefixes = [
        'https://doi.org/',
        'http://doi.org/',
        'doi.org/',
        'doi:'
    ]
    
    for prefix in prefixes:
        if doi_str.startswith(prefix):
            doi_str = doi_str[len(prefix):]
            break
    
    return doi_str

def get_doi_prefix(doi):
    """Извлекает префикс DOI после нормализации"""
    normalized_doi = normalize_doi(doi)
    if not normalized_doi:
        return ''
    
    # Извлекаем часть до первого /
    if '/' in normalized_doi:
        return normalized_doi.split('/')[0]
    return normalized_doi

# === 10. Processing with Progress Bar ===
def process_with_progress(items, func, desc="Processing", unit="items"):
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(func, item): item for item in items}
        
        for i, future in enumerate(as_completed(futures)):
            try:
                results.append(future.result())
            except Exception as e:
                st.error(f"Error in {desc}: {e}")
                results.append(None)
            
            progress = (i + 1) / len(items)
            progress_bar.progress(progress)
            status_text.text(f"{desc}: {i + 1}/{len(items)}")
    
    progress_bar.empty()
    status_text.empty()
    return results

# === 11. Analysis of Overlaps Between Analyzed and Citing Works ===
def analyze_overlaps(analyzed_metadata, citing_metadata, state):
    """Analysis of overlaps between analyzed and citing works"""
    
    overlap_details = []
    
    for analyzed in analyzed_metadata:
        if not analyzed or not analyzed.get('crossref'):
            continue
            
        analyzed_doi = analyzed['crossref'].get('DOI')
        if not analyzed_doi:
            continue
            
        # Get authors and affiliations of analyzed work
        analyzed_authors, analyzed_affiliations, _ = extract_affiliations_and_countries(analyzed.get('openalex'))
        analyzed_authors_set = set(analyzed_authors)
        analyzed_affiliations_set = set(analyzed_affiliations)
        
        # Get citing works
        citings = get_citing_dois_and_metadata((analyzed_doi, state))
        
        for citing in citings:
            if not citing or not citing.get('openalex'):
                continue
                
            citing_doi = citing.get('doi')
            if not citing_doi:
                continue
            
            # Get authors and affiliations of citing work
            citing_authors, citing_affiliations, _ = extract_affiliations_and_countries(citing.get('openalex'))
            citing_authors_set = set(citing_authors)
            citing_affiliations_set = set(citing_affiliations)
            
            # Find overlaps
            common_authors = analyzed_authors_set.intersection(citing_authors_set)
            common_affiliations = analyzed_affiliations_set.intersection(citing_affiliations_set)
            
            if common_authors or common_affiliations:
                overlap_details.append({
                    'analyzed_doi': analyzed_doi,
                    'citing_doi': citing_doi,
                    'common_authors': list(common_authors),
                    'common_affiliations': list(common_affiliations),
                    'common_authors_count': len(common_authors),
                    'common_affiliations_count': len(common_affiliations)
                })
    
    return overlap_details

# === 12. Citation Accumulation Speed Analysis ===
def analyze_citation_accumulation(analyzed_metadata, state):
    accumulation_data = defaultdict(lambda: defaultdict(int))
    yearly_citations = defaultdict(int)
    
    for analyzed in analyzed_metadata:
        if analyzed and analyzed.get('crossref'):
            analyzed_doi = analyzed['crossref'].get('DOI')
            if not analyzed_doi:
                continue
                
            pub_year = analyzed['crossref'].get('published', {}).get('date-parts', [[0]])[0][0]
            if not pub_year:
                continue
            
            citings = get_citing_dois_and_metadata((analyzed_doi, state))
            
            for citing in citings:
                if citing.get('openalex'):
                    cite_year = citing['openalex'].get('publication_year', 0)
                    if cite_year >= pub_year:
                        yearly_citations[cite_year] += 1
                        years_since_pub = cite_year - pub_year
                        if years_since_pub >= 0:
                            for year in range(years_since_pub + 1):
                                accumulation_data[pub_year][year] += 1
    
    accumulation_curves = {}
    for pub_year, yearly_counts in accumulation_data.items():
        sorted_years = sorted(yearly_counts.keys())
        cumulative_counts = []
        current_total = 0
        for year in sorted_years:
            current_total += yearly_counts[year]
            cumulative_counts.append({
                'years_since_publication': year,
                'cumulative_citations': current_total
            })
        accumulation_curves[pub_year] = cumulative_counts
    
    yearly_stats = []
    for year in sorted(yearly_citations.keys()):
        yearly_stats.append({
            'year': year,
            'citations_count': yearly_citations[year]
        })
    
    return {
        'accumulation_curves': dict(accumulation_curves),
        'yearly_citations': yearly_stats,
        'total_years_covered': len(yearly_citations)
    }

# === 13. Metadata Processing for Statistics ===
def extract_stats_from_metadata(metadata_list, is_analyzed=True, journal_prefix=''):
    total_refs = 0
    refs_with_doi = 0
    refs_without_doi = 0
    self_cites = 0
    ref_counts = []
    author_counts = []
    single_authors = 0
    multi_authors_gt10 = 0
    author_freq = Counter()
    pub_dates = []
    
    articles_with_10_citations = 0
    articles_with_20_citations = 0
    articles_with_30_citations = 0
    articles_with_50_citations = 0

    affiliations_freq = Counter()
    countries_freq = Counter()
    single_country_articles = 0
    multi_country_articles = 0
    no_country_articles = 0
    all_authors = []
    all_affiliations = []
    all_countries = []
    
    journal_freq = Counter()
    publisher_freq = Counter()

    for meta in metadata_list:
        if not meta:
            continue

        cr = meta.get('crossref')
        if cr:
            refs = cr.get('reference', [])
            total_refs += len(refs)
            for ref in refs:
                ref_doi = ref.get('DOI', '')
                if ref_doi:
                    refs_with_doi += 1
                    if get_doi_prefix(ref_doi) == journal_prefix:
                        self_cites += 1
                else:
                    refs_without_doi += 1
            ref_counts.append(len(refs))

            authors = cr.get('author', [])
            num_auth = len(authors)
            author_counts.append(num_auth)
            if num_auth == 1:
                single_authors += 1
            if num_auth > 10:
                multi_authors_gt10 += 1

            for auth in authors:
                family = auth.get('family', '').strip().title()
                given = auth.get('given', '').strip()
                initials = '.'.join([c + '.' for c in given if c.isupper()]) if given else ''
                if initials:
                    name = f"{family} {initials}"
                else:
                    name = family or 'Unknown'
                author_freq[name] += 1

            date_parts = cr.get('published', {}).get('date-parts', [[datetime.now().year]])[0]
            pub_date = datetime(date_parts[0], date_parts[1] if len(date_parts)>1 else 1, date_parts[2] if len(date_parts)>2 else 1)
            pub_dates.append(pub_date)
            
            journal_name = cr.get('container-title', [''])[0] if cr.get('container-title') else ''
            publisher = cr.get('publisher', '')
            if journal_name:
                journal_freq[journal_name] += 1
            if publisher:
                publisher_freq[publisher] += 1

        oa = meta.get('openalex')
        if oa:
            try:
                authors_list, affiliations_list, countries_list = extract_affiliations_and_countries(oa)
                
                all_authors.extend(authors_list)
                all_affiliations.extend(affiliations_list)
                all_countries.extend(countries_list)
                
                for aff in affiliations_list:
                    affiliations_freq[aff] += 1
                for country in countries_list:
                    countries_freq[country] += 1
                
                unique_countries = set(countries_list)
                if len(unique_countries) == 0:
                    no_country_articles += 1
                elif len(unique_countries) == 1:
                    single_country_articles += 1
                elif len(unique_countries) > 1:
                    multi_country_articles += 1
                
                host_venue = oa.get('host_venue', {})
                if host_venue:
                    journal_name = host_venue.get('display_name', '')
                    publisher = host_venue.get('publisher', '')
                    if journal_name and journal_name not in journal_freq:
                        journal_freq[journal_name] += 1
                    if publisher and publisher not in publisher_freq:
                        publisher_freq[publisher] += 1
                
                if is_analyzed:
                    citation_count = oa.get('cited_by_count', 0)
                    if citation_count >= 10:
                        articles_with_10_citations += 1
                    if citation_count >= 20:
                        articles_with_20_citations += 1
                    if citation_count >= 30:
                        articles_with_30_citations += 1
                    if citation_count >= 50:
                        articles_with_50_citations += 1
            except Exception as e:
                # Skip problematic records and continue processing
                print(f"Warning processing OpenAlex data: {e}")
                continue

    n_items = len(metadata_list)

    refs_with_doi_pct = (refs_with_doi / total_refs * 100) if total_refs > 0 else 0
    refs_without_doi_pct = (refs_without_doi / total_refs * 100) if total_refs > 0 else 0
    self_cites_pct = (self_cites / total_refs * 100) if total_refs > 0 else 0

    ref_min = min(ref_counts) if ref_counts else 0
    ref_max = max(ref_counts) if ref_counts else 0
    ref_mean = sum(ref_counts)/n_items if n_items > 0 else 0
    ref_median = sorted(ref_counts)[n_items//2] if n_items > 0 else 0

    auth_min = min(author_counts) if author_counts else 0
    auth_max = max(author_counts) if author_counts else 0
    auth_mean = sum(author_counts)/n_items if n_items > 0 else 0
    auth_median = sorted(author_counts)[n_items//2] if n_items > 0 else 0

    all_authors_sorted = author_freq.most_common()

    all_affiliations_sorted = affiliations_freq.most_common()
    all_countries_sorted = countries_freq.most_common()
    
    single_country_pct = (single_country_articles / n_items * 100) if n_items > 0 else 0
    multi_country_pct = (multi_country_articles / n_items * 100) if n_items > 0 else 0
    no_country_pct = (no_country_articles / n_items * 100) if n_items > 0 else 0

    all_journals_sorted = journal_freq.most_common()
    all_publishers_sorted = publisher_freq.most_common()

    return {
        'n_items': n_items,
        'total_refs': total_refs,
        'refs_with_doi': refs_with_doi, 'refs_with_doi_pct': refs_with_doi_pct,
        'refs_without_doi': refs_without_doi, 'refs_without_doi_pct': refs_without_doi_pct,
        'self_cites': self_cites, 'self_cites_pct': self_cites_pct,
        'ref_min': ref_min, 'ref_max': ref_max, 'ref_mean': ref_mean, 'ref_median': ref_median,
        'auth_min': auth_min, 'auth_max': auth_max, 'auth_mean': auth_mean, 'auth_median': auth_median,
        'single_authors': single_authors,
        'multi_authors_gt10': multi_authors_gt10,
        'all_authors': all_authors_sorted,
        'pub_dates': pub_dates,
        'articles_with_10_citations': articles_with_10_citations,
        'articles_with_20_citations': articles_with_20_citations,
        'articles_with_30_citations': articles_with_30_citations,
        'articles_with_50_citations': articles_with_50_citations,
        'all_affiliations': all_affiliations_sorted,
        'all_countries': all_countries_sorted,
        'all_authors_list': all_authors,
        'all_affiliations_list': all_affiliations,
        'all_countries_list': all_countries,
        'single_country_articles': single_country_articles, 
        'single_country_pct': single_country_pct,
        'multi_country_articles': multi_country_articles, 
        'multi_country_pct': multi_country_pct,
        'no_country_articles': no_country_articles,
        'no_country_pct': no_country_pct,
        'total_affiliations_count': len(all_affiliations),
        'unique_affiliations_count': len(set(all_affiliations)),
        'unique_countries_count': len(set(all_countries)),
        'all_journals': all_journals_sorted,
        'all_publishers': all_publishers_sorted,
        'unique_journals_count': len(journal_freq),
        'unique_publishers_count': len(publisher_freq)
    }

# === 14. Enhanced Statistics Calculation ===
def enhanced_stats_calculation(analyzed_metadata, citing_metadata, state):
    citation_network = defaultdict(list)
    citation_counts = []
    
    for analyzed in analyzed_metadata:
        if analyzed and analyzed.get('crossref'):
            analyzed_doi = analyzed['crossref'].get('DOI')
            if analyzed_doi:
                analyzed_year = analyzed['crossref'].get('published', {}).get('date-parts', [[0]])[0][0]
                citings = get_citing_dois_and_metadata((analyzed_doi, state))
                citation_counts.append(len(citings))
                
                for citing in citings:
                    if citing.get('openalex'):
                        citing_year = citing['openalex'].get('publication_year', 0)
                        citation_network[analyzed_year].append(citing_year)
    
    citation_counts.sort(reverse=True)
    h_index = 0
    for i, count in enumerate(citation_counts):
        if count >= i + 1:
            h_index = i + 1
        else:
            break
    
    return {
        'h_index': h_index,
        'citation_network': dict(citation_network),
        'avg_citations_per_article': sum(citation_counts) / len(citation_counts) if citation_counts else 0,
        'max_citations': max(citation_counts) if citation_counts else 0,
        'min_citations': min(citation_counts) if citation_counts else 0,
        'total_citations': sum(citation_counts),
        'articles_with_citations': len([c for c in citation_counts if c > 0]),
        'articles_without_citations': len([c for c in citation_counts if c == 0])
    }

# === 15. Time to First Citation Calculation ===
def calculate_citation_timing_stats(analyzed_metadata, state):
    """Calculate time to first citation statistics with proper DOI prefix comparison"""
    
    def normalize_doi(doi):
        """Normalize DOI to consistent format (without https://doi.org/)"""
        if not doi or doi == 'N/A':
            return ""
        
        # Convert to string and clean
        doi_str = str(doi).strip().lower()
        
        # Remove various DOI prefixes
        prefixes = [
            'https://doi.org/',
            'http://doi.org/',
            'doi.org/',
            'doi:'
        ]
        
        for prefix in prefixes:
            if doi_str.startswith(prefix):
                doi_str = doi_str[len(prefix):]
                break
        
        return doi_str
    
    def get_doi_prefix_from_normalized(doi):
        """Extract DOI prefix from normalized DOI"""
        if not doi:
            return ''
        
        # Extract part before first /
        if '/' in doi:
            return doi.split('/')[0]
        return doi
    
    all_days_to_first_citation = []
    citation_timing_stats = {}
    first_citation_details = []
    
    for analyzed in analyzed_metadata:
        if analyzed and analyzed.get('crossref'):
            analyzed_doi = analyzed['crossref'].get('DOI')
            if not analyzed_doi:
                continue
                
            analyzed_date_parts = analyzed['crossref'].get('published', {}).get('date-parts', [[]])[0]
            if not analyzed_date_parts or len(analyzed_date_parts) < 1:
                continue
                
            analyzed_year = analyzed_date_parts[0]
            analyzed_month = analyzed_date_parts[1] if len(analyzed_date_parts) > 1 else 1
            analyzed_day = analyzed_date_parts[2] if len(analyzed_date_parts) > 2 else 1
            
            try:
                analyzed_date = datetime(analyzed_year, analyzed_month, analyzed_day)
            except:
                continue
            
            citings = get_citing_dois_and_metadata((analyzed_doi, state))
            citation_dates = []
            
            for citing in citings:
                if citing.get('pub_date'):
                    try:
                        cite_date = datetime.fromisoformat(citing['pub_date'].replace('Z', '+00:00'))
                        citation_dates.append((cite_date, citing.get('doi')))
                    except:
                        continue
            
            if citation_dates:
                first_citation_date, first_citing_doi = min(citation_dates, key=lambda x: x[0])
                days_to_first_citation = (first_citation_date - analyzed_date).days
                
                # === FIXED DOI PREFIX COMPARISON ===
                # Normalize DOIs before comparison
                analyzed_doi_normalized = normalize_doi(analyzed_doi)
                citing_doi_normalized = normalize_doi(first_citing_doi)
                
                # Extract prefixes from normalized DOIs
                analyzed_prefix = get_doi_prefix_from_normalized(analyzed_doi_normalized)
                citing_prefix = get_doi_prefix_from_normalized(citing_doi_normalized)
                
                # Check if prefixes match (excluding empty prefixes)
                same_prefix = (analyzed_prefix == citing_prefix and analyzed_prefix != '')
                same_date = (analyzed_date.date() == first_citation_date.date())
                is_editorial_note = same_prefix and same_date
                
                if days_to_first_citation >= 0:
                    # Always save all details for Excel reporting
                    first_citation_details.append({
                        'analyzed_doi': analyzed_doi,
                        'analyzed_doi_normalized': analyzed_doi_normalized,
                        'citing_doi': first_citing_doi,
                        'citing_doi_normalized': citing_doi_normalized,
                        'analyzed_date': analyzed_date,
                        'first_citation_date': first_citation_date,
                        'days_to_first_citation': days_to_first_citation,
                        'same_prefix': same_prefix,
                        'same_date': same_date,
                        'is_editorial_note': is_editorial_note,
                        'analyzed_prefix': analyzed_prefix,
                        'citing_prefix': citing_prefix
                    })
                    
                    # Exclude editorial notes from statistical calculations
                    if not is_editorial_note:
                        all_days_to_first_citation.append(days_to_first_citation)
                    else:
                        print(f"⚠️ Editorial note excluded: {analyzed_doi} -> {first_citing_doi} (same prefix: {analyzed_prefix}, same date: {same_date})")
    
    if all_days_to_first_citation:
        citation_timing_stats = {
            # Statistics WITHOUT editorial notes (for Citing_Stats)
            'min_days_to_first_citation': min(all_days_to_first_citation),
            'max_days_to_first_citation': max(all_days_to_first_citation),
            'mean_days_to_first_citation': np.mean(all_days_to_first_citation),
            'median_days_to_first_citation': np.median(all_days_to_first_citation),
            'articles_with_citation_timing_data': len(all_days_to_first_citation),
            
            # All details (for Excel)
            'first_citation_details': first_citation_details,
            
            # Statistics for ALL data (including editorial notes)
            'all_data_stats': {
                'total_citations_analyzed': len(first_citation_details),
                'editorial_notes_count': len([d for d in first_citation_details if d.get('is_editorial_note', False)]),
                'non_editorial_citations': len(all_days_to_first_citation),
                'articles_with_any_citation': len(set(detail['analyzed_doi'] for detail in first_citation_details))
            }
        }
    else:
        citation_timing_stats = {
            'min_days_to_first_citation': 0,
            'max_days_to_first_citation': 0,
            'mean_days_to_first_citation': 0,
            'median_days_to_first_citation': 0,
            'articles_with_citation_timing_data': 0,
            'first_citation_details': [],
            'all_data_stats': {
                'total_citations_analyzed': 0,
                'editorial_notes_count': 0,
                'non_editorial_citations': 0,
                'articles_with_any_citation': 0
            }
        }
    
    return citation_timing_stats

# === 16. Citation Timing Calculation ===
def calculate_citation_timing(analyzed_metadata, state):
    timing_stats = calculate_citation_timing_stats(analyzed_metadata, state)
    accumulation_stats = analyze_citation_accumulation(analyzed_metadata, state)
    
    return {
        'days_min': timing_stats['min_days_to_first_citation'],
        'days_max': timing_stats['max_days_to_first_citation'],
        'days_mean': timing_stats['mean_days_to_first_citation'],
        'days_median': timing_stats['median_days_to_first_citation'],
        'articles_with_timing_data': timing_stats['articles_with_citation_timing_data'],
        'first_citation_details': timing_stats['first_citation_details'],
        'accumulation_curves': accumulation_stats['accumulation_curves'],
        'yearly_citations': accumulation_stats['yearly_citations'],
        'total_years_covered': accumulation_stats['total_years_covered']
    }

# === NEW FUNCTIONS: FAST METRICS WITHOUT API REQUESTS ===

def calculate_reference_age_fast(analyzed_metadata, state):
    """Reference age calculation without additional API requests"""
    ref_ages = []
    current_year = datetime.now().year
    
    for meta in analyzed_metadata:
        cr = meta.get('crossref')
        if not cr: 
            continue
        
        pub_year = cr.get('published', {}).get('date-parts', [[0]])[0][0]
        if not pub_year: 
            continue
        
        for ref in cr.get('reference', []):
            # 1. Try year from unstructured
            if 'year' in ref:
                try:
                    ref_year = int(ref['year'])
                    if 1900 <= ref_year <= current_year + 1:
                        ref_ages.append(current_year - ref_year)
                        continue
                except: 
                    pass
            
            # 2. Try DOI from cache (already loaded!)
            doi = ref.get('DOI')
            if doi and doi in state.crossref_cache:
                cached = state.crossref_cache[doi]
                date_parts = cached.get('published', {}).get('date-parts', [[0]])[0]
                if date_parts and date_parts[0]:
                    ref_year = date_parts[0]
                    ref_ages.append(current_year - ref_year)
    
    if not ref_ages: 
        return {
            'ref_median_age': None,
            'ref_mean_age': None,
            'ref_ages_25_75': [None, None],
            'total_refs_analyzed': 0
        }
    
    return {
        'ref_median_age': int(np.median(ref_ages)),
        'ref_mean_age': round(np.mean(ref_ages), 1),
        'ref_ages_25_75': [int(np.percentile(ref_ages, 25)), int(np.percentile(ref_ages, 75))],
        'total_refs_analyzed': len(ref_ages)
    }

def calculate_jscr_fast(citing_metadata, journal_issn):
    """Journal Self-Citation Rate - percentage of journal self-citations"""
    if not citing_metadata:
        return {
            'JSCR': 0,
            'self_cites': 0,
            'total_cites': 0,
            'debug': 'No citing metadata'
        }
    
    self_cites = 0
    total_processed = 0
    debug_info = []
    
    # Normalize ISSN for comparison
    journal_issn_clean = journal_issn.replace('-', '').upper() if journal_issn else ""
    
    for i, c in enumerate(citing_metadata):
        current_debug = f"Item {i}: "
        
        # Skip records without data
        if not c:
            current_debug += "No data"
            debug_info.append(current_debug)
            continue
            
        oa = c.get('openalex')
        cr = c.get('crossref')
        
        found_match = False
        found_issns = []
        
        # Check OpenAlex data
        if oa:
            host_venue = oa.get('host_venue', {})
            if host_venue:
                oa_issns = host_venue.get('issn', [])
                if isinstance(oa_issns, str):
                    oa_issns = [oa_issns]
                
                for issn in oa_issns:
                    if issn:
                        issn_clean = issn.replace('-', '').upper()
                        found_issns.append(issn_clean)
                        if issn_clean == journal_issn_clean:
                            found_match = True
                            break
        
        # Check Crossref data if not found in OpenAlex
        if not found_match and cr:
            cr_issns = cr.get('ISSN', [])
            if isinstance(cr_issns, str):
                cr_issns = [cr_issns]
                
            for issn in cr_issns:
                if issn:
                    issn_clean = issn.replace('-', '').upper()
                    found_issns.append(issn_clean)
                    if issn_clean == journal_issn_clean:
                        found_match = True
                        break
        
        # Also check by journal name in crossref (additional method)
        if not found_match and cr:
            container_title = cr.get('container-title', [])
            if container_title and journal_issn:
                # If we have journal name, we can try to match
                # but this is less reliable, so use as fallback
                pass
        
        if found_match:
            self_cites += 1
            current_debug += f"SELF-CITE found. ISSNs: {found_issns}"
        else:
            current_debug += f"Not self-cite. ISSNs: {found_issns}"
        
        debug_info.append(current_debug)
        total_processed += 1
    
    # JSCR calculation
    jscr = round(self_cites / total_processed * 100, 2) if total_processed > 0 else 0
    
    result = {
        'JSCR': jscr,
        'self_cites': self_cites,
        'total_cites': total_processed,
        'debug_count': len(debug_info),
        'journal_issn_clean': journal_issn_clean
    }
    
    # Add first part of debug information (first 10 records)
    result['debug_samples'] = debug_info[:10]
    
    return result

def calculate_cited_half_life_fast(analyzed_metadata, state):
    """Cited Half-Life - median time to receive half of citations"""
    half_lives = []
    
    for meta in analyzed_metadata:
        if not meta or not meta.get('crossref'):
            continue
            
        doi = meta['crossref'].get('DOI')
        pub_year = meta['crossref'].get('published', {}).get('date-parts', [[0]])[0][0]
        if not doi or not pub_year: 
            continue
        
        citings = state.citing_cache.get(doi, [])
        if not citings: 
            continue
        
        yearly = defaultdict(int)
        for c in citings:
            # Fix: correct way to get publication year
            if isinstance(c, dict):
                # If this is a dictionary with citation data
                if c.get('openalex'):
                    y = c['openalex'].get('publication_year')
                elif c.get('pub_date'):
                    # Try to extract year from date
                    try:
                        y = int(c['pub_date'][:4])
                    except:
                        y = None
                else:
                    y = None
            else:
                # If this is just a DOI string (fallback)
                y = None
                
            if y: 
                yearly[y] += 1
        
        total = sum(yearly.values())
        if total == 0: 
            continue
            
        cumulative = 0
        target = total / 2
        for y in range(pub_year, pub_year + 50):
            cumulative += yearly[y]
            if cumulative >= target:
                half_lives.append(y - pub_year)
                break
    
    return {
        'cited_half_life_median': int(np.median(half_lives)) if half_lives else None,
        'cited_half_life_mean': round(np.mean(half_lives), 1) if half_lives else None,
        'articles_with_chl': len(half_lives)
    }

def calculate_fwci_fast(analyzed_metadata):
    """Field-Weighted Citation Impact - improved calculation"""
    if not analyzed_metadata:
        return {
            'FWCI': 0,
            'total_cites': 0,
            'expected_cites': 0,
            'articles_with_concepts': 0,
            'method_used': 'no_data'
        }
    
    total_cites = 0
    expected_sum = 0.0
    articles_with_concepts = 0
    articles_processed = 0
    
    # Collect citation and concept data
    concept_citations = {}
    
    for meta in analyzed_metadata:
        oa = meta.get('openalex')
        if not oa: 
            continue
            
        cites = oa.get('cited_by_count', 0)
        total_cites += cites
        articles_processed += 1
        
        concepts = oa.get('concepts', [])
        if concepts:
            # Use top-3 concepts by score
            top_concepts = sorted(concepts, key=lambda x: x.get('score', 0), reverse=True)[:3]
            
            for concept in top_concepts:
                concept_name = concept.get('display_name', 'Unknown')
                concept_score = concept.get('score', 0)
                
                if concept_name not in concept_citations:
                    concept_citations[concept_name] = {
                        'total_cites': 0,
                        'article_count': 0,
                        'total_score': 0
                    }
                
                concept_citations[concept_name]['total_cites'] += cites
                concept_citations[concept_name]['article_count'] += 1
                concept_citations[concept_name]['total_score'] += concept_score
            
            articles_with_concepts += 1
    
    if articles_processed == 0 or total_cites == 0:
        return {
            'FWCI': 0,
            'total_cites': 0,
            'expected_cites': 0,
            'articles_with_concepts': 0,
            'method_used': 'no_citations'
        }
    
    # Expected citations calculation
    if concept_citations:
        # Method 1: based on concept averages
        for concept_data in concept_citations.values():
            if concept_data['article_count'] > 0:
                avg_cites_per_article = concept_data['total_cites'] / concept_data['article_count']
                avg_score = concept_data['total_score'] / concept_data['article_count']
                
                # Weight by concept score
                expected_contribution = avg_cites_per_article * avg_score
                expected_sum += expected_contribution
        
        method_used = 'concept_based'
    else:
        # Method 2: fallback - use global averages by discipline
        # (this is a simplification, real FWCI uses normalized data)
        
        # Assume basic expectations by article types
        for meta in analyzed_metadata:
            oa = meta.get('openalex')
            if not oa:
                continue
                
            # Simple heuristic approach
            cites = oa.get('cited_by_count', 0)
            work_type = oa.get('type', 'article')
            
            # Basic expectations by publication types
            type_expectations = {
                'article': 1.0,
                'review': 2.0,  # reviews usually cited more
                'conference': 0.7,
                'book': 0.5,
                'other': 0.8
            }
            
            expected = type_expectations.get(work_type, 1.0)
            expected_sum += expected
        
        method_used = 'type_based'
    
    # Normalization of expectations
    if expected_sum == 0:
        expected_sum = articles_processed * 1.0  # Fallback
        method_used = 'fallback'
    
    # FWCI calculation
    fwci = total_cites / expected_sum if expected_sum > 0 else 0
    
    return {
        'FWCI': round(fwci, 2),
        'total_cites': total_cites,
        'expected_cites': round(expected_sum, 2),
        'articles_with_concepts': articles_with_concepts,
        'method_used': method_used,
        'concepts_analyzed': len(concept_citations)
    }

def calculate_citation_velocity_fast(analyzed_metadata, state):
    """Citation Velocity - average citations per year for first 2 years"""
    velocities = []
    current_year = datetime.now().year
    
    for meta in analyzed_metadata:
        cr = meta.get('crossref')
        if not cr: 
            continue
            
        pub_year = cr.get('published', {}).get('date-parts', [[0]])[0][0]
        if current_year - pub_year < 2: 
            continue
        
        citings = state.citing_cache.get(cr.get('DOI'), [])
        early = 0
        
        for c in citings:
            if isinstance(c, dict):
                if c.get('openalex'):
                    citing_year = c['openalex'].get('publication_year', 0)
                elif c.get('pub_date'):
                    try:
                        citing_year = int(c['pub_date'][:4])
                    except:
                        citing_year = 0
                else:
                    citing_year = 0
            else:
                citing_year = 0
                
            if citing_year and citing_year <= pub_year + 2:
                early += 1
                
        velocities.append(early / 2.0)
    
    return {
        'citation_velocity': round(np.mean(velocities), 2) if velocities else 0,
        'articles_with_velocity': len(velocities)
    }

def calculate_oa_impact_premium_fast(analyzed_metadata):
    """Open Access Impact Premium - citation difference between OA and non-OA"""
    oa_citations = []
    non_oa_citations = []
    
    for meta in analyzed_metadata:
        oa = meta.get('openalex')
        if not oa: 
            continue
            
        cites = oa.get('cited_by_count', 0)
        is_oa = oa.get('open_access', {}).get('is_oa', False)
        
        if is_oa:
            oa_citations.append(cites)
        else:
            non_oa_citations.append(cites)
    
    oa_avg = np.mean(oa_citations) if oa_citations else 0
    non_oa_avg = np.mean(non_oa_citations) if non_oa_citations else 0
    
    premium = ((oa_avg - non_oa_avg) / non_oa_avg * 100) if non_oa_avg > 0 else 0
    
    return {
        'OA_impact_premium': round(premium, 1),
        'OA_articles': len(oa_citations),
        'non_OA_articles': len(non_oa_citations),
        'OA_avg_citations': round(oa_avg, 1),
        'non_OA_avg_citations': round(non_oa_avg, 1)
    }

def calculate_elite_index_fast(analyzed_metadata):
    """Elite Index - percentage of articles in top-10% by citations"""
    if not analyzed_metadata:
        return {'elite_index': 0}
    
    citations = []
    for meta in analyzed_metadata:
        oa = meta.get('openalex')
        if oa:
            cites = oa.get('cited_by_count', 0)
            citations.append(cites)
    
    if not citations:
        return {'elite_index': 0}
    
    # DIAGNOSTICS: output citation statistics
    print(f"🔍 Elite Index diagnostics:")
    print(f"   Total articles with citation data: {len(citations)}")
    print(f"   Citation distribution: min={min(citations)}, max={max(citations)}, mean={np.mean(citations):.1f}, median={np.median(citations)}")
    
    # Problem: np.percentile(citations, 90) always gives 90th percentile WITHIN our dataset
    # But Elite Index should be compared with GLOBAL data
    
    # Temporary solution: use heuristic based on distribution
    if max(citations) == 0:
        return {'elite_index': 0}
    
    # Alternative approach 1: count top-10% from maximum value
    max_citations = max(citations)
    threshold_alt1 = max_citations * 0.1  # 10% of maximum
    
    # Alternative approach 2: use quantiles more aggressively
    threshold_alt2 = int(np.percentile(citations, 85))  # More strict threshold
    
    # Alternative approach 3: based on standard deviation
    if len(citations) > 1:
        mean_cites = np.mean(citations)
        std_cites = np.std(citations)
        threshold_alt3 = mean_cites + std_cites  # Articles above average + one standard deviation
    else:
        threshold_alt3 = max(citations)
    
    # Use the most meaningful approach
    threshold = threshold_alt3
    
    elite_count = sum(1 for c in citations if c >= threshold)
    elite_index = round(elite_count / len(citations) * 100, 2)
    
    print(f"   Thresholds: percent90={np.percentile(citations, 90):.1f}, alt1={threshold_alt1:.1f}, alt2={threshold_alt2:.1f}, alt3={threshold_alt3:.1f}")
    print(f"   Result: elite_count={elite_count}, elite_index={elite_index}%")
    
    return {
        'elite_index': elite_index,
        'elite_articles': elite_count,
        'total_articles': len(citations),
        'citation_threshold': int(threshold),
        'method_used': 'mean_plus_std',
        'debug_info': {
            'percentile_90': np.percentile(citations, 90),
            'max_citations': max(citations),
            'mean_citations': np.mean(citations),
            'median_citations': np.median(citations)
        }
    }

def calculate_author_gini_fast(analyzed_metadata):
    """Author Gini Index - inequality index of publication distribution among authors"""
    author_counts = Counter()
    
    for meta in analyzed_metadata:
        oa = meta.get('openalex')
        if oa and 'authorships' in oa:
            for auth in oa['authorships']:
                author_id = auth.get('author', {}).get('id')
                if author_id:
                    author_counts[author_id] += 1
    
    if len(author_counts) < 2:
        return {'author_gini': 0}
    
    # Gini index calculation
    values = sorted(author_counts.values())
    n = len(values)
    cumulative = np.cumsum(values).astype(float)
    gini = (n + 1 - 2 * np.sum(cumulative) / cumulative[-1]) / n
    
    return {
        'author_gini': round(gini, 3),
        'total_authors': len(author_counts),
        'articles_per_author_avg': round(np.mean(values), 2),
        'articles_per_author_median': int(np.median(values))
    }

def calculate_dbi_fast(analyzed_metadata):
    """Diversity Balance Index - thematic diversification index"""
    concept_freq = Counter()
    total_concepts = 0
    
    for meta in analyzed_metadata:
        oa = meta.get('openalex')
        if oa and 'concepts' in oa:
            concepts = oa['concepts']
            # === ИЗМЕНЕНИЕ: расширяем до 10 терминов ===
            for concept in concepts[:10]:  # Take top-10 concepts
                concept_name = concept.get('display_name', '')
                if concept_name:
                    concept_freq[concept_name] += 1
                    total_concepts += 1
    
    if total_concepts == 0:
        return {'DBI': 0}
    
    # Shannon index
    proportions = [count / total_concepts for count in concept_freq.values()]
    shannon = -sum(p * np.log(p) for p in proportions if p > 0)
    
    # Normalization (maximum = log(n))
    max_shannon = np.log(len(concept_freq)) if concept_freq else 1
    dbi = shannon / max_shannon if max_shannon > 0 else 0
    
    return {
        'DBI': round(dbi, 3),
        'unique_concepts': len(concept_freq),
        'total_concept_mentions': total_concepts,
        # === ИЗМЕНЕНИЕ: расширяем до 10 терминов ===
        'top_concepts': concept_freq.most_common(10)
    }

def calculate_all_fast_metrics(analyzed_metadata, citing_metadata, state, journal_issn):
    """Calculation of all fast metrics in one pass with comprehensive error handling"""
    fast_metrics = {}
    
    # 1. Reference Age metrics
    try:
        reference_age_metrics = calculate_reference_age_fast(analyzed_metadata, state)
        fast_metrics.update(reference_age_metrics)
    except Exception as e:
        st.warning(f"⚠️ Reference Age calculation failed: {str(e)}")
        fast_metrics.update({
            'ref_median_age': None,
            'ref_mean_age': None,
            'ref_ages_25_75': [None, None],
            'total_refs_analyzed': 0
        })
    
    # 2. JSCR metrics with enhanced debugging
    try:
        jscr_metrics = calculate_jscr_fast(citing_metadata, journal_issn)
        fast_metrics.update(jscr_metrics)
        
        # Enhanced debug output
        debug_info = []
        debug_info.append(f"=== JSCR DEBUG ===")
        debug_info.append(f"Journal ISSN: {journal_issn}")
        debug_info.append(f"Clean ISSN: {jscr_metrics.get('journal_issn_clean', 'N/A')}")
        debug_info.append(f"Total citing works processed: {jscr_metrics.get('total_cites', 0)}")
        debug_info.append(f"Self-cites found: {jscr_metrics.get('self_cites', 0)}")
        debug_info.append(f"JSCR: {jscr_metrics.get('JSCR', 0)}%")
        
        # Log first few debug samples if available
        if 'debug_samples' in jscr_metrics and jscr_metrics['debug_samples']:
            debug_info.append("First 5 items analysis:")
            for i, debug in enumerate(jscr_metrics['debug_samples'][:5]):
                debug_info.append(f"  {i+1}. {debug}")
        
        # Print debug info to console
        print("\n".join(debug_info))
        
    except Exception as e:
        st.warning(f"⚠️ JSCR calculation failed: {str(e)}")
        fast_metrics.update({
            'JSCR': 0,
            'self_cites': 0,
            'total_cites': 0,
            'journal_issn_clean': journal_issn.replace('-', '').upper() if journal_issn else ""
        })
    
    # 3. Cited Half-Life metrics with robust error handling
    try:
        cited_half_life_metrics = calculate_cited_half_life_fast(analyzed_metadata, state)
        fast_metrics.update(cited_half_life_metrics)
    except Exception as e:
        st.warning(f"⚠️ Cited Half-Life calculation failed: {str(e)}")
        fast_metrics.update({
            'cited_half_life_median': None,
            'cited_half_life_mean': None,
            'articles_with_chl': 0
        })
    
    # 4. Field-Weighted Citation Impact
    try:
        fwci_metrics = calculate_fwci_fast(analyzed_metadata)
        fast_metrics.update(fwci_metrics)
    except Exception as e:
        st.warning(f"⚠️ FWCI calculation failed: {str(e)}")
        fast_metrics.update({
            'FWCI': 0,
            'total_cites_fwci': 0,
            'expected_cites': 0,
            'articles_with_concepts': 0
        })
    
    # 5. Citation Velocity with data validation
    try:
        citation_velocity_metrics = calculate_citation_velocity_fast(analyzed_metadata, state)
        fast_metrics.update(citation_velocity_metrics)
    except Exception as e:
        st.warning(f"⚠️ Citation Velocity calculation failed: {str(e)}")
        fast_metrics.update({
            'citation_velocity': 0,
            'articles_with_velocity': 0
        })
    
    # 6. Open Access Impact Premium
    try:
        oa_impact_premium_metrics = calculate_oa_impact_premium_fast(analyzed_metadata)
        fast_metrics.update(oa_impact_premium_metrics)
    except Exception as e:
        st.warning(f"⚠️ OA Impact Premium calculation failed: {str(e)}")
        fast_metrics.update({
            'OA_impact_premium': 0,
            'OA_articles': 0,
            'non_OA_articles': 0,
            'OA_avg_citations': 0,
            'non_OA_avg_citations': 0
        })
    
    # 7. Elite Index
    try:
        elite_index_metrics = calculate_elite_index_fast(analyzed_metadata)
        fast_metrics.update(elite_index_metrics)
    except Exception as e:
        st.warning(f"⚠️ Elite Index calculation failed: {str(e)}")
        fast_metrics.update({
            'elite_index': 0,
            'elite_articles': 0,
            'total_articles_elite': 0,
            'citation_threshold': 0
        })
    
    # 8. Author Gini Index
    try:
        author_gini_metrics = calculate_author_gini_fast(analyzed_metadata)
        fast_metrics.update(author_gini_metrics)
    except Exception as e:
        st.warning(f"⚠️ Author Gini calculation failed: {str(e)}")
        fast_metrics.update({
            'author_gini': 0,
            'total_authors': 0,
            'articles_per_author_avg': 0,
            'articles_per_author_median': 0
        })
    
    # 9. Diversity Balance Index
    try:
        dbi_metrics = calculate_dbi_fast(analyzed_metadata)
        fast_metrics.update(dbi_metrics)
    except Exception as e:
        st.warning(f"⚠️ DBI calculation failed: {str(e)}")
        fast_metrics.update({
            'DBI': 0,
            'unique_concepts': 0,
            'total_concept_mentions': 0,
            'top_concepts': []
        })
    
    # 10. Additional diagnostic information (with safe array handling)
    try:
        # Add summary statistics for debugging
        fast_metrics['diagnostic_info'] = {
            'analyzed_articles_count': len(analyzed_metadata),
            'citing_articles_count': len(citing_metadata),
            'citing_cache_size': len(state.citing_cache),
            'successful_metrics': len([k for k in fast_metrics.keys() if is_valid_value(fast_metrics[k])])
        }
        
        # Calculate overall data quality score with safe array handling
        quality_indicators = []
        
        # Safe checks for each indicator
        refs_analyzed = fast_metrics.get('total_refs_analyzed', 0)
        quality_indicators.append(refs_analyzed > 0 if not hasattr(refs_analyzed, 'size') else refs_analyzed.size > 0)
        
        total_cites = fast_metrics.get('total_cites', 0)
        quality_indicators.append(total_cites > 0 if not hasattr(total_cites, 'size') else total_cites.size > 0)
        
        articles_chl = fast_metrics.get('articles_with_chl', 0)
        quality_indicators.append(articles_chl > 0 if not hasattr(articles_chl, 'size') else articles_chl.size > 0)
        
        articles_velocity = fast_metrics.get('articles_with_velocity', 0)
        quality_indicators.append(articles_velocity > 0 if not hasattr(articles_velocity, 'size') else articles_velocity.size > 0)
        
        oa_articles = fast_metrics.get('OA_articles', 0)
        non_oa_articles = fast_metrics.get('non_OA_articles', 0)
        oa_check = (oa_articles > 0 if not hasattr(oa_articles, 'size') else oa_articles.size > 0)
        non_oa_check = (non_oa_articles > 0 if not hasattr(non_oa_articles, 'size') else non_oa_articles.size > 0)
        quality_indicators.append(oa_check or non_oa_check)
        
        total_authors = fast_metrics.get('total_authors', 0)
        quality_indicators.append(total_authors > 0 if not hasattr(total_authors, 'size') else total_authors.size > 0)
        
        unique_concepts = fast_metrics.get('unique_concepts', 0)
        quality_indicators.append(unique_concepts > 0 if not hasattr(unique_concepts, 'size') else unique_concepts.size > 0)
        
        # Calculate quality score safely
        if quality_indicators:
            quality_score = sum(quality_indicators) / len(quality_indicators) * 100
            fast_metrics['data_quality_score'] = round(quality_score, 1)
        else:
            fast_metrics['data_quality_score'] = 0
        
    except Exception as e:
        st.warning(f"⚠️ Diagnostic information calculation failed: {str(e)}")
        fast_metrics.update({
            'diagnostic_info': {'error': str(e)},
            'data_quality_score': 0
        })
    
    # 11. Final validation and cleanup
    try:
        # Ensure all expected keys are present with safe defaults
        expected_keys = {
            'ref_median_age', 'ref_mean_age', 'ref_ages_25_75', 'total_refs_analyzed',
            'JSCR', 'self_cites', 'total_cites', 'journal_issn_clean',
            'cited_half_life_median', 'cited_half_life_mean', 'articles_with_chl',
            'FWCI', 'total_cites_fwci', 'expected_cites', 'articles_with_concepts',
            'citation_velocity', 'articles_with_velocity',
            'OA_impact_premium', 'OA_articles', 'non_OA_articles', 'OA_avg_citations', 'non_OA_avg_citations',
            'elite_index', 'elite_articles', 'total_articles_elite', 'citation_threshold',
            'author_gini', 'total_authors', 'articles_per_author_avg', 'articles_per_author_median',
            'DBI', 'unique_concepts', 'total_concept_mentions', 'top_concepts',
            'data_quality_score'
        }
        
        for key in expected_keys:
            if key not in fast_metrics:
                if key == 'ref_ages_25_75':
                    fast_metrics[key] = [None, None]
                elif key == 'top_concepts':
                    fast_metrics[key] = []
                elif 'pct' in key or 'rate' in key or 'index' in key or 'premium' in key:
                    fast_metrics[key] = 0.0
                else:
                    fast_metrics[key] = 0
        
        # Clean up any None values and convert numpy types to Python types
        for key in list(fast_metrics.keys()):
            value = fast_metrics[key]
            
            # Handle numpy arrays and types
            if hasattr(value, 'item'):  # numpy scalar
                try:
                    fast_metrics[key] = value.item()
                except:
                    fast_metrics[key] = 0
            elif hasattr(value, 'size'):  # numpy array
                if value.size == 0:
                    fast_metrics[key] = [] if key == 'top_concepts' else 0
                elif value.size == 1:
                    try:
                        fast_metrics[key] = value.item()
                    except:
                        fast_metrics[key] = 0
                else:
                    fast_metrics[key] = value.tolist() if key == 'ref_ages_25_75' else 0
            
            # Handle None values
            elif value is None:
                if key == 'ref_ages_25_75':
                    fast_metrics[key] = [None, None]
                elif key == 'top_concepts':
                    fast_metrics[key] = []
                elif isinstance(value, (int, float)):
                    fast_metrics[key] = 0
                else:
                    fast_metrics[key] = 0
        
    except Exception as e:
        st.error(f"❌ Final validation failed: {str(e)}")
    
    # 12. Log completion with safe value checking
    try:
        successful_calculations = len([k for k in fast_metrics.keys() if is_valid_value(fast_metrics[k])])
        total_calculations = len(fast_metrics)
        
        print(f"✅ Fast metrics calculation completed: {successful_calculations}/{total_calculations} successful")
        print(f"📊 Data quality score: {fast_metrics.get('data_quality_score', 0)}%")
        
    except Exception as e:
        print(f"⚠️ Completion logging failed: {str(e)}")
    
    return fast_metrics

def is_valid_value(value):
    """Safe function to check if a value is valid (not empty/zero/None)"""
    try:
        if value is None:
            return False
        
        # Handle numpy arrays and types
        if hasattr(value, 'size'):
            if value.size == 0:
                return False
            elif value.size == 1:
                return value.item() not in [0, None]
            else:
                return True
        
        # Handle regular Python types
        if isinstance(value, (list, tuple, dict)):
            return len(value) > 0
        elif isinstance(value, (int, float)):
            return value != 0
        elif isinstance(value, str):
            return value != ""
        else:
            return value not in [0, None, [], ""]
    
    except Exception:
        return False

# === NEW FUNCTIONS FOR ADDITIONAL FEATURES ===

def normalize_issn_for_comparison(issn):
    """Normalize ISSN for comparison"""
    if not issn:
        return ""

    # Convert to string if it's a float or other numeric type
    if isinstance(issn, (float, int)):
        # Handle NaN values and convert to string without decimal for integers
        if pd.isna(issn):
            return ""
        issn_str = str(int(issn)) if isinstance(issn, float) and issn.is_integer() else str(issn)
    else:
        issn_str = str(issn)
    
    # Remove any hyphens and spaces
    clean_issn = issn_str.replace('-', '').replace(' ', '')

    # Remove any decimal points if present (for float conversion)
    clean_issn = clean_issn.replace('.', '')
    
    # === FIX: Add leading zeros for 7-digit ISSNs ===
    if len(clean_issn) == 7:
        clean_issn = '0' + clean_issn  # Add leading zero
    
    # Pad with leading zeros to make 8 digits
    normalized = clean_issn.zfill(8)
    
    return normalized

def load_metrics_data():
    """Load IF and CS data from Excel files"""
    state = get_analysis_state()
    
    # Load IF data (Web of Science)
    try:
        if os.path.exists('IF.xlsx'):
            state.if_data = pd.read_excel('IF.xlsx')
            # Removed success message to avoid showing in interface
        else:
            # Removed warning message to avoid showing in interface
            state.if_data = pd.DataFrame()
    except Exception as e:
        # Removed error message to avoid showing in interface
        state.if_data = pd.DataFrame()
    
    # Load CS data (Scopus) - UPDATED: Now loading CS.xlsx
    try:
        if os.path.exists('CS.xlsx'):
            state.cs_data = pd.read_excel('CS.xlsx')
            # Removed success message to avoid showing in interface
        else:
            # Removed warning message to avoid showing in interface
            state.cs_data = pd.DataFrame()
    except Exception as e:
        # Removed error message to avoid showing in interface
        state.cs_data = pd.DataFrame()

def get_journal_metrics(journal_issns):
    """Get metrics for a journal based on its ISSNs"""
    state = get_analysis_state()
    
    if_metrics = {}
    cs_metrics = {}
    
    # Process each ISSN to find matches
    for issn in journal_issns:
        if not issn or pd.isna(issn):
            continue
            
        normalized_issn = normalize_issn_for_comparison(issn)
        print(f"🔍 Searching for ISSN: {issn} -> normalized: {normalized_issn}")
        
        # Search in Web of Science data (IF)
        if not state.if_data.empty and not if_metrics:  # Only search if not already found
            # Apply normalization with error handling
            def safe_normalize_issn(issn_series):
                try:
                    return issn_series.fillna('').astype(str).apply(normalize_issn_for_comparison)
                except Exception as e:
                    print(f"Error normalizing IF ISSN: {e}")
                    return pd.Series([""] * len(issn_series))
    
            if_match = state.if_data[
                (safe_normalize_issn(state.if_data['ISSN']) == normalized_issn) |
                (safe_normalize_issn(state.if_data['eISSN']) == normalized_issn)
            ]
            
            if not if_match.empty:
                print(f"✅ Found IF match: {len(if_match)} records")
                if_metrics = {
                    'if': if_match.iloc[0]['IF'],
                    'quartile': if_match.iloc[0]['Quartile']
                }
                # Do NOT break here - continue searching for CS metrics
                  
        # Search in Scopus data (CS) - UPDATED: Now searching in CS.xlsx
        if not state.cs_data.empty and not cs_metrics:  # Only search if not already found
            # Apply normalization for CS data
            def safe_normalize_cs_issn(issn_series):
                try:
                    return issn_series.fillna('').astype(str).apply(normalize_issn_for_comparison)
                except Exception as e:
                    print(f"Error normalizing CS ISSN: {e}")
                    return pd.Series([""] * len(issn_series))
            
            # Search for matches in Print ISSN or E-ISSN columns
            cs_match = state.cs_data[
                (safe_normalize_cs_issn(state.cs_data['Print ISSN']) == normalized_issn) |
                (safe_normalize_cs_issn(state.cs_data['E-ISSN']) == normalized_issn)
            ]
            
            if not cs_match.empty:
                print(f"✅ Found CS match: {len(cs_match)} records")
                # Handle duplicates - take the best quartile (lowest number)
                best_quartile = cs_match['Quartile'].min()
                corresponding_citescore = cs_match[cs_match['Quartile'] == best_quartile]['CiteScore'].iloc[0]
                
                cs_metrics = {
                    'citescore': corresponding_citescore,
                    'quartile': f"Q{int(best_quartile)}"
                }
                # Do NOT break here - continue processing other ISSNs if needed
    
        # If we found both metrics, we can stop early
        if if_metrics and cs_metrics:
            break

    print(f"🎯 Final metrics - IF: {if_metrics}, CS: {cs_metrics}")

    return {
        'if_metrics': if_metrics,
        'cs_metrics': cs_metrics
    }

def analyze_citation_seasonality(analyzed_metadata, state, median_days_to_first_citation):
    """Analyze citation seasonality and predict optimal publication months"""
    citation_months = Counter()
    publication_months = Counter()
    
    # Collect citation months
    for analyzed in analyzed_metadata:
        if analyzed and analyzed.get('crossref'):
            analyzed_doi = analyzed['crossref'].get('DOI')
            if not analyzed_doi:
                continue
                
            citings = state.citing_cache.get(analyzed_doi, [])
            
            for citing in citings:
                if citing.get('pub_date'):
                    try:
                        cite_date = datetime.fromisoformat(citing['pub_date'].replace('Z', '+00:00'))
                        citation_months[cite_date.month] += 1
                    except:
                        continue
    
    # Collect publication months of analyzed articles
    for analyzed in analyzed_metadata:
        if analyzed and analyzed.get('crossref'):
            date_parts = analyzed['crossref'].get('published', {}).get('date-parts', [[]])[0]
            if len(date_parts) >= 2:  # Has at least year and month
                publication_months[date_parts[1]] += 1
    
    # Calculate optimal publication months based on citation seasonality and median time to first citation
    optimal_months = []
    if citation_months and median_days_to_first_citation > 0:
        # Find months with highest citations
        top_citation_months = [month for month, count in citation_months.most_common(3)]
        
        # Calculate recommended publication months (considering median time to first citation)
        for citation_month in top_citation_months:
            # Calculate when to publish to get citations in high-citation months
            days_to_subtract = median_days_to_first_citation
            recommended_publication_month = int((citation_month - (days_to_subtract // 30)) % 12)
            if recommended_publication_month == 0:
                recommended_publication_month = 12
            
            optimal_months.append({
                'citation_month': citation_month,
                'citation_count': citation_months[citation_month],
                'recommended_publication_month': recommended_publication_month,
                'reasoning': f"Publish in month {recommended_publication_month} to receive citations in high-citation month {citation_month} (considering {median_days_to_first_citation} days median time to first citation)"
            })
    
    return {
        'citation_months': dict(citation_months),
        'publication_months': dict(publication_months),
        'optimal_publication_months': optimal_months,
        'total_citations_by_month': sum(citation_months.values())
    }

def find_potential_reviewers(analyzed_metadata, citing_metadata, overlap_details, state):
    """Find potential reviewers from citing authors who never published in the journal"""
    
    # Get all authors from analyzed articles (journal authors)
    journal_authors = set()
    for analyzed in analyzed_metadata:
        if analyzed and analyzed.get('openalex'):
            authors, _, _ = extract_affiliations_and_countries(analyzed.get('openalex'))
            journal_authors.update(authors)
    
    # Get overlap authors (those who already have connections with the journal)
    overlap_authors = set()
    for overlap in overlap_details:
        overlap_authors.update(overlap['common_authors'])
    
    # Find citing authors who are NOT in journal authors and NOT in overlap authors
    potential_reviewer_candidates = Counter()
    reviewer_citation_details = defaultdict(list)
    
    for citing in citing_metadata:
        if not citing or not citing.get('openalex'):
            continue
            
        authors, _, _ = extract_affiliations_and_countries(citing.get('openalex'))
        citing_doi = citing.get('doi', 'Unknown DOI')
        
        for author in authors:
            # Check if author is NOT a journal author and NOT an overlap author
            if author not in journal_authors and author not in overlap_authors and author != 'Unknown':
                potential_reviewer_candidates[author] += 1
                reviewer_citation_details[author].append(citing_doi)
    
    # Prepare detailed results - filter out authors with only 1 citation
    potential_reviewers = []
    for author, citation_count in potential_reviewer_candidates.most_common():
        if citation_count > 1:  # Only include authors with more than 1 citation
            potential_reviewers.append({
                'author': author,
                'citation_count': citation_count,
                'citing_dois': reviewer_citation_details[author]  # Keep all DOIs for detailed analysis
            })
    
    return {
        'potential_reviewers': potential_reviewers,
        'total_journal_authors': len(journal_authors),
        'total_overlap_authors': len(overlap_authors),
        'total_potential_reviewers': len(potential_reviewers)
    }

# === NEW CLASS FOR TITLE KEYWORDS ANALYSIS ===
class TitleKeywordsAnalyzer:
    def __init__(self):
        # Инициализация стоп-слов и стеммера
        try:
            import nltk
            from nltk.corpus import stopwords
            from nltk.stem import PorterStemmer
            
            # Загружаем стоп-слова
            nltk.download('stopwords', quiet=True)
            self.stop_words = set(stopwords.words('english'))
            self.stemmer = PorterStemmer()
        except:
            # Fallback если nltk не доступен
            self.stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            self.stemmer = None
        
        # Научные стоп-слова
        self.scientific_stopwords = {
            'activation', 'adaptive', 'advanced', 'analysis', 'application',
            'applications', 'approach', 'architecture', 'artificial', 'assessment',
            'based', 'behavior', 'capacity', 'characteristics', 'characterization',
            'coating', 'coatings', 'comparative', 'computational', 'composite',
            'composites', 'control', 'cycle', 'damage', 'data', 'density', 'design',
            'detection', 'development', 'device', 'devices', 'diagnosis', 'discovery',
            'dynamic', 'dynamics', 'economic', 'effect', 'effects', 'efficacy',
            'efficient', 'energy', 'engineering', 'enhanced', 'environmental',
            'evaluation', 'experimental', 'exploration', 'factors', 'failure',
            'fabrication', 'field', 'film', 'films', 'flow', 'framework', 'frequency',
            'functional', 'growth', 'high', 'impact', 'improved', 'improvement',
            'induced', 'influence', 'information', 'innovative', 'intelligent',
            'interaction', 'interface', 'interfaces', 'investigation', 'knowledge',
            'layer', 'layers', 'learning', 'magnetic', 'management', 'material',
            'materials', 'measurement', 'mechanism', 'mechanisms', 'medical',
            'method', 'methods', 'model', 'models', 'modification', 'modulation',
            'molecular', 'monitoring', 'motion', 'nanoparticle', 'nanoparticles',
            'nanostructure', 'nanostructures', 'network', 'neural', 'new', 'nonlinear',
            'novel', 'numerical', 'optical', 'optimization', 'pattern', 'performance',
            'phenomenon', 'potential', 'power', 'prediction', 'preparation', 'process',
            'processing', 'production', 'progression', 'property', 'properties',
            'quality', 'regulation', 'relationship', 'reliability', 'remote', 'repair',
            'research', 'resistance', 'response', 'review', 'risk', 'role', 'safety',
            'sample', 'samples', 'scale', 'screening', 'separation', 'signal',
            'simulation', 'specific', 'stability', 'stable', 'state', 'storage',
            'strain', 'strength', 'stress', 'structural', 'structure', 'study',
            'studies', 'sustainable', 'synergy', 'synthesis', 'system', 'systems',
            'targeted', 'techniques', 'technology', 'testing', 'theoretical', 'therapy',
            'thermal', 'tissue', 'tolerance', 'toxicity', 'transformation', 'transition',
            'transmission', 'transport', 'type', 'understanding', 'using', 'validation',
            'value', 'variation', 'virtual', 'waste', 'wave'
        }
        
        # Стемминг научных стоп-слов
        if self.stemmer:
            self.scientific_stopwords_stemmed = {
                self.stemmer.stem(word) for word in self.scientific_stopwords
            }
        else:
            self.scientific_stopwords_stemmed = self.scientific_stopwords
    
    def preprocess_content_words(self, text: str) -> List[str]:
        """Очищает и нормализует содержательные слова (удалено слово 'sub')"""
        if not text or text in ['Название не найдено', 'Таймаут запроса', 'Ошибка сети', 'Ошибка при получении']:
            return []

        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s-]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        words = text.split()
        content_words = []

        for word in words:
            # ИСКЛЮЧАЕМ слово "sub"
            if word == 'sub':
                continue
            if '-' in word:
                continue
            if len(word) > 2 and word not in self.stop_words:
                if self.stemmer:
                    stemmed_word = self.stemmer.stem(word)
                else:
                    stemmed_word = word
                if stemmed_word not in self.scientific_stopwords_stemmed:
                    content_words.append(stemmed_word)

        return content_words

    def extract_compound_words(self, text: str) -> List[str]:
        """Извлекает составные слова через дефис"""
        if not text or text in ['Название не найдено', 'Таймаут запроса', 'Ошибка сети', 'Ошибка при получении']:
            return []

        text = text.lower()
        compound_words = re.findall(r'\b[a-z]{2,}-[a-z]{2,}(?:-[a-z]{2,})*\b', text)

        filtered_compounds = []
        for word in compound_words:
            parts = word.split('-')
            if not any(part in self.stop_words for part in parts):
                filtered_compounds.append(word)

        return filtered_compounds

    def extract_scientific_stopwords(self, text: str) -> List[str]:
        """Извлекает научные стоп-слова"""
        if not text or text in ['Название не найдено', 'Таймаут запроса', 'Ошибка сети', 'Ошибка при получении']:
            return []

        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        words = text.split()
        scientific_words = []

        for word in words:
            if len(word) > 2:
                if self.stemmer:
                    stemmed_word = self.stemmer.stem(word)
                else:
                    stemmed_word = word
                if stemmed_word in self.scientific_stopwords_stemmed:
                    for original_word in self.scientific_stopwords:
                        if self.stemmer:
                            original_stemmed = self.stemmer.stem(original_word)
                        else:
                            original_stemmed = original_word
                        if original_stemmed == stemmed_word:
                            scientific_words.append(original_word)
                            break

        return scientific_words

    def analyze_titles(self, analyzed_titles: List[str], citing_titles: List[str]) -> dict:
        """Анализирует ключевые слова в названиях анализируемых и цитирующих статей"""
        # Анализ анализируемых статей
        analyzed_content_words = []
        analyzed_compound_words = []
        analyzed_scientific_words = []
        
        valid_analyzed_titles = [t for t in analyzed_titles if t and t not in ['Название не найдено', 'Таймаут запроса', 'Ошибка сети', 'Ошибка при получении']]
        
        for title in valid_analyzed_titles:
            analyzed_content_words.extend(self.preprocess_content_words(title))
            analyzed_compound_words.extend(self.extract_compound_words(title))
            analyzed_scientific_words.extend(self.extract_scientific_stopwords(title))
        
        # Анализ цитирующих статей
        citing_content_words = []
        citing_compound_words = []
        citing_scientific_words = []
        
        valid_citing_titles = [t for t in citing_titles if t and t not in ['Название не найдено', 'Таймаут запроса', 'Ошибка сети', 'Ошибка при получении']]
        
        for title in valid_citing_titles:
            citing_content_words.extend(self.preprocess_content_words(title))
            citing_compound_words.extend(self.extract_compound_words(title))
            citing_scientific_words.extend(self.extract_scientific_stopwords(title))
        
        # Подсчет частот
        analyzed_content_freq = Counter(analyzed_content_words)
        analyzed_compound_freq = Counter(analyzed_compound_words)
        analyzed_scientific_freq = Counter(analyzed_scientific_words)
        
        citing_content_freq = Counter(citing_content_words)
        citing_compound_freq = Counter(citing_compound_words)
        citing_scientific_freq = Counter(citing_scientific_words)
        
        # Топ-50 для каждого типа
        top_50_analyzed_content = analyzed_content_freq.most_common(50)
        top_50_analyzed_compound = analyzed_compound_freq.most_common(50)
        top_50_analyzed_scientific = analyzed_scientific_freq.most_common(50)
        
        top_50_citing_content = citing_content_freq.most_common(50)
        top_50_citing_compound = citing_compound_freq.most_common(50)
        top_50_citing_scientific = citing_scientific_freq.most_common(50)
        
        return {
            'analyzed': {
                'content_words': top_50_analyzed_content,
                'compound_words': top_50_analyzed_compound,
                'scientific_words': top_50_analyzed_scientific,
                'total_titles': len(valid_analyzed_titles)
            },
            'citing': {
                'content_words': top_50_citing_content,
                'compound_words': top_50_citing_compound,
                'scientific_words': top_50_citing_scientific,
                'total_titles': len(valid_citing_titles)
            }
        }

def extract_titles_from_metadata(metadata_list):
    """Извлекает названия статей из метаданных"""
    titles = []
    for meta in metadata_list:
        if not meta:
            titles.append('')
            continue
            
        cr = meta.get('crossref')
        oa = meta.get('openalex')
        
        title = ''
        if cr:
            title_list = cr.get('title', [])
            if title_list:
                title = title_list[0]
        elif oa:
            title = oa.get('title', '')
        
        titles.append(title if title else '')
    
    return titles

def normalize_author_name(author_name):
    """Нормализация имени автора - оставляем только первый инициал"""
    if not author_name:
        return author_name
    
    # Убираем лишние точки (исправляем Pikalova E..Y. -> Pikalova E.Y.)
    author_name = re.sub(r'\.\.', '.', author_name)
    
    # Разделяем фамилию и инициалы
    parts = author_name.split()
    if len(parts) < 2:
        return author_name
    
    # Берем фамилию (первая часть) и первый инициал
    surname = parts[0]
    initials = parts[1]
    
    # Берем только первую букву инициалов (первый инициал)
    if '.' in initials:
        # Если инициалы с точками: "E.Y." -> берем "E."
        first_initials = re.findall(r'[A-Z]\.', initials)
        if first_initials:
            first_initial = first_initials[0]
        else:
            # Если формат другой, берем первую букву
            first_initial = initials[0] + '.' if len(initials) > 0 else ''
    else:
        # Если без точек: "EY" -> берем "E."
        first_initial = initials[0] + '.' if len(initials) > 0 else ''
    
    return f"{surname} {first_initial}".strip()

def normalize_keywords_data(keywords_data):
    """Нормализация данных ключевых слов для объединенного листа"""
    normalized_data = []
    
    # Нормализация для content words
    analyzed_total = keywords_data['analyzed']['total_titles']
    citing_total = keywords_data['citing']['total_titles']
    
    # Content words
    for i, (word, analyzed_count) in enumerate(keywords_data['analyzed']['content_words'], 1):
        citing_count = next((c for w, c in keywords_data['citing']['content_words'] if w == word), 0)
        
        # Нормализация частот
        norm_analyzed = analyzed_count / analyzed_total if analyzed_total > 0 else 0
        norm_citing = citing_count / citing_total if citing_total > 0 else 0
        total_norm = norm_analyzed + norm_citing
        ratio = norm_analyzed / norm_citing if norm_citing > 0 else float('inf')
        
        normalized_data.append({
            'Rank': i,
            'Keyword Type': 'Content',
            'Keyword': word,
            'Norm_Analyzed': round(norm_analyzed, 4),
            'Norm_Citing': round(norm_citing, 4),
            'Total_Norm': round(total_norm, 4),
            'Ratio_Analyzed/Citing': round(ratio, 2)
        })
    
    # Compound words
    for i, (word, analyzed_count) in enumerate(keywords_data['analyzed']['compound_words'], 1):
        citing_count = next((c for w, c in keywords_data['citing']['compound_words'] if w == word), 0)
        
        norm_analyzed = analyzed_count / analyzed_total if analyzed_total > 0 else 0
        norm_citing = citing_count / citing_total if citing_total > 0 else 0
        total_norm = norm_analyzed + norm_citing
        ratio = norm_analyzed / norm_citing if norm_citing > 0 else float('inf')
        
        normalized_data.append({
            'Rank': i,
            'Keyword Type': 'Compound',
            'Keyword': word,
            'Norm_Analyzed': round(norm_analyzed, 4),
            'Norm_Citing': round(norm_citing, 4),
            'Total_Norm': round(total_norm, 4),
            'Ratio_Analyzed/Citing': round(ratio, 2)
        })
    
    # Scientific stopwords
    for i, (word, analyzed_count) in enumerate(keywords_data['analyzed']['scientific_words'], 1):
        citing_count = next((c for w, c in keywords_data['citing']['scientific_words'] if w == word), 0)
        
        norm_analyzed = analyzed_count / analyzed_total if analyzed_total > 0 else 0
        norm_citing = citing_count / citing_total if citing_total > 0 else 0
        total_norm = norm_analyzed + norm_citing
        ratio = norm_analyzed / norm_citing if norm_citing > 0 else float('inf')
        
        normalized_data.append({
            'Rank': i,
            'Keyword Type': 'Scientific',
            'Keyword': word,
            'Norm_Analyzed': round(norm_analyzed, 4),
            'Norm_Citing': round(norm_citing, 4),
            'Total_Norm': round(total_norm, 4),
            'Ratio_Analyzed/Citing': round(ratio, 2)
        })
    
    # Сортировка по убыванию Norm_Citing
    normalized_data.sort(key=lambda x: x['Norm_Citing'], reverse=True)
    
    # Обновляем ранги после сортировки
    for i, item in enumerate(normalized_data, 1):
        item['Rank'] = i
    
    return normalized_data

# === NEW FUNCTION FOR SPECIAL ANALYSIS METRICS ===
def create_issn_lookup_cache(state):
    """Создает кэш для быстрого поиска ISSN в базах данных"""
    # Кэш для Scopus (CS.xlsx)
    scopus_issn_cache = set()
    if not state.cs_data.empty:
        print("🔍 Building Scopus ISSN cache...")
        for col in ['Print ISSN', 'E-ISSN']:
            if col in state.cs_data.columns:
                issns = state.cs_data[col].dropna().astype(str)
                for issn in issns:
                    normalized = normalize_issn_for_comparison(issn)
                    if normalized and len(normalized) == 8:
                        scopus_issn_cache.add(normalized)
        print(f"✅ Scopus cache built: {len(scopus_issn_cache)} ISSNs")
    
    # Кэш для WoS (IF.xlsx)
    wos_issn_cache = set()
    if not state.if_data.empty:
        print("🔍 Building WoS ISSN cache...")
        for col in ['ISSN', 'eISSN']:
            if col in state.if_data.columns:
                issns = state.if_data[col].dropna().astype(str)
                for issn in issns:
                    normalized = normalize_issn_for_comparison(issn)
                    if normalized and len(normalized) == 8:
                        wos_issn_cache.add(normalized)
        print(f"✅ WoS cache built: {len(wos_issn_cache)} ISSNs")
    
    return scopus_issn_cache, wos_issn_cache

def get_all_issns_from_work(work):
    """Быстро извлекает все ISSN из работы"""
    issns = set()
    if not work:
        return issns
        
    cr = work.get('crossref')
    oa = work.get('openalex')
    
    if cr:
        cr_issns = cr.get('ISSN', [])
        if isinstance(cr_issns, str):
            cr_issns = [cr_issns]
        for issn in cr_issns:
            if issn:
                normalized = normalize_issn_for_comparison(issn)
                if normalized:
                    issns.add(normalized)
    
    if oa:
        host_venue = oa.get('host_venue', {})
        if host_venue:
            oa_issns = host_venue.get('issn', [])
            if isinstance(oa_issns, str):
                oa_issns = [oa_issns]
            for issn in oa_issns:
                if issn:
                    normalized = normalize_issn_for_comparison(issn)
                    if normalized:
                        issns.add(normalized)
    
    return issns

def calculate_special_analysis_metrics(analyzed_metadata, citing_metadata, state):
    """Calculate CiteScore and Impact Factor metrics for Special Analysis mode"""
    
    # Initialize metrics with default values
    special_metrics = {
        'cite_score': 0,
        'cite_score_corrected': 0,
        'impact_factor': 0,
        'impact_factor_corrected': 0,
        'debug_info': {}
    }
    
    # Check if we're in Special Analysis mode
    if not state.is_special_analysis:
        return special_metrics
    
    # Get current date for time window calculations
    current_date = datetime.now()
    
    # Define time windows for Special Analysis
    # CiteScore windows (1580 to 120 days ago)
    cs_start_date = current_date - timedelta(days=1580)
    cs_end_date = current_date - timedelta(days=120)
    
    # Impact Factor windows
    # Analyzed articles: 1265 to 535 days ago
    if_analyzed_start = current_date - timedelta(days=1265)
    if_analyzed_end = current_date - timedelta(days=535)
    
    # Citing works: 534 to 170 days ago  
    if_citing_start = current_date - timedelta(days=534)
    if_citing_end = current_date - timedelta(days=170)
    
    print(f"🔍 Special Analysis Date Windows:")
    print(f"   CiteScore: {cs_start_date.date()} to {cs_end_date.date()}")
    print(f"   IF Analyzed: {if_analyzed_start.date()} to {if_analyzed_end.date()}")
    print(f"   IF Citing: {if_citing_start.date()} to {if_citing_end.date()}")
    
    # Create ISSN lookup cache for fast searching - ИСПРАВЛЕННЫЙ ВЫЗОВ
    scopus_issn_cache, wos_issn_cache = create_issn_lookup_cache(state)
    print(f"📊 ISSN cache sizes - Scopus: {len(scopus_issn_cache)}, WoS: {len(wos_issn_cache)}")
    
    # Initialize counters
    B = 0  # Articles for CiteScore (published in CS window)
    A = 0  # All citations for CiteScore (COUNTING EACH CITATION)
    C = 0  # Citations from Scopus-indexed journals for CiteScore (COUNTING EACH CITATION)
    
    D = 0  # Articles for Impact Factor (published in IF window)
    E = 0  # All citations for Impact Factor (COUNTING EACH CITATION) 
    F = 0  # Citations from WoS-indexed journals for Impact Factor (COUNTING EACH CITATION)
    
    # Track which articles are used for metrics (for Excel reporting)
    analyzed_articles_usage = {}
    citing_articles_usage = {}  # NEW: Track citing articles usage
    
    # Detailed citation tracking - count each citation separately
    citation_details = {
        'cs_citations': [],  # List of (analyzed_doi, citing_doi, analyzed_date, citing_date) for CiteScore
        'cs_scopus_citations': [],  # List of (analyzed_doi, citing_doi, analyzed_date, citing_date) for Scopus-corrected CiteScore
        'if_citations': [],  # List of (analyzed_doi, citing_doi, analyzed_date, citing_date) for Impact Factor
        'if_wos_citations': []  # List of (analyzed_doi, citing_doi, analyzed_date, citing_date) for WoS-corrected Impact Factor
    }
    
    # Helper function to extract publication date from metadata
    def get_publication_date(metadata):
        """Extract publication date from metadata (Crossref or OpenAlex)"""
        if not metadata:
            return None
            
        # Try Crossref first
        cr = metadata.get('crossref')
        if cr:
            date_parts = cr.get('published', {}).get('date-parts', [[]])[0]
            if date_parts and len(date_parts) >= 1:
                try:
                    year = date_parts[0]
                    month = date_parts[1] if len(date_parts) > 1 else 1
                    day = date_parts[2] if len(date_parts) > 2 else 1
                    return datetime(year, month, day)
                except:
                    pass
        
        # Try OpenAlex
        oa = metadata.get('openalex')
        if oa and oa.get('publication_date'):
            try:
                return datetime.fromisoformat(oa['publication_date'].replace('Z', '+00:00'))
            except:
                pass
                
        return None
    
    # Step 1: Process analyzed articles for CiteScore (B) and Impact Factor (D)
    print(f"📊 Processing {len(analyzed_metadata)} analyzed articles...")
    
    for analyzed in analyzed_metadata:
        if not analyzed or not analyzed.get('crossref'):
            continue
            
        analyzed_doi = analyzed['crossref'].get('DOI')
        if not analyzed_doi:
            continue
            
        # Get publication date
        analyzed_pub_date = get_publication_date(analyzed)
        
        # Initialize usage tracking for this analyzed article
        analyzed_articles_usage[analyzed_doi] = {
            'used_for_sc': False,
            'used_for_if': False,
            'cs_citations_count': 0,  # Number of citations for CiteScore
            'if_citations_count': 0,  # Number of citations for Impact Factor
            'publication_date': analyzed_pub_date
        }
        
        # Check if this article should be used for CiteScore (B)
        if analyzed_pub_date and (cs_start_date <= analyzed_pub_date <= cs_end_date):
            B += 1
            analyzed_articles_usage[analyzed_doi]['used_for_sc'] = True
            print(f"✅ Article {analyzed_doi} included in CiteScore (published: {analyzed_pub_date.date()})")
        
        # Check if this article should be used for Impact Factor (D)
        if analyzed_pub_date and (if_analyzed_start <= analyzed_pub_date <= if_analyzed_end):
            D += 1
            analyzed_articles_usage[analyzed_doi]['used_for_if'] = True
            print(f"✅ Article {analyzed_doi} included in Impact Factor (published: {analyzed_pub_date.date()})")
    
    print(f"📈 Articles for CiteScore (B): {B}")
    print(f"📈 Articles for Impact Factor (D): {D}")
    
    # Step 2: Process citing works and citations - COUNT EACH CITATION SEPARATELY
    print(f"🔍 Processing citations for {len(analyzed_metadata)} analyzed articles...")
    
    total_citations_processed = 0
    
    for analyzed in analyzed_metadata:
        if not analyzed or not analyzed.get('crossref'):
            continue
            
        analyzed_doi = analyzed['crossref'].get('DOI')
        if not analyzed_doi:
            continue
            
        # Get analyzed article publication date
        analyzed_pub_date = get_publication_date(analyzed)
        if not analyzed_pub_date:
            continue
            
        # Get citing works for this analyzed article
        citings = state.citing_cache.get(analyzed_doi, [])
        
        for citing in citings:
            if not citing:
                continue
                
            citing_doi = citing.get('doi')
            if not citing_doi:
                continue
            
            total_citations_processed += 1
            
            # Initialize citing article usage tracking if not exists
            if citing_doi not in citing_articles_usage:
                citing_articles_usage[citing_doi] = {
                    'used_for_sc': True,  # или False в зависимости от условий
                    'used_for_sc_corr': True,  # или False  
                    'used_for_if': True,  # или False
                    'used_for_if_corr': True  # или False
                }
            
            # Get citing work publication date
            citing_pub_date = None
            citing_pub_date_str = citing.get('pub_date')
            if citing_pub_date_str:
                try:
                    citing_pub_date = datetime.fromisoformat(citing_pub_date_str.replace('Z', '+00:00'))
                except:
                    # Try to get from OpenAlex data
                    citing_pub_date = get_publication_date(citing)
            
            if not citing_pub_date:
                continue
            
            # CiteScore calculations (A and C) - COUNT EACH CITATION
            # BOTH analyzed article AND citing work must be in CiteScore period
            analyzed_in_cs = (cs_start_date <= analyzed_pub_date <= cs_end_date)
            citing_in_cs = (cs_start_date <= citing_pub_date <= cs_end_date)
            
            if analyzed_in_cs and citing_in_cs:
                # Count this citation for CiteScore
                A += 1
                analyzed_articles_usage[analyzed_doi]['cs_citations_count'] += 1
                citation_details['cs_citations'].append((analyzed_doi, citing_doi, analyzed_pub_date.date(), citing_pub_date.date()))
                citing_articles_usage[citing_doi]['used_for_sc'] = True  # NEW: Mark citing article for SC
                
                # FAST CHECK: Check if citing work is in Scopus using cache
                citing_issns = get_all_issns_from_work(citing)
                in_scopus = any(issn in scopus_issn_cache for issn in citing_issns)
                
                if in_scopus:
                    C += 1
                    citation_details['cs_scopus_citations'].append((analyzed_doi, citing_doi, analyzed_pub_date.date(), citing_pub_date.date()))
                    citing_articles_usage[citing_doi]['used_for_sc_corr'] = True  # NEW: Mark citing article for SC_corr
            
            # Impact Factor calculations (E and F) - COUNT EACH CITATION
            # Analyzed article in IF publication window, citing work in IF citation window
            analyzed_in_if_pub = (if_analyzed_start <= analyzed_pub_date <= if_analyzed_end)
            citing_in_if_cite = (if_citing_start <= citing_pub_date <= if_citing_end)
            
            if analyzed_in_if_pub and citing_in_if_cite:
                # Count this citation for Impact Factor
                E += 1
                analyzed_articles_usage[analyzed_doi]['if_citations_count'] += 1
                citation_details['if_citations'].append((analyzed_doi, citing_doi, analyzed_pub_date.date(), citing_pub_date.date()))
                citing_articles_usage[citing_doi]['used_for_if'] = True  # NEW: Mark citing article for IF
                
                # FAST CHECK: Check if citing work is in WoS using cache
                citing_issns = get_all_issns_from_work(citing)
                in_wos = any(issn in wos_issn_cache for issn in citing_issns)
                
                if in_wos:
                    F += 1
                    citation_details['if_wos_citations'].append((analyzed_doi, citing_doi, analyzed_pub_date.date(), citing_pub_date.date()))
                    citing_articles_usage[citing_doi]['used_for_if_corr'] = True  # NEW: Mark citing article for IF_corr
    
    print(f"📊 Citation Processing Complete:")
    print(f"   Total citations processed: {total_citations_processed}")
    print(f"   CiteScore: A={A}, C={C}, B={B}")
    print(f"   Impact Factor: E={E}, F={F}, D={D}")
    
    # Calculate final metrics
    special_metrics['cite_score'] = round(A / B, 2) if B > 0 else 0
    special_metrics['cite_score_corrected'] = round(C / B, 2) if B > 0 else 0
    special_metrics['impact_factor'] = round(E / D, 2) if D > 0 else 0
    special_metrics['impact_factor_corrected'] = round(F / D, 2) if D > 0 else 0
    
    # Store debug information
    special_metrics['debug_info'] = {
        'B': B,
        'A': A, 
        'C': C,
        'D': D,
        'E': E,
        'F': F,
        'analyzed_articles_usage': analyzed_articles_usage,
        'citing_articles_usage': citing_articles_usage,  # NEW: Include citing articles usage
        'citation_details': citation_details,
        'total_cs_citations': len(citation_details['cs_citations']),
        'total_cs_scopus_citations': len(citation_details['cs_scopus_citations']),
        'total_if_citations': len(citation_details['if_citations']),
        'total_if_wos_citations': len(citation_details['if_wos_citations']),
        'total_citations_processed': total_citations_processed,
        'scopus_cache_size': len(scopus_issn_cache),
        'wos_cache_size': len(wos_issn_cache)
    }
    
    print(f"🎯 Final Metrics:")
    print(f"   CiteScore: {special_metrics['cite_score']} (Corrected: {special_metrics['cite_score_corrected']})")
    print(f"   Impact Factor: {special_metrics['impact_factor']} (Corrected: {special_metrics['impact_factor_corrected']})")
    
    return special_metrics

# === NEW FUNCTIONS FOR COMBINED SHEETS ===

def search_ror_organization(affiliation_name):
    """Search for organization in ROR database and return best match with improved matching"""
    try:
        if not affiliation_name or affiliation_name.strip() == '':
            return None, None
            
        print(f"🔍 Searching ROR for: '{affiliation_name}'")
        
        # Search ROR API
        url = "https://api.ror.org/organizations"
        params = {'query': affiliation_name.strip()}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        items = response.json().get('items', [])
        print(f"📊 Found {len(items)} potential matches")
        
        if not items:
            return None, None
        
        # Find best match using improved fuzzy matching
        best_match = None
        best_score = -1
        
        query_lower = affiliation_name.strip().lower()
        
        for i, item in enumerate(items):
            name = item.get('name', '').lower()
            aliases = [a.lower() for a in item.get('aliases', [])]
            acronyms = [a.lower() for a in item.get('acronyms', []) if a]
            
            # All possible name variations
            all_names = [name] + aliases + acronyms
            
            # Calculate score for each name variation
            for test_name in all_names:
                score = 0
                
                # Exact match
                if query_lower == test_name:
                    score = 10000
                # Contains query
                elif query_lower in test_name:
                    score = 8000
                # Query contains organization name
                elif test_name in query_lower:
                    score = 7000
                # Fuzzy matching
                else:
                    try:
                        from thefuzz import fuzz
                        score = fuzz.token_set_ratio(query_lower, test_name)
                        # Boost score for longer matches
                        if len(test_name) > 10:
                            score = int(score * 1.1)
                    except ImportError:
                        # Fallback simple matching
                        common_words = len(set(query_lower.split()) & set(test_name.split()))
                        score = common_words * 20
                
                # Additional scoring based on organization type
                org_type = item.get('types', [])
                if any(t in ['Education', 'University', 'Institute'] for t in org_type):
                    score += 100
                
                if score > best_score:
                    best_score = score
                    best_match = item
                    print(f"🎯 New best match: {name} (score: {score})")
        
        print(f"🏆 Best match selected: {best_match.get('name') if best_match else 'None'} with score {best_score}")
        
        if best_match and best_score > 50:  # Minimum threshold
            # Extract ROR ID and website
            ror_id = best_match['id'].split('/')[-1]
            colab_url = f"https://colab.ws/organizations/{ror_id}"
            
            # Extract website
            website = None
            links = best_match.get('links', []) or []
            for link in links:
                if isinstance(link, dict):
                    url = link.get('value') or link.get('url')
                else:
                    url = str(link)
                    
                if url and isinstance(url, str):
                    url = url.strip()
                    if url.startswith('http'):
                        website = url
                        break
                    elif '.' in url:  # Likely a website
                        website = 'https://' + url
                        break
            
            print(f"✅ Found: Colab-ROR: {colab_url}, Website: {website}")
            return colab_url, website
        else:
            print(f"❌ No good match found (best score: {best_score})")
            return None, None
        
    except Exception as e:
        print(f"🚨 Error searching ROR for '{affiliation_name}': {str(e)}")
        return None, None

def search_ror_organization_cached(affiliation_name, cache_dict):
    """Cached version of ROR search to avoid duplicate API calls"""
    if not affiliation_name:
        return None, None
        
    # Use cache to avoid duplicate API calls
    cache_key = affiliation_name.strip().lower()
    
    if cache_key in cache_dict:
        return cache_dict[cache_key]
    
    # Perform search
    colab_ror, website = search_ror_organization(affiliation_name)
    
    # Cache the result
    cache_dict[cache_key] = (colab_ror, website)
    
    return colab_ror, website

# === NEW FUNCTION: PARALLEL ROR PROCESSING WITH PROGRESS BAR ===
def process_ror_data_parallel(affiliations_list, state):
    """Process ROR data for affiliations in parallel with progress bar"""
    if not state.include_ror_data:
        return {}
    
    print(f"🔍 Starting parallel ROR processing for {len(affiliations_list)} affiliations")
    
    # Progress bar setup
    ror_progress = st.progress(0)
    ror_status = st.empty()
    
    ror_results = {}
    processed_count = 0
    total_affiliations = len(affiliations_list)
    
    # Prepare arguments for parallel processing
    args_list = [(affiliation, state.ror_cache) for affiliation in affiliations_list]
    
    # Use 4 workers for ROR API to avoid overloading
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(search_ror_organization_cached, args[0], args[1]): args for args in args_list}
        
        for i, future in enumerate(as_completed(futures)):
            args = futures[future]
            affiliation_name = args[0]
            
            try:
                colab_ror, website = future.result()
                ror_results[affiliation_name] = (colab_ror, website)
                processed_count += 1
                
                # Update progress
                progress = (i + 1) / total_affiliations
                ror_progress.progress(progress)
                ror_status.text(f"🔍 Processing ROR data: {i + 1}/{total_affiliations}")
                
            except Exception as e:
                print(f"⚠️ Error processing ROR for '{affiliation_name}': {str(e)}")
                ror_results[affiliation_name] = (None, None)
                processed_count += 1
    
    ror_progress.empty()
    ror_status.empty()
    
    print(f"✅ ROR processing completed: {processed_count}/{total_affiliations} affiliations processed")
    return ror_results
    
def create_combined_authors_sheet(analyzed_authors_data, citing_authors_data, analyzed_total_articles, citing_total_articles):
    """Создает объединенный лист авторов анализируемых и цитирующих статей"""
    
    # Нормализуем имена авторов и объединяем счетчики
    def normalize_and_aggregate(authors_list):
        normalized_counts = Counter()
        for author, count in authors_list:
            normalized_name = normalize_author_name(author)
            normalized_counts[normalized_name] += count
        return normalized_counts
    
    analyzed_authors = normalize_and_aggregate(analyzed_authors_data)
    citing_authors = normalize_and_aggregate(citing_authors_data)
    
    combined_data = []
    all_authors = set(analyzed_authors.keys()) | set(citing_authors.keys())
    
    for author in all_authors:
        analyzed_count = analyzed_authors.get(author, 0)
        citing_count = citing_authors.get(author, 0)
        total_publications = analyzed_count + citing_count
        
        # Рассчитываем проценты
        analyzed_pct = (analyzed_count / analyzed_total_articles * 100) if analyzed_total_articles > 0 else 0
        citing_pct = (citing_count / citing_total_articles * 100) if citing_total_articles > 0 else 0
        
        # Определяем статус автора
        if analyzed_count > 0 and citing_count > 0:
            author_status = "Both"
        elif analyzed_count > 0:
            author_status = "Analyzed Only"
        else:
            author_status = "Citing Only"
        
        # Рассчитываем Loyalty Score (процент публикаций от общей активности)
        loyalty_score_pct = (analyzed_count / total_publications * 100) if total_publications > 0 else 0
        
        # Определяем Activity Balance
        if author_status == "Analyzed Only":
            activity_balance = "Publishing-Only"
        elif author_status == "Citing Only":
            activity_balance = "Citing-Only"
        elif loyalty_score_pct >= 70:
            activity_balance = "Publishing-Heavy"
        elif loyalty_score_pct >= 30:
            activity_balance = "Balanced"
        else:
            activity_balance = "Citing-Heavy"
        
        combined_data.append({
            'Author': author,
            'Total': total_publications,
            'Status': author_status,
            'Analyzed_Count': analyzed_count,
            'Citing_Count': citing_count,
            'Loyalty_Score': f"{loyalty_score_pct:.1f}%",
            'Activity_Balance': activity_balance,
            'Analyzed_Pct': round(analyzed_pct, 2),
            'Citing_Pct': round(citing_pct, 2)
        })
    
    # Сортируем по общему количеству публикаций (убывание)
    combined_data.sort(key=lambda x: x['Total'], reverse=True)
    
    return combined_data

def create_combined_affiliations_sheet(analyzed_affiliations_data, citing_affiliations_data, analyzed_total_mentions, citing_total_mentions, state):
    """Создает объединенный лист аффилиаций анализируемых и цитирующих статей"""
    
    analyzed_affiliations = Counter(dict(analyzed_affiliations_data))
    citing_affiliations = Counter(dict(citing_affiliations_data))
    
    combined_data = []
    all_affiliations = set(analyzed_affiliations.keys()) | set(citing_affiliations.keys())
    
    # NEW: Process ROR data in parallel if enabled
    ror_results = {}
    if state.include_ror_data and hasattr(state, 'ror_cache'):
        try:
            affiliations_list = list(all_affiliations)
            ror_results = process_ror_data_parallel(affiliations_list, state)
        except Exception as e:
            print(f"Warning: ROR data processing failed: {e}")
            ror_results = {}
    
    for affiliation in all_affiliations:
        analyzed_count = analyzed_affiliations.get(affiliation, 0)
        citing_count = citing_affiliations.get(affiliation, 0)
        total_mentions = analyzed_count + citing_count
        
        # Рассчитываем проценты
        analyzed_pct = (analyzed_count / analyzed_total_mentions * 100) if analyzed_total_mentions > 0 else 0
        citing_pct = (citing_count / citing_total_mentions * 100) if citing_total_mentions > 0 else 0
        
        # Определяем статус аффилиации
        if analyzed_count > 0 and citing_count > 0:
            affiliation_status = "Both"
        elif analyzed_count > 0:
            affiliation_status = "Analyzed Only"
        else:
            affiliation_status = "Citing Only"
        
        # Рассчитываем Engagement Score (процент публикаций от общей активности)
        engagement_score_pct = (analyzed_count / total_mentions * 100) if total_mentions > 0 else 0
        
        # Определяем Activity Balance
        if affiliation_status == "Analyzed Only":
            activity_balance = "Publishing-Only"
        elif affiliation_status == "Citing Only":
            activity_balance = "Citing-Only"
        elif engagement_score_pct >= 70:
            activity_balance = "Publishing-Heavy"
        elif engagement_score_pct >= 30:
            activity_balance = "Balanced"
        else:
            activity_balance = "Citing-Heavy"
        
        # NEW: Get ROR information from cache or API results
        colab_ror = ""
        website = ""
        if state.include_ror_data and hasattr(state, 'ror_cache'):
            if affiliation in ror_results:
                colab_ror, website = ror_results[affiliation]
            else:
                # Fallback to direct search if not in results
                try:
                    colab_ror, website = search_ror_organization_cached(affiliation, state.ror_cache)
                except Exception as e:
                    print(f"Warning: ROR search failed for {affiliation}: {e}")
        
        combined_data.append({
            'Affiliation': affiliation,
            'Colab-ROR': colab_ror if colab_ror else '',
            'Website': website if website else '',
            'Total': total_mentions,
            'Status': affiliation_status,
            'Analyzed_Count': analyzed_count,
            'Citing_Count': citing_count,
            'Engagement_Score': f"{engagement_score_pct:.1f}%",
            'Activity_Balance': activity_balance,
            'Analyzed_Pct': round(analyzed_pct, 2),
            'Citing_Pct': round(citing_pct, 2)
        })
    
    # Сортируем по общему количеству упоминаний (убывание)
    combined_data.sort(key=lambda x: x['Total'], reverse=True)
    
    return combined_data

def create_combined_countries_sheet(analyzed_countries_data, citing_countries_data, analyzed_total_mentions, citing_total_mentions):
    """Создает объединенный лист стран анализируемых и цитирующих статей"""
    
    analyzed_countries = Counter(dict(analyzed_countries_data))
    citing_countries = Counter(dict(citing_countries_data))
    
    combined_data = []
    all_countries = set(analyzed_countries.keys()) | set(citing_countries.keys())
    
    for country in all_countries:
        analyzed_count = analyzed_countries.get(country, 0)
        citing_count = citing_countries.get(country, 0)
        total_mentions = analyzed_count + citing_count
        
        # Рассчитываем проценты
        analyzed_pct = (analyzed_count / analyzed_total_mentions * 100) if analyzed_total_mentions > 0 else 0
        citing_pct = (citing_count / citing_total_mentions * 100) if citing_total_mentions > 0 else 0
        
        # Определяем статус страны
        if analyzed_count > 0 and citing_count > 0:
            country_status = "Both"
        elif analyzed_count > 0:
            country_status = "Analyzed Only"
        else:
            country_status = "Citing Only"
        
        # Рассчитываем Self-Sufficiency (доля локальной активности)
        self_sufficiency_pct = (analyzed_count / total_mentions * 100) if total_mentions > 0 else 0
        
        # Рассчитываем Global Reach (доля международной активности)
        global_reach_pct = (citing_count / total_mentions * 100) if total_mentions > 0 else 0
        
        combined_data.append({
            'Country': country,
            'Total': total_mentions,
            'Status': country_status,
            'Analyzed_Count': analyzed_count,
            'Citing_Count': citing_count,
            'Self_Sufficiency': f"{self_sufficiency_pct:.1f}%",
            'Global_Reach': f"{global_reach_pct:.1f}%",
            'Analyzed_Pct': round(analyzed_pct, 2),
            'Citing_Pct': round(citing_pct, 2)
        })
    
    # Сортируем по общему количеству упоминаний (убывание)
    combined_data.sort(key=lambda x: x['Total'], reverse=True)
    
    return combined_data

# === NEW FUNCTIONS FOR AUTHOR ID DATA ===

def format_author_name_from_raw(raw_name):
    """Из любого raw_author_name делает полное имя: Sabirov Denis или Agliullin Marat"""
    if not raw_name:
        return "Unknown Author"
    
    # Убираем лишние пробелы и запятые
    name = re.sub(r'\s+', ' ', raw_name.strip().replace(',', ' '))
    parts = name.split()
    
    if len(parts) == 1:
        return parts[0]  # только фамилия
    
    # Фамилия — всегда последняя часть
    family = parts[-1]
    
    # Имя — все части кроме последней, объединяем пробелами
    given_names = ' '.join(parts[:-1])
    
    return f"{family} {given_names}"

def extract_clean_authors_from_work(data):
    """Извлекает авторов из данных OpenAlex в формате Фамилия Имя с аффилиацией"""
    authors = []
    for auth in data.get('authorships', []):
        raw_name = auth.get('raw_author_name')
        if not raw_name:
            continue
            
        name = format_author_name_from_raw(raw_name)
        
        # Аффилиация — только название учреждения, без страны
        aff = "No affiliation"
        for inst in auth.get('institutions', []):
            if inst and inst.get('display_name'):
                aff = inst['display_name']
                break  # берём только первую
        
        # Разделяем имя на фамилию и имя для поиска
        name_parts = name.split()
        surname = name_parts[0] if name_parts else ""
        given_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        authors.append({
            'name': name,
            'surname': surname,
            'given_name': given_name,
            'affiliation': aff
        })
    
    return authors

def get_work_by_doi(doi):
    """Получает данные работы по DOI из OpenAlex"""
    doi = doi.strip()
    url = f"https://api.openalex.org/works/https://doi.org/{doi}"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json()
    except:
        return None

def search_orcid_author(surname, given_name, affiliation):
    """Поиск автора в ORCID API по фамилии, имени и аффилиации - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    try:
        if not surname or not surname.strip():
            return None, None, None
            
        print(f"🔍 ORCID Search: {surname} {given_name}, Affiliation: {affiliation}")
        
        # Формируем поисковый запрос
        query_parts = [f"family-name:{surname.strip()}"]
        
        if given_name and given_name.strip():
            # Используем полное имя вместо инициала
            clean_given_name = given_name.strip()
            query_parts.append(f"given-names:{clean_given_name}")
        
        if affiliation and affiliation.strip():
            # Используем более широкий поиск по аффилиации
            query_parts.append(f'affiliation-org-name:"{affiliation.strip()}"')
        
        query = " AND ".join(query_parts)
        url = f"https://pub.orcid.org/v3.0/search/?q={quote(query)}"
        
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'JournalAnalysisTool/1.0'
        }
        
        print(f"📡 ORCID API Request: {url}")
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            num_results = data.get('num-found', 0)
            print(f"✅ ORCID API Response: {num_results} results found")
            
            if num_results > 0:
                # Берем первый (наиболее релевантный) результат
                result = data['result'][0]
                orcid_id = result.get('orcid-identifier', {}).get('path')
                
                if orcid_id:
                    print(f"🎯 Found ORCID: {orcid_id}")
                    
                    # Получаем подробную информацию для Scopus и WoS ID
                    orcid_url, scopus_id, wos_id = get_detailed_orcid_info(orcid_id)
                    return orcid_url, scopus_id, wos_id
            else:
                print("❌ No results found in ORCID")
        else:
            print(f"❌ ORCID API Error: {response.status_code} - {response.text}")
            
        return None, None, None
        
    except Exception as e:
        print(f"🚨 Error searching ORCID for {surname} {given_name}: {str(e)}")
        return None, None, None

def get_detailed_orcid_info(orcid_id):
    """Получает подробную информацию из профиля ORCID включая Scopus и WoS ID"""
    try:
        orcid_url = f"https://orcid.org/{orcid_id}"
        scopus_id = None
        wos_id = None
        
        # Получаем person данные
        person_url = f"https://pub.orcid.org/v3.0/{orcid_id}/person"
        headers = {'Accept': 'application/json', 'User-Agent': 'JournalAnalysisTool/1.0'}
        
        response = requests.get(person_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            person_data = response.json()
            
            # Ищем внешние идентификаторы
            external_ids = person_data.get('external-identifiers', {}).get('external-identifier', [])
            
            for ext_id in external_ids:
                ext_id_type = ext_id.get('external-id-type', '')
                ext_id_value = ext_id.get('external-id-value', '')
                
                if not ext_id_value:
                    continue
                    
                if ext_id_type.upper() in ['SCOPUS', 'SCOPUS AUTHOR ID']:
                    scopus_id = f"https://www.scopus.com/authid/detail.uri?authorId={ext_id_value}"
                    print(f"🔍 Found Scopus ID: {scopus_id}")
                    
                elif ext_id_type.upper() in ['RESEARCHERID', 'WOS']:
                    wos_id = f"https://www.webofscience.com/wos/author/record/{ext_id_value}"
                    print(f"🔍 Found WoS ID: {wos_id}")
            
            # Дополнительная проверка для Researcher URLs
            researcher_urls = person_data.get('researcher-urls', {}).get('researcher-url', [])
            for url_data in researcher_urls:
                url_value = url_data.get('url', {}).get('value', '')
                if 'scopus' in url_value.lower() and 'authorId' in url_value:
                    scopus_id = url_value
                elif 'researcherid' in url_value.lower() or 'webofscience' in url_value.lower():
                    wos_id = url_value
        
        print(f"✅ Detailed info - ORCID: {orcid_url}, Scopus: {scopus_id}, WoS: {wos_id}")
        return orcid_url, scopus_id, wos_id
        
    except Exception as e:
        print(f"🚨 Error getting detailed ORCID info: {str(e)}")
        return f"https://orcid.org/{orcid_id}", None, None

def search_orcid_author_cached(surname, given_name, affiliation, cache_dict):
    """Кэшированная версия поиска автора в ORCID - ИСПРАВЛЕННАЯ"""
    if not surname or not surname.strip():
        return None, None, None
        
    cache_key = f"{surname}_{given_name}_{affiliation}".lower().strip()
    
    if cache_key in cache_dict:
        print(f"📦 Using cached result for {cache_key}")
        return cache_dict[cache_key]
    
    # Выполняем поиск
    orcid_id, scopus_id, wos_id = search_orcid_author(surname, given_name, affiliation)
    
    # Кэшируем результат (даже если None)
    cache_dict[cache_key] = (orcid_id, scopus_id, wos_id)
    
    return orcid_id, scopus_id, wos_id

def process_author_id_data_parallel(author_list, state):
    """Обработка данных авторов в параллельном режиме - УЛУЧШЕННАЯ ВЕРСИЯ"""
    if not state.include_author_id_data:
        return []
    
    if not author_list:
        print("❌ No authors to process")
        return []
    
    print(f"🔍 Starting parallel Author ID processing for {len(author_list)} authors")
    
    # Прогресс-бар
    author_progress = st.progress(0)
    author_status = st.empty()
    
    results = []
    processed_count = 0
    total_authors = len(author_list)
    
    # Подготавливаем аргументы для параллельной обработки
    args_list = []
    for author in author_list:
        surname = author.get('surname', '').strip()
        given_name = author.get('given_name', '').strip()
        affiliation = author.get('affiliation', '').strip()
        
        if surname:  # Только авторы с фамилией
            args_list.append((surname, given_name, affiliation, state.author_id_cache))
    
    if not args_list:
        print("❌ No valid authors to process")
        author_progress.empty()
        author_status.empty()
        return []
    
    # Используем меньше рабочих потоков для избежания rate limiting
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        
        for i, args in enumerate(args_list):
            future = executor.submit(search_orcid_author_cached, args[0], args[1], args[2], args[3])
            futures[future] = i
        
        for i, future in enumerate(as_completed(futures)):
            author_index = futures[future]
            author_data = author_list[author_index]
            
            try:
                orcid_id, scopus_id, wos_id = future.result()
                
                # Создаем запись с полной информацией об авторе
                result_entry = {
                    'Full Name': author_data['full_name'],
                    'Surname': author_data['surname'],
                    'Given Name': author_data['given_name'],
                    'Affiliation': author_data['affiliation'],
                    '.': '.',  # Точка в пустой колонке
                    'ORCID ID': orcid_id if orcid_id else '',
                    'Scopus ID': scopus_id if scopus_id else '',
                    'WoS ID': wos_id if wos_id else '',
                    'Sources': ', '.join(author_data['sources']),
                    'All Affiliations': '; '.join(author_data['all_affiliations']) if author_data['all_affiliations'] else 'No affiliation'
                }
                
                results.append(result_entry)
                processed_count += 1
                
                # Обновляем прогресс
                progress = (i + 1) / len(args_list)
                author_progress.progress(progress)
                author_status.text(f"🔍 Processing Author ID data: {i + 1}/{len(args_list)}")
                
                # Добавляем небольшую задержку для избежания rate limiting
                time.sleep(0.2)
                
            except Exception as e:
                print(f"⚠️ Error processing author {author_data['surname']} {author_data['given_name']}: {str(e)}")
                # Добавляем запись с ошибкой (но без ID)
                results.append({
                    'Full Name': author_data['full_name'],
                    'Surname': author_data['surname'],
                    'Given Name': author_data['given_name'],
                    'Affiliation': author_data['affiliation'],
                    '.': '.',
                    'ORCID ID': '',
                    'Scopus ID': '',
                    'WoS ID': '',
                    'Sources': ', '.join(author_data['sources']),
                    'All Affiliations': '; '.join(author_data['all_affiliations']) if author_data['all_affiliations'] else 'No affiliation'
                })
                processed_count += 1
    
    author_progress.empty()
    author_status.empty()
    
    print(f"✅ Author ID processing completed: {processed_count}/{total_authors} authors processed")
    
    # Логируем статистику
    found_orcid = sum(1 for r in results if r['ORCID ID'] != '')
    found_scopus = sum(1 for r in results if r['Scopus ID'] != '') 
    found_wos = sum(1 for r in results if r['WoS ID'] != '')
    
    print(f"📊 Results - ORCID: {found_orcid}, Scopus: {found_scopus}, WoS: {found_wos}")
    
    return results

def extract_unique_authors_from_metadata(analyzed_metadata, citing_metadata, state):
    """Извлекает уникальных авторов из метаданных анализируемых и цитирующих статей с объединением аффилиаций"""
    author_records = {}  # ключ: "Фамилия Имя", значение: список аффилиаций
    
    def process_metadata(metadata_list, source_type):
        """Обрабатывает метаданные и добавляет авторов в общую коллекцию"""
        for meta in metadata_list:
            if not meta or not meta.get('openalex'):
                continue
                
            doi = meta.get('doi')
            if not doi:
                continue
                
            # Получаем данные работы
            work_data = get_work_by_doi(doi)
            if not work_data:
                continue
                
            # Извлекаем авторов
            authors = extract_clean_authors_from_work(work_data)
            for author in authors:
                author_name = author['name']
                affiliation = author['affiliation']
                
                if author_name not in author_records:
                    author_records[author_name] = {
                        'surname': author['surname'],
                        'given_name': author['given_name'],
                        'affiliations': set(),
                        'sources': set()
                    }
                
                # Добавляем аффилиацию (если есть)
                if affiliation and affiliation != "No affiliation":
                    author_records[author_name]['affiliations'].add(affiliation)
                
                # Отмечаем источник
                author_records[author_name]['sources'].add(source_type)
    
    # Обрабатываем анализируемые статьи
    print("🔍 Processing analyzed articles for authors...")
    process_metadata(analyzed_metadata, 'analyzed')
    
    # Обрабатываем цитирующие статьи
    print("🔍 Processing citing articles for authors...")
    process_metadata(citing_metadata, 'citing')
    
    # Преобразуем в список с выбором лучшей аффилиации
    author_list = []
    
    for author_name, data in author_records.items():
        affiliations_list = list(data['affiliations'])
        
        # Выбираем лучшую аффилиацию по приоритету:
        # 1. Аффилиация из анализируемых статей
        # 2. Первая аффилиация из цитирующих статей  
        # 3. "No affiliation" если ничего нет
        
        best_affiliation = "No affiliation"
        if affiliations_list:
            # Если автор есть в анализируемых статьях, предпочитаем его аффилиации
            if 'analyzed' in data['sources']:
                # Ищем аффилиации из анализируемых статей
                analyzed_affiliations = set()
                # Для этого нужно проверить исходные данные, но в упрощенной версии берем первую
                best_affiliation = affiliations_list[0]
            else:
                # Только цитирующие статьи - берем первую аффилиацию
                best_affiliation = affiliations_list[0]
        
        author_list.append({
            'surname': data['surname'],
            'given_name': data['given_name'],
            'full_name': author_name,
            'affiliation': best_affiliation,
            'all_affiliations': affiliations_list,  # сохраняем все аффилиации для отладки
            'sources': list(data['sources'])
        })
    
    # Сортируем по фамилии для удобства
    author_list.sort(key=lambda x: x['surname'])
    
    print(f"📊 Extracted {len(author_list)} unique authors from metadata")
    print(f"   - With affiliations: {len([a for a in author_list if a['affiliation'] != 'No affiliation'])}")
    print(f"   - From analyzed articles: {len([a for a in author_list if 'analyzed' in a['sources']])}")
    print(f"   - From citing articles: {len([a for a in author_list if 'citing' in a['sources']])}")
    print(f"   - From both sources: {len([a for a in author_list if len(a['sources']) > 1])}")
    
    return author_list

def create_author_id_sheet(analyzed_metadata, citing_metadata, state):
    """Создает лист Author_ID_data с данными об идентификаторах авторов"""
    if not state.include_author_id_data:
        return []
    
    # Извлекаем уникальных авторов с объединением данных
    unique_authors = extract_unique_authors_from_metadata(analyzed_metadata, citing_metadata, state)
    
    if not unique_authors:
        st.info("No authors found for Author ID data processing.")
        return []
    
    # Показываем статистику
    st.info(f"📊 Found {len(unique_authors)} unique authors for ID processing")
    
    # Обрабатываем данные авторов
    author_id_data = process_author_id_data_parallel(unique_authors, state)
    
    # Создаем финальный DataFrame с нужными колонками
    final_columns = [
        'Full Name', 
        'Surname', 
        'Given Name', 
        'Affiliation', 
        '.', 
        'ORCID ID', 
        'Scopus ID', 
        'WoS ID'
    ]
    
    # Фильтруем только нужные колонки для итогового листа
    final_data = []
    for record in author_id_data:
        final_record = {col: record[col] for col in final_columns}
        final_data.append(final_record)
    
    return final_data

# === 17. Enhanced Excel Report Creation ===
def precompute_excel_data(analyzed_data, citing_data, analyzed_stats, citing_stats, enhanced_stats, citation_timing, overlap_details, fast_metrics, additional_data, state):
    """Предварительный расчет всех данных для Excel отчетов"""
    
    print("🔍 Precomputing data for Excel generation...")
    
    # Предварительно извлекаем все данные и кэшируем
    analyzed_precomputed = []
    for item in analyzed_data:
        if item and item.get('crossref'):
            cr = item['crossref']
            oa = item.get('openalex', {})
            
            # Используем кэшированные функции
            article_data = cached_extract_article_data({'openalex': oa})
            journal_info = cached_extract_journal_info(item)
            
            analyzed_precomputed.append({
                'cr': cr,
                'oa': oa,
                'article_data': article_data,
                'journal_info': journal_info,
                'doi': cr.get('DOI', '')
            })
    
    citing_precomputed = []
    for item in citing_data:
        if item and item.get('crossref'):
            cr = item['crossref']
            oa = item.get('openalex', {})
            
            article_data = cached_extract_article_data({'openalex': oa})
            journal_info = cached_extract_journal_info(item)
            
            citing_precomputed.append({
                'cr': cr,
                'oa': oa, 
                'article_data': article_data,
                'journal_info': journal_info,
                'doi': cr.get('DOI', '')
            })
    
    # Предварительно вычисляем usage данные для Special Analysis
    special_metrics = additional_data.get('special_analysis_metrics', {})
    analyzed_articles_usage = special_metrics.get('debug_info', {}).get('analyzed_articles_usage', {})
    citing_articles_usage = special_metrics.get('debug_info', {}).get('citing_articles_usage', {})
    
    return {
        'analyzed_precomputed': analyzed_precomputed,
        'citing_precomputed': citing_precomputed,
        'analyzed_articles_usage': analyzed_articles_usage,
        'citing_articles_usage': citing_articles_usage
    }

def create_enhanced_excel_report(analyzed_data, citing_data, analyzed_stats, citing_stats, enhanced_stats, citation_timing, overlap_details, fast_metrics, excel_buffer, additional_data):
    """Create enhanced Excel report with error handling for large data"""
    
    # ДОБАВИТЬ В НАЧАЛО ФУНКЦИИ:
    state = get_analysis_state()
    precomputed_data = precompute_excel_data(
        analyzed_data, citing_data, analyzed_stats, citing_stats, 
        enhanced_stats, citation_timing, overlap_details, fast_metrics, 
        additional_data, state
    )
    
    analyzed_precomputed = precomputed_data['analyzed_precomputed']
    citing_precomputed = precomputed_data['citing_precomputed']
    analyzed_articles_usage = precomputed_data['analyzed_articles_usage']
    citing_articles_usage = precomputed_data['citing_articles_usage']
    
    def safe_convert(value):
        """Safely convert numpy types to Python native types"""
        if value is None:
            return 0
        if hasattr(value, 'item'):
            return value.item()
        elif isinstance(value, (np.integer, np.int32, np.int64)):
            return int(value)
        elif isinstance(value, (np.floating, np.float32, np.float64)):
            return float(value)
        elif isinstance(value, np.bool_):
            return bool(value)
        return value

    def safe_join(items, sep='; ', max_len=None):
        """Safely join list, filtering None and applying length limit"""
        if not items:
            return ''
        cleaned = [str(x).strip() for x in items if x is not None and str(x).strip()]
        result = sep.join(cleaned)
        return result[:max_len] if max_len else result
            
    try:
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            # Sheet 1: Analyzed articles (with optimization)
            analyzed_list = []
            MAX_ROWS = 50000
            
            # ИСПОЛЬЗУЕМ ПРЕДВАРИТЕЛЬНО ВЫЧИСЛЕННЫЕ ДАННЫЕ
            for i, precomputed in enumerate(analyzed_precomputed):
                if i >= MAX_ROWS:
                    break
                    
                cr = precomputed['cr']
                article_data = precomputed['article_data']
                journal_info = precomputed['journal_info']
                
                analyzed_doi = cr.get('DOI', '')
                usage_info = analyzed_articles_usage.get(analyzed_doi, {})
                
                analyzed_list.append({
                    'DOI': safe_convert(cr.get('DOI', ''))[:100],
                    'Title': (cr.get('title', [''])[0] if cr.get('title') else 'No title')[:200],
                    'Authors_Crossref': safe_join([f"{a.get('given', '')} {a.get('family', '')}".strip() for a in cr.get('author', []) if a.get('given') or a.get('family')])[:300],
                    'Authors_OpenAlex': safe_join(article_data['authors'])[:300],  # ИЗ КЭША
                    'Affiliations': safe_join(article_data['affiliations'])[:500],  # ИЗ КЭША
                    'Countries': safe_join(article_data['countries'])[:100],  # ИЗ КЭША
                    'Publication_Year': safe_convert(cr.get('published', {}).get('date-parts', [[0]])[0][0]),
                    'Journal': safe_convert(journal_info['journal_name'])[:100],  # ИЗ КЭША
                    'Publisher': safe_convert(journal_info['publisher'])[:100],  # ИЗ КЭША
                    'ISSN': safe_join([str(issn) for issn in journal_info['issn'] if issn])[:50],  # ИЗ КЭША
                    'Reference_Count': safe_convert(cr.get('reference-count', 0)),
                    'Citations_Crossref': safe_convert(cr.get('is-referenced-by-count', 0)),
                    'Citations_OpenAlex': safe_convert(precomputed['oa'].get('cited_by_count', 0)) if precomputed['oa'] else 0,
                    'Author_Count': safe_convert(len(cr.get('author', []))),
                    'Work_Type': safe_convert(cr.get('type', ''))[:50],
                    'Used for SC': '×' if usage_info.get('used_for_sc') else '',
                    'Used for IF': '×' if usage_info.get('used_for_if') else ''
                })
            
            # Get special analysis metrics if available
            state = get_analysis_state()
            special_metrics = additional_data.get('special_analysis_metrics', {})
            analyzed_articles_usage = special_metrics.get('debug_info', {}).get('analyzed_articles_usage', {})
                        
            if analyzed_list:
                analyzed_df = pd.DataFrame(analyzed_list)
                analyzed_df.to_excel(writer, sheet_name='Analyzed_Articles', index=False)

            # Sheet 2: Citing works (with optimization) - UPDATED WITH 4 NEW COLUMNS
            citing_list = []
            
            # Get citing articles usage from special analysis metrics - FIXED LOGIC
            citing_usage_dict = {}
            if 'special_analysis_metrics' in additional_data:
                debug_info = additional_data['special_analysis_metrics'].get('debug_info', {})
                citing_usage_dict = debug_info.get('citing_articles_usage', {})
                print(f"🔍 DEBUG: Loaded citing_usage_dict with {len(citing_usage_dict)} entries for Citing_Works sheet")
            
            for i, item in enumerate(citing_data):
                if i >= MAX_ROWS:
                    break
                if item and item.get('crossref'):
                    cr = item['crossref']
                    oa = item.get('openalex', {})
                    authors_list, affiliations_list, countries_list = extract_affiliations_and_countries(oa)
                    journal_info = extract_journal_info(item)
                    
                    citing_doi = cr.get('DOI', '')
                    
                    # FIXED: Properly extract usage information from citing_usage_dict
                    usage_info = citing_usage_dict.get(citing_doi, {})
                    
                    # Debug output for first few records
                    if i < 5 and citing_doi:
                        print(f"🔍 Citing_Works DEBUG - Item {i}: DOI={citing_doi}, usage_info={usage_info}")
                    
                    citing_list.append({
                        'DOI': safe_convert(cr.get('DOI', ''))[:100],
                        'Title': (cr.get('title', [''])[0] if cr.get('title') else 'No title')[:200],
                        'Authors_Crossref': safe_join([f"{a.get('given', '')} {a.get('family', '')}".strip() for a in cr.get('author', []) if a.get('given') or a.get('family')])[:300],
                        'Authors_OpenAlex': safe_join(authors_list)[:300],
                        'Affiliations': safe_join(affiliations_list)[:500],
                        'Countries': safe_join(countries_list)[:100],
                        'Publication_Year': safe_convert(cr.get('published', {}).get('date-parts', [[0]])[0][0]),
                        'Journal': safe_convert(journal_info['journal_name'])[:100],
                        'Publisher': safe_convert(journal_info['publisher'])[:100],
                        'ISSN': safe_join([str(issn) for issn in journal_info['issn'] if issn])[:50],
                        'Reference_Count': safe_convert(cr.get('reference-count', 0)),
                        'Citations_Crossref': safe_convert(cr.get('is-referenced-by-count', 0)),
                        'Citations_OpenAlex': safe_convert(oa.get('cited_by_count', 0)) if oa else 0,
                        'Author_Count': safe_convert(len(cr.get('author', []))),
                        'Work_Type': safe_convert(cr.get('type', ''))[:50],
                        # FIXED: 4 columns for special analysis usage - using proper dictionary access
                        'Used for SC': '×' if usage_info.get('used_for_sc') else '',
                        'Used for SC_corr': '×' if usage_info.get('used_for_sc_corr') else '',
                        'Used for IF': '×' if usage_info.get('used_for_if') else '',
                        'Used for IF_corr': '×' if usage_info.get('used_for_if_corr') else ''
                    })
            
            if citing_list:
                citing_df = pd.DataFrame(citing_list)
                citing_df.to_excel(writer, sheet_name='Citing_Works', index=False)

            # Sheet 3: Overlaps between analyzed and citing works
            overlap_list = []
            for overlap in overlap_details:
                overlap_list.append({
                    'Analyzed_DOI': safe_convert(overlap['analyzed_doi'])[:100],
                    'Citing_DOI': safe_convert(overlap['citing_doi'])[:100],
                    'Common_Authors': safe_join(overlap['common_authors'])[:300],
                    'Common_Authors_Count': safe_convert(overlap['common_authors_count']),
                    'Common_Affiliations': safe_join(overlap['common_affiliations'])[:500],
                    'Common_Affiliations_Count': safe_convert(overlap['common_affiliations_count'])
                })
            
            if overlap_list:
                overlap_df = pd.DataFrame(overlap_list)
                overlap_df.to_excel(writer, sheet_name='Work_Overlaps', index=False)

            # Sheet 4: Time to first citation (WITH EDITORIAL NOTES EXCLUDED)
            first_citation_list = []
            for detail in citation_timing.get('first_citation_details', []):
                # === EXCLUDE EDITORIAL NOTES ===
                # Skip records that are editorial notes (same prefix AND same date)
                if detail.get('is_editorial_note', False):
                    continue
                    
                # Normalize DOIs for consistent display
                analyzed_doi_normalized = normalize_doi(detail['analyzed_doi'])
                citing_doi_normalized = normalize_doi(detail['citing_doi'])
                
                first_citation_list.append({
                    'Analyzed_DOI': safe_convert(analyzed_doi_normalized)[:100],
                    'First_Citing_DOI': safe_convert(citing_doi_normalized)[:100],
                    'Publication_Date': detail['analyzed_date'].strftime('%Y-%m-%d') if detail['analyzed_date'] else 'N/A',
                    'First_Citation_Date': detail['first_citation_date'].strftime('%Y-%m-%d') if detail['first_citation_date'] else 'N/A',
                    'Days_to_First_Citation': safe_convert(detail['days_to_first_citation']),
                    'Same_DOI_Prefix': detail.get('same_prefix', False),
                    'Same_Publication_Date': detail.get('same_date', False),
                    'Editorial_Note_Excluded': detail.get('is_editorial_note', False)
                })
            
            if first_citation_list:
                first_citation_df = pd.DataFrame(first_citation_list)
                first_citation_df.to_excel(writer, sheet_name='First_Citations', index=False)

            # Sheet 5: Combined Statistics (NEW - объединенный лист)
            statistics_data = {
                'Metric': [
                    'Total Articles', 
                    'Total References', 
                    'References with DOI', 'References with DOI Count', 'References with DOI Percentage',
                    'References without DOI', 'References without DOI Count', 'References without DOI Percentage',
                    'Self-Citations', 'Self-Citations Count', 'Self-Citations Percentage',
                    'Single Author Articles',
                    'Articles with >10 Authors', 
                    'Minimum References', 
                    'Maximum References', 
                    'Average References',
                    'Median References', 
                    'Minimum Authors',
                    'Maximum Authors', 
                    'Average Authors',
                    'Median Authors', 
                    'Single Country Articles', 'Single Country Articles Percentage',
                    'Multiple Country Articles', 'Multiple Country Articles Percentage',
                    'No Country Data Articles', 'No Country Data Articles Percentage',
                    'Total Affiliations',
                    'Unique Affiliations', 
                    'Unique Countries',
                    'Unique Journals',
                    'Unique Publishers',
                    'Articles with ≥10 citations',
                    'Articles with ≥20 citations',
                    'Articles with ≥30 citations',
                    'Articles with ≥50 citations'
                ],
                'Value_Analyzed': [
                    safe_convert(analyzed_stats['n_items']),
                    safe_convert(analyzed_stats['total_refs']),
                    'References with DOI', safe_convert(analyzed_stats['refs_with_doi']), f"{safe_convert(analyzed_stats['refs_with_doi_pct']):.1f}%",
                    'References without DOI', safe_convert(analyzed_stats['refs_without_doi']), f"{safe_convert(analyzed_stats['refs_without_doi_pct']):.1f}%",
                    'Self-Citations', safe_convert(analyzed_stats['self_cites']), f"{safe_convert(analyzed_stats['self_cites_pct']):.1f}%",
                    safe_convert(analyzed_stats['single_authors']),
                    safe_convert(analyzed_stats['multi_authors_gt10']),
                    safe_convert(analyzed_stats['ref_min']),
                    safe_convert(analyzed_stats['ref_max']),
                    f"{safe_convert(analyzed_stats['ref_mean']):.1f}",
                    safe_convert(analyzed_stats['ref_median']),
                    safe_convert(analyzed_stats['auth_min']),
                    safe_convert(analyzed_stats['auth_max']),
                    f"{safe_convert(analyzed_stats['auth_mean']):.1f}",
                    safe_convert(analyzed_stats['auth_median']),
                    safe_convert(analyzed_stats['single_country_articles']), f"{safe_convert(analyzed_stats['single_country_pct']):.1f}%",
                    safe_convert(analyzed_stats['multi_country_articles']), f"{safe_convert(analyzed_stats['multi_country_pct']):.1f}%",
                    safe_convert(analyzed_stats['no_country_articles']), f"{safe_convert(analyzed_stats['no_country_pct']):.1f}%",
                    safe_convert(analyzed_stats['total_affiliations_count']),
                    safe_convert(analyzed_stats['unique_affiliations_count']),
                    safe_convert(analyzed_stats['unique_countries_count']),
                    safe_convert(analyzed_stats['unique_journals_count']),
                    safe_convert(analyzed_stats['unique_publishers_count']),
                    safe_convert(analyzed_stats['articles_with_10_citations']),
                    safe_convert(analyzed_stats['articles_with_20_citations']),
                    safe_convert(analyzed_stats['articles_with_30_citations']),
                    safe_convert(analyzed_stats['articles_with_50_citations'])
                ],
                'Value_Citing': [
                    safe_convert(citing_stats['n_items']),
                    safe_convert(citing_stats['total_refs']),
                    'References with DOI', safe_convert(citing_stats['refs_with_doi']), f"{safe_convert(citing_stats['refs_with_doi_pct']):.1f}%",
                    'References without DOI', safe_convert(citing_stats['refs_without_doi']), f"{safe_convert(citing_stats['refs_without_doi_pct']):.1f}%",
                    'Self-Citations', safe_convert(citing_stats['self_cites']), f"{safe_convert(citing_stats['self_cites_pct']):.1f}%",
                    safe_convert(citing_stats['single_authors']),
                    safe_convert(citing_stats['multi_authors_gt10']),
                    safe_convert(citing_stats['ref_min']),
                    safe_convert(citing_stats['ref_max']),
                    f"{safe_convert(citing_stats['ref_mean']):.1f}",
                    safe_convert(citing_stats['ref_median']),
                    safe_convert(citing_stats['auth_min']),
                    safe_convert(citing_stats['auth_max']),
                    f"{safe_convert(citing_stats['auth_mean']):.1f}",
                    safe_convert(citing_stats['auth_median']),
                    safe_convert(citing_stats['single_country_articles']), f"{safe_convert(citing_stats['single_country_pct']):.1f}%",
                    safe_convert(citing_stats['multi_country_articles']), f"{safe_convert(citing_stats['multi_country_pct']):.1f}%",
                    safe_convert(citing_stats['no_country_articles']), f"{safe_convert(citing_stats['no_country_pct']):.1f}%",
                    safe_convert(citing_stats['total_affiliations_count']),
                    safe_convert(citing_stats['unique_affiliations_count']),
                    safe_convert(citing_stats['unique_countries_count']),
                    safe_convert(citing_stats['unique_journals_count']),
                    safe_convert(citing_stats['unique_publishers_count']),
                    'N/A',  # Articles with ≥10 citations (для цитирующих не применимо)
                    'N/A',  # Articles with ≥20 citations
                    'N/A',  # Articles with ≥30 citations
                    'N/A'   # Articles with ≥50 citations
                ]
            }
            statistics_df = pd.DataFrame(statistics_data)
            statistics_df.to_excel(writer, sheet_name='Statistics', index=False)

            # Sheet 6: Combined Citing Stats (NEW - объединенный лист Enhanced_Statistics и Citation_Timing)
            citing_stats_data = {
                'Metric': [
                    'H-index', 'Total Citations',
                    'Average Citations per Article', 'Maximum Citations',
                    'Minimum Citations', 'Articles with Citations',
                    'Articles without Citations',
                    'Minimum Days to First Citation',
                    'Maximum Days to First Citation', 
                    'Average Days to First Citation',
                    'Median Days to First Citation', 
                    'Articles with Citation Timing Data',
                    'Total Years Covered by Citation Data'
                ],
                'Value': [
                    safe_convert(enhanced_stats['h_index']),
                    safe_convert(enhanced_stats['total_citations']),
                    f"{safe_convert(enhanced_stats['avg_citations_per_article']):.1f}",
                    safe_convert(enhanced_stats['max_citations']),
                    safe_convert(enhanced_stats['min_citations']),
                    safe_convert(enhanced_stats['articles_with_citations']),
                    safe_convert(enhanced_stats['articles_without_citations']),
                    safe_convert(citation_timing['days_min']),
                    safe_convert(citation_timing['days_max']),
                    f"{safe_convert(citation_timing['days_mean']):.1f}",
                    safe_convert(citation_timing['days_median']),
                    safe_convert(citation_timing['articles_with_timing_data']),
                    safe_convert(citation_timing['total_years_covered'])
                ]
            }
            citing_stats_df = pd.DataFrame(citing_stats_data)
            citing_stats_df.to_excel(writer, sheet_name='Citing_Stats', index=False)

            # Sheet 7: Citations by year
            yearly_citations_data = []
            for yearly_stat in citation_timing['yearly_citations']:
                yearly_citations_data.append({
                    'Year': safe_convert(yearly_stat['year']),
                    'Citations_Count': safe_convert(yearly_stat['citations_count'])
                })
            
            if yearly_citations_data:
                yearly_citations_df = pd.DataFrame(yearly_citations_data)
                yearly_citations_df.to_excel(writer, sheet_name='Citations_by_Year', index=False)

            # Sheet 8: Citation network (СОРТИРОВКА ПО ГОДАМ)
            citation_network_data = []
            for year, citing_years in enhanced_stats.get('citation_network', {}).items():
                year_counts = Counter(citing_years)
                for citing_year, count in year_counts.items():
                    citation_network_data.append({
                        'Publication_Year': safe_convert(year),
                        'Citation_Year': safe_convert(citing_year),
                        'Citations_Count': safe_convert(count)
                    })
            
            # === СОРТИРОВКА: сначала по году публикации, затем по году цитирования ===
            if citation_network_data:
                citation_network_df = pd.DataFrame(citation_network_data)
                citation_network_df = citation_network_df.sort_values(['Publication_Year', 'Citation_Year'])
                citation_network_df.to_excel(writer, sheet_name='Citation_Network', index=False)

            # === NEW COMBINED SHEETS ===

            # Sheet 9: Combined Authors (REPLACES All_Authors_Analyzed and All_Authors_Citing)
            combined_authors_data = create_combined_authors_sheet(
                analyzed_stats['all_authors'],
                citing_stats['all_authors'],
                analyzed_stats['n_items'],
                citing_stats['n_items']
            )
            if combined_authors_data:
                combined_authors_df = pd.DataFrame(combined_authors_data)
                combined_authors_df.to_excel(writer, sheet_name='Combined_Authors', index=False)

            # Sheet 10: Combined Affiliations (REPLACES All_Affiliations_Analyzed and All_Affiliations_Citing)
            combined_affiliations_data = create_combined_affiliations_sheet(
                analyzed_stats['all_affiliations'],
                citing_stats['all_affiliations'],
                sum(count for _, count in analyzed_stats['all_affiliations']),
                sum(count for _, count in citing_stats['all_affiliations']),
                state  # NEW: Pass state to access ROR settings
            )
            if combined_affiliations_data:
                combined_affiliations_df = pd.DataFrame(combined_affiliations_data)
                combined_affiliations_df.to_excel(writer, sheet_name='Combined_Affiliations', index=False)

            # Sheet 11: Combined Countries (REPLACES All_Countries_Analyzed and All_Countries_Citing)
            combined_countries_data = create_combined_countries_sheet(
                analyzed_stats['all_countries'],
                citing_stats['all_countries'],
                sum(count for _, count in analyzed_stats['all_countries']),
                sum(count for _, count in citing_stats['all_countries'])
            )
            if combined_countries_data:
                combined_countries_df = pd.DataFrame(combined_countries_data)
                combined_countries_df.to_excel(writer, sheet_name='Combined_Countries', index=False)

            # Sheet 12: All journals citing (with percentages) - UPDATED VERSION WITH CS DATA
            if citing_stats['all_journals']:
                all_citing_journals_data = []
                total_citing_articles = safe_convert(citing_stats['n_items'])
                
                # Load metrics data if not already loaded
                if get_analysis_state().if_data is None or get_analysis_state().cs_data is None:
                    load_metrics_data()
                
                for journal_info in citing_stats['all_journals']:
                    journal_name = journal_info[0]
                    count = journal_info[1]
                    percentage = (safe_convert(count) / total_citing_articles * 100) if total_citing_articles > 0 else 0
                    
                    # Extract ISSNs for this journal from citing data
                    journal_issns = []
                    for citing_item in citing_data:
                        if citing_item and citing_item.get('crossref'):
                            cr = citing_item['crossref']
                            container_title = cr.get('container-title', [''])[0] if cr.get('container-title') else ''
                            if container_title == journal_name:
                                issns = cr.get('ISSN', [])
                                if issns is None:
                                    issns = []
                                if isinstance(issns, str):
                                    issns = [issns]
                                issns = [str(issn).strip() for issn in issns if issn and isinstance(issn, str)]
                                journal_issns.extend(issns)
                    
                    # Remove duplicates
                    journal_issns = list(set(journal_issns))
                    
                    # Get ISSNs for display
                    issn_1 = journal_issns[0] if len(journal_issns) > 0 else ""
                    issn_2 = journal_issns[1] if len(journal_issns) > 1 else ""
                    
                    # Get metrics for this journal - UPDATED WITH CS DATA
                    metrics = get_journal_metrics(journal_issns)
                    
                    all_citing_journals_data.append({
                        'Journal': safe_convert(journal_name),
                        'ISSN_1': safe_convert(issn_1),
                        'ISSN_2': safe_convert(issn_2),
                        'Articles_Count': safe_convert(count),
                        'Percentage': round(percentage, 2),
                        '': '',  # Empty column
                        'IF (WoS)': safe_convert(metrics['if_metrics'].get('if', '')) if metrics['if_metrics'] else '',
                        'Q(WoS)': safe_convert(metrics['if_metrics'].get('quartile', '')) if metrics['if_metrics'] else '',
                        'SC(Scopus)': safe_convert(metrics['cs_metrics'].get('citescore', '')) if metrics['cs_metrics'] else '',
                        'Q(Scopus)': safe_convert(metrics['cs_metrics'].get('quartile', '')) if metrics['cs_metrics'] else ''
                    })
                
                all_citing_journals_df = pd.DataFrame(all_citing_journals_data)
                all_citing_journals_df.to_excel(writer, sheet_name='All_Journals_Citing', index=False)

            # Sheet 13: All publishers citing (with percentages)
            if citing_stats['all_publishers']:
                all_citing_publishers_data = []
                total_articles = safe_convert(citing_stats['n_items'])
                for publisher, count in citing_stats['all_publishers']:
                    percentage = (safe_convert(count) / total_articles * 100) if total_articles > 0 else 0
                    all_citing_publishers_data.append({
                        'Publisher': safe_convert(publisher),
                        'Articles_Count': safe_convert(count),
                        'Percentage': round(percentage, 2)
                    })
                all_citing_publishers_df = pd.DataFrame(all_citing_publishers_data)
                all_citing_publishers_df.to_excel(writer, sheet_name='All_Publishers_Citing', index=False)

            # Sheet 14: Fast metrics (NEW)
            fast_metrics_data = {
                'Metric': [
                    'Reference Age (median)', 'Reference Age (mean)',
                    'Reference Age (25-75 percentile)', 'References Analyzed',
                    'Journal Self-Citation Rate (JSCR)', 'Journal Self-Citations',
                    'Total Citations for JSCR',
                    'Cited Half-Life (median)', 'Cited Half-Life (mean)',
                    'Articles with CHL Data',
                    'Field-Weighted Citation Impact (FWCI)', 'Total Citations',
                    'Expected Citations',
                    'Citation Velocity', 'Articles with Velocity Data',
                    'OA Impact Premium', 'OA Articles', 'Non-OA Articles',
                    'Average OA Citations', 'Average Non-OA Citations',
                    'Elite Index', 'Elite Articles', 'Citation Threshold',
                    'Author Gini Index', 'Total Authors',
                    'Average Articles per Author', 'Median Articles per Author',
                    'Diversity Balance Index (DBI)', 'Unique Concepts',
                    'Total Concept Mentions'
                ],
                'Value': [
                    safe_convert(fast_metrics.get('ref_median_age', 'N/A')),
                    safe_convert(fast_metrics.get('ref_mean_age', 'N/A')),
                    f"{safe_convert(fast_metrics.get('ref_ages_25_75', ['N/A', 'N/A'])[0])}-{safe_convert(fast_metrics.get('ref_ages_25_75', ['N/A', 'N/A'])[1])}",
                    safe_convert(fast_metrics.get('total_refs_analyzed', 0)),
                    f"{safe_convert(fast_metrics.get('JSCR', 0))}%",
                    safe_convert(fast_metrics.get('self_cites', 0)),
                    safe_convert(fast_metrics.get('total_cites', 0)),
                    safe_convert(fast_metrics.get('cited_half_life_median', 'N/A')),
                    safe_convert(fast_metrics.get('cited_half_life_mean', 'N/A')),
                    safe_convert(fast_metrics.get('articles_with_chl', 0)),
                    safe_convert(fast_metrics.get('FWCI', 0)),
                    safe_convert(fast_metrics.get('total_cites', 0)),
                    safe_convert(fast_metrics.get('expected_cites', 0)),
                    safe_convert(fast_metrics.get('citation_velocity', 0)),
                    safe_convert(fast_metrics.get('articles_with_velocity', 0)),
                    f"{safe_convert(fast_metrics.get('OA_impact_premium', 0))}%",
                    safe_convert(fast_metrics.get('OA_articles', 0)),
                    safe_convert(fast_metrics.get('non_OA_articles', 0)),
                    safe_convert(fast_metrics.get('OA_avg_citations', 0)),
                    safe_convert(fast_metrics.get('non_OA_avg_citations', 0)),
                    f"{safe_convert(fast_metrics.get('elite_index', 0))}%",
                    safe_convert(fast_metrics.get('elite_articles', 0)),
                    safe_convert(fast_metrics.get('citation_threshold', 0)),
                    safe_convert(fast_metrics.get('author_gini', 0)),
                    safe_convert(fast_metrics.get('total_authors', 0)),
                    safe_convert(fast_metrics.get('articles_per_author_avg', 0)),
                    safe_convert(fast_metrics.get('articles_per_author_median', 0)),
                    safe_convert(fast_metrics.get('DBI', 0)),
                    safe_convert(fast_metrics.get('unique_concepts', 0)),
                    safe_convert(fast_metrics.get('total_concept_mentions', 0))
                ]
            }
            fast_metrics_df = pd.DataFrame(fast_metrics_data)
            fast_metrics_df.to_excel(writer, sheet_name='Fast_Metrics', index=False)

            # Sheet 15: Top concepts (NEW) - РАСШИРЕНО ДО 10 ТЕРМИНОВ
            if fast_metrics.get('top_concepts'):
                top_concepts_data = {
                    'Concept': [safe_convert(concept[0]) for concept in fast_metrics['top_concepts']],
                    'Mentions_Count': [safe_convert(concept[1]) for concept in fast_metrics['top_concepts']]
                }
                top_concepts_df = pd.DataFrame(top_concepts_data)
                top_concepts_df.to_excel(writer, sheet_name='Top_Concepts', index=False)

            # === НОВЫЙ ЛИСТ: Объединенный анализ ключевых слов в названиях ===
            # Sheet 16: Combined Title Keywords (NEW) - ИСПРАВЛЕНО: правильное имя листа
            if 'title_keywords' in additional_data:
                keywords_data = additional_data['title_keywords']
                normalized_keywords = normalize_keywords_data(keywords_data)
                
                if normalized_keywords:
                    keywords_df = pd.DataFrame(normalized_keywords)
                    keywords_df.to_excel(writer, sheet_name='Combined_Title_Keywords', index=False)

            # Sheet 17: Citation seasonality - ИСПРАВЛЕНО: правильное имя листа
            if 'citation_seasonality' in additional_data:
                seasonality_data = []
                citation_seasonality = additional_data['citation_seasonality']
                
                # Citation by month chart
                for month in range(1, 13):
                    month_name = datetime(2023, month, 1).strftime('%B')
                    citation_count = safe_convert(citation_seasonality['citation_months'].get(month, 0))
                    publication_count = safe_convert(citation_seasonality['publication_months'].get(month, 0))
                    
                    seasonality_data.append({
                        'Month_Number': safe_convert(month),
                        'Month_Name': safe_convert(month_name),
                        'Citation_Count': citation_count,
                        'Publication_Count': publication_count
                    })
                
                if seasonality_data:
                    seasonality_df = pd.DataFrame(seasonality_data)
                    seasonality_df.to_excel(writer, sheet_name='Citation_Seasonality', index=False)
            
                # Optimal publication months - ИСПРАВЛЕНО: создаем отдельный лист
                if citation_seasonality['optimal_publication_months']:
                    optimal_months_data = []
                    for optimal in citation_seasonality['optimal_publication_months']:
                        optimal_months_data.append({
                            'High_Citation_Month': datetime(2023, safe_convert(optimal['citation_month']), 1).strftime('%B'),
                            'Citation_Count': safe_convert(optimal['citation_count']),
                            'Recommended_Publication_Month': datetime(2023, safe_convert(optimal['recommended_publication_month']), 1).strftime('%B'),
                            'Reasoning': safe_convert(optimal['reasoning'])
                        })
                    
                    optimal_months_df = pd.DataFrame(optimal_months_data)
                    optimal_months_df.to_excel(writer, sheet_name='Optimal_Publication_Months', index=False)
              
            # Sheet 18: Potential reviewers - ИСПРАВЛЕНО: правильное имя листа
            if 'potential_reviewers' in additional_data:
                reviewers_data = []
                potential_reviewers_info = additional_data['potential_reviewers']
                
                for reviewer in potential_reviewers_info['potential_reviewers']:
                    # Create separate rows for each DOI
                    for i, doi in enumerate(reviewer['citing_dois']):
                        reviewers_data.append({
                            'Author': safe_convert(reviewer['author']) if i == 0 else '',  # Only show author name in first row
                            'Citation_Count': safe_convert(reviewer['citation_count']) if i == 0 else '',
                            'Citing_DOI': safe_convert(doi)
                        })
                
                if reviewers_data:
                    reviewers_df = pd.DataFrame(reviewers_data)
                    reviewers_df.to_excel(writer, sheet_name='Potential_Reviewers', index=False)

            # Sheet 19: Special Analysis Metrics (NEW) - ИСПРАВЛЕНО: правильное имя листа
            if 'special_analysis_metrics' in additional_data:
                special_metrics = additional_data['special_analysis_metrics']
                debug_info = special_metrics.get('debug_info', {})
                
                special_metrics_data = {
                    'Metric': [
                        'CiteScore (A/B)',
                        'CiteScore Corrected (C/B)', 
                        'Impact Factor (E/D)',
                        'Impact Factor Corrected (F/D)',
                        'B (Articles for CiteScore)',
                        'A (Citations for CiteScore)',
                        'C (Scopus Citations for CiteScore)',
                        'D (Articles for Impact Factor)',
                        'E (Citations for Impact Factor)',
                        'F (WoS Citations for Impact Factor)'
                    ],
                    'Value': [
                        safe_convert(special_metrics.get('cite_score', 0)),
                        safe_convert(special_metrics.get('cite_score_corrected', 0)),
                        safe_convert(special_metrics.get('impact_factor', 0)),
                        safe_convert(special_metrics.get('impact_factor_corrected', 0)),
                        safe_convert(debug_info.get('B', 0)),
                        safe_convert(debug_info.get('A', 0)),
                        safe_convert(debug_info.get('C', 0)),
                        safe_convert(debug_info.get('D', 0)),
                        safe_convert(debug_info.get('E', 0)),
                        safe_convert(debug_info.get('F', 0))
                    ]
                }
                special_metrics_df = pd.DataFrame(special_metrics_data)
                special_metrics_df.to_excel(writer, sheet_name='Special_Analysis_Metrics', index=False)

            # === NEW SHEET: Author ID Data ===
            # Sheet 20: Author_ID_data (NEW)
            if state.include_author_id_data:
                author_id_data = create_author_id_sheet(analyzed_data, citing_data, state)
                if author_id_data:
                    author_id_df = pd.DataFrame(author_id_data)
                    author_id_df.to_excel(writer, sheet_name='Author_ID_data', index=False)

            # Ensure at least one sheet exists
            if len(writer.sheets) == 0:
                summary_df = pd.DataFrame({
                    'Status': ['Analysis completed'],
                    'Message': ['No data matched the criteria. Check ISSN and period.']
                })
                summary_df.to_excel(writer, sheet_name='Summary', index=False)

        excel_buffer.seek(0)
        return True

    except Exception as e:
        st.error(translation_manager.get_text('excel_creation_error').format(error=str(e)))
        # Create minimal report with error
        try:
            excel_buffer.seek(0)
            excel_buffer.truncate(0)
            
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                error_df = pd.DataFrame({
                    'Error': [f'{translation_manager.get_text("failed_create_full_report")}: {str(e)}'],
                    'Recommendation': [translation_manager.get_text('try_reduce_data_or_period')]
                })
                error_df.to_excel(writer, sheet_name='Information', index=False)
            
            excel_buffer.seek(0)
            st.warning(translation_manager.get_text('simplified_report_created'))
            return True
            
        except Exception as e2:
            st.error(translation_manager.get_text('critical_excel_error').format(error=str(e2)))
            return False

def precompute_excel_data(analyzed_data, citing_data, analyzed_stats, citing_stats, enhanced_stats, citation_timing, overlap_details, fast_metrics, additional_data, state):
    """Предварительный расчет всех данных для Excel отчетов"""
    
    print("🔍 Precomputing data for Excel generation...")
    
    # Обработка анализируемых данных блоками
    def process_analyzed_chunk(chunk):
        chunk_results = []
        for item in chunk:
            if item and item.get('crossref'):
                cr = item['crossref']
                oa = item.get('openalex', {})
                
                article_data = cached_extract_article_data({'openalex': oa})
                journal_info = cached_extract_journal_info(item)
                
                chunk_results.append({
                    'cr': cr,
                    'oa': oa,
                    'article_data': article_data,
                    'journal_info': journal_info,
                    'doi': cr.get('DOI', '')
                })
        return chunk_results
    
    analyzed_precomputed = process_data_in_chunks(analyzed_data, 500, process_analyzed_chunk)
    
    # Аналогично для citing данных
    def process_citing_chunk(chunk):
        chunk_results = []
        for item in chunk:
            if item and item.get('crossref'):
                cr = item['crossref']
                oa = item.get('openalex', {})
                
                article_data = cached_extract_article_data({'openalex': oa})
                journal_info = cached_extract_journal_info(item)
                
                chunk_results.append({
                    'cr': cr,
                    'oa': oa,
                    'article_data': article_data,
                    'journal_info': journal_info,
                    'doi': cr.get('DOI', '')
                })
        return chunk_results
    
    citing_precomputed = process_data_in_chunks(citing_data, 500, process_citing_chunk)
    
    # Предварительно вычисляем usage данные для Special Analysis
    special_metrics = additional_data.get('special_analysis_metrics', {})
    analyzed_articles_usage = special_metrics.get('debug_info', {}).get('analyzed_articles_usage', {})
    citing_articles_usage = special_metrics.get('debug_info', {}).get('citing_articles_usage', {})
    
    return {
        'analyzed_precomputed': analyzed_precomputed,
        'citing_precomputed': citing_precomputed,
        'analyzed_articles_usage': analyzed_articles_usage,
        'citing_articles_usage': citing_articles_usage
    }

# === 18. Data Visualization ===
def create_visualizations(analyzed_stats, citing_stats, enhanced_stats, citation_timing, overlap_details, fast_metrics, additional_data, is_special_analysis=False):
    """Create visualizations for dashboard"""
    
    # Create tabs for different visualization types
    tab1, tab2, tab3, tab4 = st.tabs([
        translation_manager.get_text('tab_main_metrics'), 
        translation_manager.get_text('tab_authors_organizations'), 
        translation_manager.get_text('tab_geography'), 
        translation_manager.get_text('tab_citations')
    ])
    
    with tab1:
        st.subheader(translation_manager.get_text('tab_main_metrics'))
        
        # Check if we're in Special Analysis mode and show additional metrics
        if is_special_analysis and 'special_analysis_metrics' in additional_data:
            st.subheader("🎯 Special Analysis Metrics")
            
            special_metrics = additional_data['special_analysis_metrics']
            debug_info = special_metrics.get('debug_info', {})
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "CiteScore", 
                    f"{special_metrics.get('cite_score', 0):.2f}",
                    help="A/B: Total citations (A) / Total articles (B) in Special Analysis period"
                )
            with col2:
                st.metric(
                    "CiteScore Corrected", 
                    f"{special_metrics.get('cite_score_corrected', 0):.2f}",
                    help="C/B: Scopus-indexed citations (C) / Total articles (B)"
                )
            with col3:
                st.metric(
                    "Impact Factor", 
                    f"{special_metrics.get('impact_factor', 0):.2f}",
                    help="E/D: Total citations (E) / Total articles (D) in IF calculation period"
                )
            with col4:
                st.metric(
                    "Impact Factor Corrected", 
                    f"{special_metrics.get('impact_factor_corrected', 0):.2f}",
                    help="F/D: WoS-indexed citations (F) / Total articles (D)"
                )
    
            # Show debug information in expander
                with st.expander("📊 Special Analysis Details", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**CiteScore Calculation:**")
                        st.write(f"- B (Articles): {debug_info.get('B', 0)}")
                        st.write(f"- A (Citations): {debug_info.get('A', 0)}")
                        st.write(f"- C (Scopus Citations): {debug_info.get('C', 0)}")
                        st.write(f"- CiteScore: {debug_info.get('A', 0)} / {debug_info.get('B', 0)} = {special_metrics.get('cite_score', 0):.2f}")
                    
                    with col2:
                        st.write("**Impact Factor Calculation:**")
                        st.write(f"- D (Articles): {debug_info.get('D', 0)}")
                        st.write(f"- E (Citations): {debug_info.get('E', 0)}")
                        st.write(f"- F (WoS Citations): {debug_info.get('F', 0)}")
                        st.write(f"- Impact Factor: {debug_info.get('E', 0)} / {debug_info.get('D', 0)} = {special_metrics.get('impact_factor', 0):.2f}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                translation_manager.get_text('h_index'), 
                enhanced_stats['h_index'],
                help=glossary.get_tooltip('H-index')
            )
        with col2:
            st.metric(
                translation_manager.get_text('total_articles'), 
                analyzed_stats['n_items'],
                help=glossary.get_tooltip('Crossref')
            )
        with col3:
            st.metric(
                translation_manager.get_text('total_citations'), 
                enhanced_stats['total_citations'],
                help=translation_manager.get_text('total_citations_tooltip')
            )
        with col4:
            st.metric(
                translation_manager.get_text('average_citations'), 
                f"{enhanced_stats['avg_citations_per_article']:.1f}",
                help=translation_manager.get_text('average_citations_tooltip')
            )
        
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.metric(
                translation_manager.get_text('articles_with_citations'), 
                enhanced_stats['articles_with_citations'],
                help=translation_manager.get_text('articles_with_citations_tooltip')
            )
        with col6:
            st.metric(
                translation_manager.get_text('self_citations'), 
                f"{analyzed_stats['self_cites_pct']:.1f}%",
                help=glossary.get_tooltip('Self-Cites')
            )
        with col7:
            st.metric(
                translation_manager.get_text('international_articles'), 
                f"{analyzed_stats['multi_country_pct']:.1f}%",
                help=glossary.get_tooltip('International Collaboration')
            )
        with col8:
            st.metric(
                translation_manager.get_text('unique_affiliations'), 
                analyzed_stats['unique_affiliations_count'],
                help=translation_manager.get_text('unique_affiliations_tooltip')
            )
        
        # Contextual tooltip for H-index
        with st.expander("❓ " + translation_manager.get_text('what_is_h_index'), expanded=False):
            h_info = glossary.get_detailed_info('H-index')
            if h_info:
                st.write(f"**{h_info['term']}** - {h_info['definition']}")
                st.write(f"**Calculation:** {h_info['calculation']}")
                st.write(f"**Interpretation:** {h_info['interpretation']}")
                st.write(f"**Example:** {h_info['example']}")
                st.write(f"**Category:** {h_info['category']}")
        
        # Citations by year chart
        if citation_timing['yearly_citations']:
            years = [item['year'] for item in citation_timing['yearly_citations']]
            citations = [item['citations_count'] for item in citation_timing['yearly_citations']]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=years, 
                y=citations, 
                name=translation_manager.get_text('citations'),
                marker_color='lightblue'
            ))
            fig.update_layout(
                title=translation_manager.get_text('citations_by_year'),
                xaxis_title=translation_manager.get_text('year'),
                yaxis_title=translation_manager.get_text('citations_count'),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader(translation_manager.get_text('tab_authors_organizations'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top authors of analyzed articles
            if analyzed_stats['all_authors']:
                top_authors = analyzed_stats['all_authors'][:15]
                authors_df = pd.DataFrame(top_authors, columns=[translation_manager.get_text('author'), translation_manager.get_text('articles')])
                fig = px.bar(
                    authors_df, 
                    x=translation_manager.get_text('articles'), 
                    y=translation_manager.get_text('author'), 
                    orientation='h',
                    title=translation_manager.get_text('top_15_authors_analyzed')
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Author count distribution
            author_counts_data = {
                translation_manager.get_text('category'): ['1 ' + translation_manager.get_text('author'), '2-5 ' + translation_manager.get_text('authors'), '6-10 ' + translation_manager.get_text('authors'), '>10 ' + translation_manager.get_text('authors')],
                translation_manager.get_text('articles'): [
                    analyzed_stats['single_authors'],
                    analyzed_stats['n_items'] - analyzed_stats['single_authors'] - analyzed_stats['multi_authors_gt10'],
                    analyzed_stats['multi_authors_gt10'],
                    0  # Can add additional categorization
                ]
            }
            fig = px.pie(
                author_counts_data, 
                values=translation_manager.get_text('articles'), 
                names=translation_manager.get_text('category'),
                title=translation_manager.get_text('author_count_distribution')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Contextual tooltip for Author Gini
        if fast_metrics.get('author_gini', 0) > 0:
            with st.expander("🎯 " + translation_manager.get_text('author_gini_meaning'), expanded=False):
                gini_info = glossary.get_detailed_info('Author Gini')
                if gini_info:
                    st.write(f"**{translation_manager.get_text('current_value')}:** {fast_metrics['author_gini']}")
                    st.write(f"**{translation_manager.get_text('interpretation')}:** {gini_info['interpretation']}")
                    st.progress(min(fast_metrics['author_gini'], 1.0))
        
        # Top affiliations
        if analyzed_stats['all_affiliations']:
            top_affiliations = analyzed_stats['all_affiliations'][:10]
            aff_df = pd.DataFrame(top_affiliations, columns=[translation_manager.get_text('affiliation'), translation_manager.get_text('mentions')])
            fig = px.bar(
                aff_df, 
                x=translation_manager.get_text('mentions'), 
                y=translation_manager.get_text('affiliation'), 
                orientation='h',
                title=translation_manager.get_text('top_10_affiliations_analyzed'),
                color=translation_manager.get_text('mentions')
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader(translation_manager.get_text('tab_geography'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Country distribution
            if analyzed_stats['all_countries']:
                countries_df = pd.DataFrame(analyzed_stats['all_countries'], columns=[translation_manager.get_text('country'), translation_manager.get_text('articles')])
                fig = px.pie(
                    countries_df, 
                    values=translation_manager.get_text('articles'), 
                    names=translation_manager.get_text('country'),
                    title=translation_manager.get_text('article_country_distribution')
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # International collaboration
            collaboration_data = {
                translation_manager.get_text('type'): [translation_manager.get_text('single_country'), translation_manager.get_text('multiple_countries'), translation_manager.get_text('no_data')],
                translation_manager.get_text('articles'): [
                    analyzed_stats['single_country_articles'],
                    analyzed_stats['multi_country_articles'],
                    analyzed_stats['no_country_articles']
                ]
            }
            fig = px.bar(
                collaboration_data, 
                x=translation_manager.get_text('type'), 
                y=translation_manager.get_text('articles'),
                title=translation_manager.get_text('international_collaboration'),
                color=translation_manager.get_text('type')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Contextual tooltip for international collaboration
        with st.expander("🌐 " + translation_manager.get_text('about_international_collaboration'), expanded=False):
            collab_info = glossary.get_detailed_info('International Collaboration')
            if collab_info:
                st.write(f"**{translation_manager.get_text('definition')}:** {collab_info['definition']}")
                st.write(f"**{translation_manager.get_text('significance_for_science')}:** " + translation_manager.get_text('high_international_articles_indicator'))
    
    with tab4:
        st.subheader(translation_manager.get_text('tab_citations'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Citations by thresholds
            citation_thresholds = {
                translation_manager.get_text('threshold'): ['≥10', '≥20', '≥30', '≥50'],
                translation_manager.get_text('articles'): [
                    analyzed_stats['articles_with_10_citations'],
                    analyzed_stats['articles_with_20_citations'],
                    analyzed_stats['articles_with_30_citations'],
                    analyzed_stats['articles_with_50_citations']
                ]
            }
            fig = px.bar(
                citation_thresholds, 
                x=translation_manager.get_text('threshold'), 
                y=translation_manager.get_text('articles'),
                title=translation_manager.get_text('articles_by_citation_thresholds'),
                color=translation_manager.get_text('threshold')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Articles with/without citations
            citation_status = {
                translation_manager.get_text('status'): [translation_manager.get_text('with_citations'), translation_manager.get_text('without_citations')],
                translation_manager.get_text('count'): [
                    enhanced_stats['articles_with_citations'],
                    enhanced_stats['articles_without_citations']
                ]
            }
            fig = px.pie(
                citation_status, 
                values=translation_manager.get_text('count'), 
                names=translation_manager.get_text('status'),
                title=translation_manager.get_text('articles_by_citation_status')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Contextual tooltip for JSCR
        if fast_metrics.get('JSCR', 0) > 0:
            with st.expander("🔍 " + translation_manager.get_text('jscr_explanation'), expanded=False):
                jscr_info = glossary.get_detailed_info('JSCR')
                if jscr_info:
                    st.write(f"**{translation_manager.get_text('current_value')}:** {fast_metrics['JSCR']}%")
                    st.write(f"**{translation_manager.get_text('interpretation')}:** {jscr_info['interpretation']}")
                    
                    # Visual indication
                    jscr_value = fast_metrics['JSCR']
                    if jscr_value < 10:
                        st.success("✅ " + translation_manager.get_text('low_self_citations_excellent'))
                    elif jscr_value < 20:
                        st.info("ℹ️ " + translation_manager.get_text('moderate_self_citations_normal'))
                    elif jscr_value < 30:
                        st.warning("⚠️ " + translation_manager.get_text('elevated_self_citations_attention'))
                    else:
                        st.error("❌ " + translation_manager.get_text('high_self_citations_problems'))

# =============================================================================
# 19. OPTIMIZED MAIN ANALYSIS FUNCTION
# =============================================================================

def analyze_journal_optimized(issn, period_str, special_analysis=False, include_ror_data=False, include_author_id_data=False):
    """Optimized version of analyze_journal with parallel processing and caching"""
    global delayer
    delayer = AdaptiveDelayer()

    analysis_start_time = time.time()
    
    # Создаем контейнер для счетчика общего времени
    timer_container = st.empty()
    timer_container.info("⏱️ Starting analysis...")
    
    state = get_analysis_state()
    state.analysis_complete = False
    
    # Функция для обновления счетчика общего времени
    def update_timer():
        elapsed_time = time.time() - analysis_start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        timer_container.info(f"⏱️ Total analysis time: {minutes:02d}:{seconds:02d}")
    
    # Запускаем обновление таймера в отдельном потоке
    import threading
    stop_timer = False
    
    def timer_thread():
        while not stop_timer:
            update_timer()
            time.sleep(1)  # Обновляем каждую секунду
    
    timer_thread = threading.Thread(target=timer_thread, daemon=True)
    timer_thread.start()
    
    # Set analysis modes
    state.is_special_analysis = special_analysis
    state.include_ror_data = include_ror_data
    state.include_author_id_data = include_author_id_data
    
    # Predictive cache warmup
    predictive_cache_warmup(issn)
    
    # Load metrics data in background
    load_metrics_data()
    
    # Overall progress
    overall_progress = st.progress(0)
    overall_status = st.empty()
    
    # Period parsing
    overall_status.text(translation_manager.get_text('parsing_period'))
    
    if state.is_special_analysis:
        current_date = datetime.now()
        from_date = (current_date - timedelta(days=1580)).strftime('%Y-%m-%d')
        until_date = (current_date - timedelta(days=120)).strftime('%Y-%m-%d')
        years = [current_date.year - 4, current_date.year - 3, current_date.year - 2, current_date.year - 1]
        st.info(f"🔬 Special Analysis Mode: Using fixed period {from_date} to {until_date}")
    else:
        years = parse_period(period_str)
        if not years:
            return
        from_date = f"{min(years)}-01-01"
        until_date = f"{max(years)}-12-31"
    
    overall_progress.progress(0.1)
    
    # Journal name (optimized with caching)
    overall_status.text(translation_manager.get_text('getting_journal_name'))
    journal_name = optimized_get_journal_name(issn)
    st.success(translation_manager.get_text('journal_found').format(journal_name=journal_name, issn=issn))
    overall_progress.progress(0.2)
    
    # Article retrieval
    overall_status.text(translation_manager.get_text('loading_articles'))
    items = fetch_articles_by_issn_period(issn, from_date, until_date)
    if not items:
        st.error(translation_manager.get_text('no_articles_found'))
        return

    n_analyzed = len(items)
    st.success(translation_manager.get_text('articles_found').format(count=n_analyzed))
    overall_progress.progress(0.3)
    
    # Data validation
    overall_status.text(translation_manager.get_text('validating_data'))
    validated_items = validate_and_clean_data(items)
    journal_prefix = get_doi_prefix(validated_items[0].get('DOI', '')) if validated_items else ''
    overall_progress.progress(0.4)
    
    # PARALLEL: Analyzed articles processing
    overall_status.text(translation_manager.get_text('processing_articles'))
    
    analyzed_metadata = []
    dois = [item.get('DOI') for item in validated_items if item.get('DOI')]
    
    # Use parallel metadata loading
    meta_progress = st.progress(0)
    meta_status = st.empty()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(parallel_metadata_loading, doi, state): doi for doi in dois}
        
        for i, future in enumerate(as_completed(futures)):
            doi = futures[future]
            try:
                result = future.result()
                analyzed_metadata.append({
                    'doi': doi,
                    'crossref': result['crossref'],
                    'openalex': result['openalex']
                })
            except Exception as e:
                st.error(f"Error processing DOI {doi}: {e}")
            
            progress = (i + 1) / len(dois)
            meta_progress.progress(progress)
            meta_status.text(f"{translation_manager.get_text('getting_metadata')}: {i + 1}/{len(dois)}")
    
    meta_progress.empty()
    meta_status.empty()
    overall_progress.progress(0.6)
    
    # PARALLEL: Citing works retrieval and processing
    overall_status.text(translation_manager.get_text('collecting_citations'))
    
    all_citing_metadata = []
    analyzed_dois = [am['doi'] for am in analyzed_metadata if am.get('doi')]
    
    citing_progress = st.progress(0)
    citing_status = st.empty()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(get_citing_dois_and_metadata, (doi, state)): doi for doi in analyzed_dois}
        
        for i, future in enumerate(as_completed(futures)):
            doi = futures[future]
            try:
                citings = future.result()
                all_citing_metadata.extend(citings)
            except Exception as e:
                st.error(f"Error collecting citations for {doi}: {e}")
            
            progress = (i + 1) / len(analyzed_dois)
            citing_progress.progress(progress)
            citing_status.text(f"{translation_manager.get_text('collecting_citations_progress')}: {i + 1}/{len(analyzed_dois)}")
    
    citing_progress.empty()
    citing_status.empty()
    
    # Unique citing works
    unique_citing_dois = set(c['doi'] for c in all_citing_metadata if c.get('doi'))
    n_citing = len(unique_citing_dois)
    st.success(translation_manager.get_text('unique_citing_works').format(count=n_citing))
    overall_progress.progress(0.7)
    
    # PARALLEL: Statistics and metrics calculation
    overall_status.text(translation_manager.get_text('calculating_statistics'))
    
    # Use parallel metrics calculation
    stats_progress = st.progress(0)
    stats_status = st.empty()
    
    # Start parallel calculations
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_analyzed_stats = executor.submit(extract_stats_from_metadata, analyzed_metadata, journal_prefix=journal_prefix)
        future_citing_stats = executor.submit(extract_stats_from_metadata, all_citing_metadata, is_analyzed=False)
        future_parallel_metrics = executor.submit(parallel_metrics_calculation, analyzed_metadata, all_citing_metadata, state, issn)
        
        # Wait for completion with progress updates
        stats_status.text("Calculating analyzed statistics...")
        analyzed_stats = future_analyzed_stats.result()
        stats_progress.progress(0.33)
        
        stats_status.text("Calculating citing statistics...")
        citing_stats = future_citing_stats.result()
        stats_progress.progress(0.66)
        
        stats_status.text("Calculating advanced metrics...")
        parallel_metrics = future_parallel_metrics.result()
        stats_progress.progress(1.0)
    
    stats_progress.empty()
    stats_status.empty()
    
    # Extract results from parallel metrics
    enhanced_stats = parallel_metrics['basic']
    fast_metrics = parallel_metrics['fast']
    citation_timing = parallel_metrics['timing']
    overlap_details = parallel_metrics['overlap']
    
    # PARALLEL: Additional analyses
    overall_status.text("Calculating additional insights...")
    
    additional_data = parallel_analyses(
        analyzed_metadata, 
        all_citing_metadata, 
        state, 
        citation_timing['days_median'],
        analyzed_stats,  # передаем статистику
        citing_stats     # передаем статистику
    )
    
    # Add special analysis metrics if available
    if state.is_special_analysis and 'special_analysis' in additional_data:
        additional_data['special_analysis_metrics'] = additional_data['special_analysis']
    
    overall_progress.progress(0.9)
    
    # Report creation
    overall_status.text(translation_manager.get_text('creating_report'))

    analysis_end_time = time.time()
    analysis_duration = analysis_end_time - analysis_start_time
    minutes = int(analysis_duration // 60)
    seconds = int(analysis_duration % 60)
    
    st.success(f"✅ Data analysis completed in {minutes}m {seconds}s")
    st.info("📊 Now generating Excel report...")
    
    excel_start_time = time.time()  # Таймер для генерации Excel
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'journal_analysis_{issn}_{timestamp}.xlsx'
    
    # Create Excel file in memory
    excel_buffer = io.BytesIO()
    
    # Prepare data for Excel
    excel_data = {
        'analyzed': analyzed_metadata,
        'citing': all_citing_metadata,
        'stats': {
            'analyzed': analyzed_stats,
            'citing': citing_stats,
            'enhanced': enhanced_stats,
            'timing': citation_timing
        },
        'metrics': {
            'fast': fast_metrics,
            'overlap': overlap_details
        },
        'additional': additional_data
    }
    
    create_enhanced_excel_report(
        analyzed_metadata, 
        all_citing_metadata, 
        analyzed_stats, 
        citing_stats, 
        enhanced_stats, 
        citation_timing, 
        overlap_details, 
        fast_metrics, 
        excel_buffer,
        additional_data
    )
    
    excel_buffer.seek(0)
    state.excel_buffer = excel_buffer

    excel_end_time = time.time()
    excel_duration = excel_end_time - excel_start_time
    total_duration = excel_end_time - analysis_start_time
    
    total_minutes = int(total_duration // 60)
    total_seconds = int(total_duration % 60)
    excel_minutes = int(excel_duration // 60)
    excel_seconds = int(excel_duration % 60)
    
    overall_progress.progress(1.0)
    overall_status.text(translation_manager.get_text('analysis_complete'))

    st.success(f"🎉 Complete analysis finished in {total_minutes}m {total_seconds}s")
    st.info(f"⏱️ Breakdown: Data analysis - {minutes}m {seconds}s, Excel generation - {excel_minutes}m {excel_seconds}s")
    
    # Save results
    state.analysis_results = {
        'analysis_duration': total_duration,
        'data_analysis_time': analysis_duration,
        'excel_generation_time': excel_duration,
        'analyzed_stats': analyzed_stats,
        'citing_stats': citing_stats,
        'enhanced_stats': enhanced_stats,
        'citation_timing': citation_timing,
        'overlap_details': overlap_details,
        'fast_metrics': fast_metrics,
        'additional_data': additional_data,
        'journal_name': journal_name,
        'issn': issn,
        'period': period_str,
        'n_analyzed': n_analyzed,
        'n_citing': n_citing
    }
    
    # Add special analysis metrics to results if available
    if state.is_special_analysis:
        state.analysis_results['special_analysis_metrics'] = additional_data.get('special_analysis_metrics', {})
    
    state.analysis_complete = True
    
    # Clear old caches to free memory
    clear_old_cache()
    
    time.sleep(1)
    overall_progress.empty()
    overall_status.empty()

    # Останавливаем таймер
    stop_timer = True
    timer_thread.join(timeout=1)
    
    # Финальное отображение времени
    elapsed_time = time.time() - analysis_start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    timer_container.success(f"✅ Total analysis completed in: {minutes:02d}:{seconds:02d}")

# =============================================================================
# 20. UPDATED MAIN INTERFACE WITH OPTIMIZED ANALYSIS
# =============================================================================

def main_optimized():
    """Optimized main interface using enhanced analysis"""
    initialize_analysis_state()
    state = get_analysis_state()
    
    # Language selector in sidebar
    with st.sidebar:
        st.header("🌍 Language")
        selected_language = st.selectbox(
            "Select language:",
            options=list(translation_manager.languages.keys()),
            format_func=lambda x: translation_manager.languages[x],
            index=0  # English by default
        )
        translation_manager.set_language(selected_language)
    
    # Header
    st.title("🔬 " + translation_manager.get_text('app_title'))
    st.markdown("---")
    
    # Sidebar with data input
    with st.sidebar:
        st.header("📝 " + translation_manager.get_text('analysis_parameters'))
        
        issn = st.text_input(
            translation_manager.get_text('journal_issn'),
            value="2411-1414",
            help=glossary.get_tooltip('ISSN')
        )
        
        # Special Analysis checkbox
        special_analysis = st.checkbox(
            "🎯 Special Analysis Mode", 
            value=False,
            help="Calculate CiteScore and Impact Factor metrics using their specific timeframe windows"
        )
        
        # Period input - disabled when Special Analysis is active
        period = st.text_input(
            translation_manager.get_text('analysis_period'),
            value="2022-2025",
            help=translation_manager.get_text('period_examples'),
            disabled=special_analysis
        )
        
        st.markdown("---")
        
        # Include ROR data checkbox
        include_ror_data = st.checkbox(
            "🔍 Include ROR data", 
            value=False,
            help="Include ROR organization data in Combined_Affiliations sheet (may increase processing time)"
        )
        
        # Include Author ID data checkbox
        include_author_id_data = st.checkbox(
            "👤 Include Author ID data", 
            value=False,
            help="Include Author ID data (ORCID, Scopus ID, WoS ID) in Author_ID_data sheet (may significantly increase processing time; **please do not select for a large number of analyzed or citing papers**)"
        )
        
        if include_ror_data:
            st.info("🔍 ROR Data: Organization information will be included in Combined_Affiliations sheet")
        
        if include_author_id_data:
            st.info("👤 Author ID Data: Author identifiers (ORCID, Scopus ID, WoS ID) will be included in Author_ID_data sheet")
        
        st.markdown("---")
        st.header("📚 " + translation_manager.get_text('dictionary_of_terms'))
        
        # Dictionary term search widget
        search_term = st.selectbox(
            translation_manager.get_text('select_term_to_learn'),
            options=[""] + list(glossary.terms.keys()),
            format_func=lambda x: translation_manager.get_text('choose_term') if x == "" else f"{x} ({glossary.terms[x]['category']})",
            help=translation_manager.get_text('study_metric_meanings')
        )
        
        if search_term:
            term_info = glossary.get_detailed_info(search_term)
            if term_info:
                st.info(f"**{term_info['term']}**\n\n{term_info['definition']}")
                st.caption(f"**{translation_manager.get_text('calculation')}:** {term_info['calculation']}")
                st.caption(f"**{translation_manager.get_text('interpretation')}:** {term_info['interpretation']}")
                st.caption(f"**{translation_manager.get_text('example')}:** {term_info['example']}")
                st.caption(f"**{translation_manager.get_text('category')}:** {term_info['category']}")
                
                # Mark viewed term
                if search_term not in st.session_state.viewed_terms:
                    st.session_state.viewed_terms.add(search_term)
                    st.toast(translation_manager.get_text('learned_term_toast').format(term=search_term), icon="🎯")
                
                # "I understood" button
                if st.button(translation_manager.get_text('term_understood'), key=f"understand_{search_term}"):
                    if search_term not in st.session_state.learned_terms:
                        st.session_state.learned_terms.add(search_term)
                        st.success(translation_manager.get_text('term_added_success').format(term=search_term))
                        st.balloons()
        
        # Learned terms statistics
        if st.session_state.learned_terms:
            st.markdown("---")
            st.header("🎓 " + translation_manager.get_text('your_progress'))
            learned_count = len(st.session_state.learned_terms)
            total_terms = len(glossary.terms)
            progress = learned_count / total_terms
            
            st.write(f"{translation_manager.get_text('learned_terms')}: **{learned_count}/{total_terms}**")
            st.progress(progress)
            
            if learned_count >= 5:
                st.success(translation_manager.get_text('progress_great').format(count=learned_count))
            elif learned_count >= 2:
                st.info(translation_manager.get_text('progress_good'))
        
        # Documentation download
        st.markdown("---")
        st.header("📄 Documentation")
        
        def read_readme_file():
            try:
                with open('readme.txt', 'r', encoding='utf-8') as file:
                    return file.read()
            except FileNotFoundError:
                return "README file not found. Please make sure 'readme.txt' exists in the same directory as app.py"
            except Exception as e:
                return f"Error reading README file: {str(e)}"
        
        readme_content = read_readme_file()
        
        st.download_button(
            label="📥 Download README.txt",
            data=readme_content,
            file_name="readme.txt",
            mime="text/plain",
            help="Download the documentation and user guide for this application",
            use_container_width=True
        )
        
        st.caption("Contains detailed instructions and information about the application")
        
        st.markdown("---")
        st.header("💡 " + translation_manager.get_text('information'))
        
        st.info("**" + translation_manager.get_text('analysis_capabilities') + ":**\n" +
                "- " + translation_manager.get_text('capability_1') + "\n" +
                "- " + translation_manager.get_text('capability_2') + "\n" + 
                "- " + translation_manager.get_text('capability_3') + "\n" +
                "- " + translation_manager.get_text('capability_4') + "\n" +
                "- " + translation_manager.get_text('capability_5') + "\n" +
                "- " + translation_manager.get_text('capability_6') + "\n" +
                "- " + translation_manager.get_text('capability_7') + "\n" +
                "- " + translation_manager.get_text('capability_8') + "\n" +
                "- **NEW:** Special Analysis metrics (CiteScore & Impact Factor)\n" +
                "- **NEW:** ROR organization data integration\n" +
                "- **NEW:** Author ID data (ORCID, Scopus ID, WoS ID)\n")
        
        st.warning("**" + translation_manager.get_text('note') + ":** \n" +
                  "- " + translation_manager.get_text('note_text_1') + "\n" +
                  "- " + translation_manager.get_text('note_text_2') + "\n" +
                  "- " + translation_manager.get_text('note_text_3') + "\n" +
                  "- " + translation_manager.get_text('note_text_4') + "\n" +
                  "- " + translation_manager.get_text('note_text_5') + "\n")
    
    # Main area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🚀 " + translation_manager.get_text('start_analysis'))
        
        # Use optimized analysis function
        if st.button("🚀 Start Optimized Analysis", type="primary", use_container_width=True):
            if not issn:
                st.error(translation_manager.get_text('issn_required'))
                return
                
            if not period and not special_analysis:
                st.error(translation_manager.get_text('period_required'))
                return
                
            with st.spinner("Starting optimized analysis with parallel processing..."):
                analyze_journal_optimized(issn, period, special_analysis, include_ror_data, include_author_id_data)
    
    with col2:
        st.subheader("📤 " + translation_manager.get_text('results'))
        
        if state.analysis_complete and state.excel_buffer is not None:
            results = state.analysis_results
            
            st.download_button(
                label="📥 " + translation_manager.get_text('download_excel_report'),
                data=state.excel_buffer,
                file_name=f"journal_analysis_{results['issn']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    # Results display (same as original)
    if state.analysis_complete:
        st.markdown("---")
        st.header("📊 " + translation_manager.get_text('analysis_results'))
        
        results = state.analysis_results

        if 'analysis_duration' in results:
            total_minutes = int(results['analysis_duration'] // 60)
            total_seconds = int(results['analysis_duration'] % 60)
            st.success(f"⏱️ Total processing time: {total_minutes}m {total_seconds}s")
        
        # Summary information
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(translation_manager.get_text('journal'), results['journal_name'])
        with col2:
            st.metric(translation_manager.get_text('issn'), results['issn'])
        with col3:
            st.metric(translation_manager.get_text('period'), results['period'])
        with col4:
            st.metric(translation_manager.get_text('articles_analyzed'), results['n_analyzed'])
        
        # Visualizations
        create_visualizations(
            results['analyzed_stats'],
            results['citing_stats'], 
            results['enhanced_stats'],
            results['citation_timing'],
            results['overlap_details'],
            results.get('fast_metrics', {}),
            results.get('additional_data', {}),
            getattr(state, 'is_special_analysis', False) or results.get('special_analysis_metrics', {}).get('is_special_analysis', False)
        )

# =============================================================================
# MAIN EXECUTION - USE OPTIMIZED VERSION
# =============================================================================

if __name__ == "__main__":
    # Use optimized version by default
    main_optimized()
