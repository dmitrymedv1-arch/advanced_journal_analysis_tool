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
from tqdm import tqdm
import sys
from datetime import datetime, timedelta
import io
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import base64
import os
import calendar
import pickle
import hashlib
import warnings
import asyncio
import aiohttp
import nest_asyncio

# Для работы async в Streamlit
try:
    nest_asyncio.apply()
except:
    pass

warnings.filterwarnings('ignore')

# --- Конфигурация страницы ---
st.set_page_config(
    page_title="Комплексный анализатор научных журналов",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Глобальные настройки ---
EMAIL = st.secrets.get("EMAIL", "your.email@example.com") if hasattr(st, 'secrets') else "your.email@example.com"
MAX_WORKERS = 5
RETRIES = 3
DELAYS = [0.2, 0.5, 0.7, 1.0, 1.3, 1.5, 2.0]

# Настройки кэша
CACHE_DIR = "journal_analysis_cache"
CACHE_DURATION = timedelta(hours=24)

# Глобальные переменные для статистики
total_requests = 0
failed_requests = 0
request_lock = threading.Lock()
last_429_warning = ""

# --- Классы для хранения состояния ---
class AnalysisState:
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

# --- Инициализация состояния ---
def initialize_analysis_state():
    if 'analysis_state' not in st.session_state:
        st.session_state.analysis_state = AnalysisState()

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

# --- Адаптивная задержка ---
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

# --- Конфигурация ---
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

# --- Функции кэширования ---
def ensure_cache_dir():
    """Создает директорию для кэша если её нет"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def get_cache_key(*args):
    """Генерирует ключ кэша на основе аргументов"""
    key_string = "_".join(str(arg) for arg in args)
    return hashlib.md5(key_string.encode()).hexdigest()

def save_to_cache(data, cache_key):
    """Сохраняет данные в кэш"""
    ensure_cache_dir()
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.pkl")
    cache_data = {
        'data': data,
        'timestamp': datetime.now()
    }
    with open(cache_file, 'wb') as f:
        pickle.dump(cache_data, f)

def load_from_cache(cache_key):
    """Загружает данные из кэша"""
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.pkl")
    if not os.path.exists(cache_file):
        return None
    try:
        with open(cache_file, 'rb') as f:
            cache_data = pickle.load(f)
        if datetime.now() - cache_data['timestamp'] < CACHE_DURATION:
            return cache_data['data']
        else:
            os.remove(cache_file)
            return None
    except:
        return None

# --- Вспомогательные функции ---
def update_progress(progress, text):
    state = get_analysis_state()
    state.current_progress = progress
    state.progress_text = text

# --- Валидация и парсинг периода ---
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
                    st.warning(f"⚠️ Диапазон вне 1900–2100 или некорректный: {part}")
            except ValueError:
                st.warning(f"⚠️ Ошибка парсинга диапазона: {part}")
        else:
            try:
                y = int(part)
                if 1900 <= y <= 2100:
                    years.add(y)
                else:
                    st.warning(f"⚠️ Год вне 1900–2100: {y}")
            except ValueError:
                st.warning(f"⚠️ Не год: {part}")
    if not years:
        st.error("❌ Нет корректных годов.")
        return []
    return sorted(years)

# --- Валидация данных ---
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
        st.warning(f"⚠️ Пропущено {skipped_count} статей из-за проблем с данными")
    return validated

# === 1. Название журнала ===
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
    return "Журнал не найден"

# === 2. Получение Crossref metadata ===
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

# === 3. Получение OpenAlex metadata ===
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

# === 4. Унифицированные метаданные ===
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

# === 5. Получение цитирующих DOI и их metadata ===
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

# === 6. Извлечение аффилиаций и стран ===
def extract_affiliations_and_countries(openalex_data):
    affiliations = set()
    countries = set()
    authors_list = []
    
    if not openalex_data:
        return authors_list, list(affiliations), list(countries)
    
    if 'authorships' in openalex_data:
        for auth in openalex_data['authorships']:
            author_name = auth.get('author', {}).get('display_name', 'Unknown')
            authors_list.append(author_name)
            
            for inst in auth.get('institutions', []):
                inst_name = inst.get('display_name')
                country_code = inst.get('country_code')
                
                if inst_name:
                    affiliations.add(inst_name)
                if country_code:
                    countries.add(country_code.upper())
    
    return authors_list, list(affiliations), list(countries)

# === 7. Извлечение информации о журнале ===
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

# === 8. Получение статей из Crossref ===
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
        st.info("📥 Начинается загрузка информации из баз данных **Crossref** и **OpenAlex**. Анализ может занять длительное время в случае большого числа анализируемых статей или цитирований. Для получения 'быстрой' статистики рекомендуется уменьшить период анализа...")
    
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
                    
                    status_text.text(f"📥 Загружено {len(items)} статей...")
                    if cursor:
                        progress = min(len(items) / (len(items) + 100), 0.95)
                        progress_bar.progress(progress)
                    
                    delayer.wait(success=True)
                    success = True
                    break
            except Exception as e:
                st.error(f"Ошибка при загрузке: {e}")
            delayer.wait(success=False)
        if not success:
            break
        if not new_items:
            break
    
    progress_bar.progress(1.0)
    status_text.text(f"✅ Загружено {len(items)} статей")
    time.sleep(0.5)
    progress_bar.empty()
    status_text.empty()
    progress_container.empty()
    
    return items

# === 9. Извлечение префикса DOI ===
def get_doi_prefix(doi):
    if not doi or doi == 'N/A':
        return ''
    return doi.split('/')[0] if '/' in doi else doi[:7]

# === 10. Обработка с прогресс-баром ===
def process_with_progress(items, func, desc="Обработка", unit="элементов"):
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(func, item): item for item in items}
        
        for i, future in enumerate(as_completed(futures)):
            try:
                results.append(future.result())
            except Exception as e:
                st.error(f"Ошибка в {desc}: {e}")
                results.append(None)
            
            progress = (i + 1) / len(items)
            progress_bar.progress(progress)
            status_text.text(f"{desc}: {i + 1}/{len(items)}")
    
    progress_bar.empty()
    status_text.empty()
    return results

# === 11. Анализ пересечений между анализируемыми и цитирующими работами ===
def analyze_overlaps(analyzed_metadata, citing_metadata, state):
    """Анализ пересечений между анализируемыми и цитирующими работами"""
    
    overlap_details = []
    
    for analyzed in analyzed_metadata:
        if not analyzed or not analyzed.get('crossref'):
            continue
            
        analyzed_doi = analyzed['crossref'].get('DOI')
        if not analyzed_doi:
            continue
            
        # Получаем авторов и аффилиации анализируемой работы
        analyzed_authors, analyzed_affiliations, _ = extract_affiliations_and_countries(analyzed.get('openalex'))
        analyzed_authors_set = set(analyzed_authors)
        analyzed_affiliations_set = set(analyzed_affiliations)
        
        # Получаем цитирующие работы
        citings = get_citing_dois_and_metadata((analyzed_doi, state))
        
        for citing in citings:
            if not citing or not citing.get('openalex'):
                continue
                
            citing_doi = citing.get('doi')
            if not citing_doi:
                continue
            
            # Получаем авторов и аффилиации цитирующей работы
            citing_authors, citing_affiliations, _ = extract_affiliations_and_countries(citing.get('openalex'))
            citing_authors_set = set(citing_authors)
            citing_affiliations_set = set(citing_affiliations)
            
            # Находим пересечения
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

# === 12. Анализ скорости накопления цитирований ===
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

# === 13. Обработка метаданных для статистики ===
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
    articles_with_50_citations = 0
    articles_with_100_citations = 0
    articles_with_200_citations = 0

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
                if citation_count >= 50:
                    articles_with_50_citations += 1
                if citation_count >= 100:
                    articles_with_100_citations += 1
                if citation_count >= 200:
                    articles_with_200_citations += 1

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
        'articles_with_50_citations': articles_with_50_citations,
        'articles_with_100_citations': articles_with_100_citations,
        'articles_with_200_citations': articles_with_200_citations,
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

# === 14. Расчет расширенной статистики ===
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

# === 15. Расчет времени до первого цитирования ===
def calculate_citation_timing_stats(analyzed_metadata, state):
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
                if days_to_first_citation >= 0:
                    all_days_to_first_citation.append(days_to_first_citation)
                    first_citation_details.append({
                        'analyzed_doi': analyzed_doi,
                        'citing_doi': first_citing_doi,
                        'analyzed_date': analyzed_date,
                        'first_citation_date': first_citation_date,
                        'days_to_first_citation': days_to_first_citation
                    })
    
    if all_days_to_first_citation:
        citation_timing_stats = {
            'min_days_to_first_citation': min(all_days_to_first_citation),
            'max_days_to_first_citation': max(all_days_to_first_citation),
            'mean_days_to_first_citation': np.mean(all_days_to_first_citation),
            'median_days_to_first_citation': np.median(all_days_to_first_citation),
            'articles_with_citation_timing_data': len(all_days_to_first_citation),
            'first_citation_details': first_citation_details
        }
    else:
        citation_timing_stats = {
            'min_days_to_first_citation': 0,
            'max_days_to_first_citation': 0,
            'mean_days_to_first_citation': 0,
            'median_days_to_first_citation': 0,
            'articles_with_citation_timing_data': 0,
            'first_citation_details': []
        }
    
    return citation_timing_stats

# === 16. КОРРЕКТНЫЙ РАСЧЕТ Impact Factor и CiteScore ===
def validate_issn(issn):
    """Проверка формата ISSN"""
    if not issn:
        return False
    pattern = r'^\d{4}-\d{3}[\dXx]$'
    return re.match(pattern, issn) is not None

def get_seasonal_coefficients(journal_field="general"):
    """Возвращает взвешенные коэффициенты на основе исторических данных"""
    seasonal_patterns = {
        "natural_sciences": {
            1: 0.85, 2: 1.05, 3: 1.25, 4: 1.15, 5: 1.00, 6: 0.95,
            7: 0.70, 8: 0.75, 9: 1.30, 10: 1.20, 11: 1.15, 12: 0.65
        },
        "general": {
            1: 0.90, 2: 1.15, 3: 1.20, 4: 1.15, 5: 1.00, 6: 1.00,
            7: 0.70, 8: 0.80, 9: 1.20, 10: 1.25, 11: 1.15, 12: 0.60
        }
    }
    return seasonal_patterns.get(journal_field, seasonal_patterns["general"])

def calculate_weighted_multiplier(current_date, seasonal_coefficients, method="balanced"):
    """Расчет взвешенного множителя"""
    current_year = current_date.year
    current_month = current_date.month
    days_passed = (current_date - date(current_year, 1, 1)).days + 1

    weighted_passed = 0
    for month in range(1, current_month + 1):
        _, month_days = calendar.monthrange(current_year, month)
        if month == current_month:
            month_days = current_date.day
        weighted_passed += seasonal_coefficients[month] * month_days

    total_weighted_year = sum(
        seasonal_coefficients[month] * calendar.monthrange(current_year, month)[1]
        for month in range(1, 13)
    )

    base_multiplier = total_weighted_year / weighted_passed if weighted_passed > 0 else 1.0

    if method == "conservative":
        return max(1.0, base_multiplier * 0.9)
    elif method == "optimistic":
        return max(1.0, base_multiplier * 1.1)
    else:
        return max(1.0, base_multiplier)

def detect_journal_field(issn, journal_name):
    """Автоматическое определение области журнала"""
    field_keywords = {
        "natural_sciences": ['nature', 'science', 'physical', 'chemistry', 'physics'],
        "general": ['general', 'techno', 'acta']
    }
    journal_name_lower = journal_name.lower()
    for field, keywords in field_keywords.items():
        for keyword in keywords:
            if keyword in journal_name_lower:
                return field
    return "general"

def calculate_correct_impact_factor_and_citescore(issn, journal_name, analyzed_metadata, state):
    """Корректный расчет Impact Factor и CiteScore по методологии из второго кода"""
    
    try:
        current_date = datetime.now().date()
        current_year = current_date.year
        journal_field = detect_journal_field(issn, journal_name)

        # Периоды для Impact Factor (публикации за 2 предыдущих года)
        if_publication_years = [current_year - 2, current_year - 1]
        
        # Периоды для CiteScore (публикации за 4 предыдущих года)
        cs_publication_years = list(range(current_year - 3, current_year + 1))

        # Фильтрация статей для IF
        if_items = []
        for meta in analyzed_metadata:
            if meta and meta.get('crossref'):
                cr = meta['crossref']
                pub_year = cr.get('published', {}).get('date-parts', [[0]])[0][0]
                if pub_year in if_publication_years:
                    if_items.append({
                        'DOI': cr.get('DOI', 'N/A'),
                        'published': {'date-parts': [[pub_year]]},
                        'is-referenced-by-count': cr.get('is-referenced-by-count', 0),
                        'crossref_data': cr,
                        'openalex_data': meta.get('openalex')
                    })

        # Фильтрация статей для CiteScore
        cs_items = []
        for meta in analyzed_metadata:
            if meta and meta.get('crossref'):
                cr = meta['crossref']
                pub_year = cr.get('published', {}).get('date-parts', [[0]])[0][0]
                if pub_year in cs_publication_years:
                    cs_items.append({
                        'DOI': cr.get('DOI', 'N/A'),
                        'published': {'date-parts': [[pub_year]]},
                        'is-referenced-by-count': cr.get('is-referenced-by-count', 0),
                        'crossref_data': cr,
                        'openalex_data': meta.get('openalex')
                    })

        B_if = len(if_items)
        B_cs = len(cs_items)
        
        st.info(f"📊 Для расчета Impact Factor: {B_if} статей за {if_publication_years}")
        st.info(f"📊 Для расчета CiteScore: {B_cs} статей за {cs_publication_years}")

        if B_if == 0 or B_cs == 0:
            st.warning("❌ Недостаточно данных для расчета метрик")
            return None

        # Расчет цитирований через OpenAlex для IF
        A_if_current = 0
        if_citation_data = []
        
        for item in if_items:
            doi = item['DOI']
            crossref_cites = item['is-referenced-by-count']
            
            if doi != 'N/A':
                # Получаем цитирования через OpenAlex
                oa_data = get_openalex_metadata(doi, state)
                if oa_data:
                    openalex_count = oa_data.get('cited_by_count', 0)
                    A_if_current += openalex_count
                    
                    if_citation_data.append({
                        'DOI': doi,
                        'Год публикации': item['published']['date-parts'][0][0],
                        'Цитирования (Crossref)': crossref_cites,
                        'Цитирования (OpenAlex)': openalex_count,
                        'Цитирования в периоде': openalex_count
                    })
                else:
                    if_citation_data.append({
                        'DOI': doi,
                        'Год публикации': item['published']['date-parts'][0][0],
                        'Цитирования (Crossref)': crossref_cites,
                        'Цитирования (OpenAlex)': 0,
                        'Цитирования в периоде': 0
                    })
            else:
                if_citation_data.append({
                    'DOI': doi,
                    'Год публикации': item['published']['date-parts'][0][0],
                    'Цитирования (Crossref)': crossref_cites,
                    'Цитирования (OpenAlex)': 0,
                    'Цитирования в периоде': 0
                })

        # Расчет цитирований для CiteScore (используем Crossref)
        A_cs_current = sum(item['is-referenced-by-count'] for item in cs_items)
        cs_citation_data = [
            {
                'DOI': item['DOI'],
                'Год публикации': item['published']['date-parts'][0][0],
                'Цитирования (Crossref)': item['is-referenced-by-count'],
                'Цитирования (OpenAlex)': 0,
                'Цитирования в периоде': 0
            } for item in cs_items
        ]

        # Расчет текущих значений
        current_if = A_if_current / B_if if B_if > 0 else 0
        current_citescore = A_cs_current / B_cs if B_cs > 0 else 0

        # Прогнозирование с учетом сезонности
        seasonal_coefficients = get_seasonal_coefficients(journal_field)
        multiplier_conservative = calculate_weighted_multiplier(current_date, seasonal_coefficients, "conservative")
        multiplier_balanced = calculate_weighted_multiplier(current_date, seasonal_coefficients, "balanced")
        multiplier_optimistic = calculate_weighted_multiplier(current_date, seasonal_coefficients, "optimistic")

        if_forecasts = {
            'conservative': current_if * multiplier_conservative,
            'balanced': current_if * multiplier_balanced,
            'optimistic': current_if * multiplier_optimistic
        }

        citescore_forecasts = {
            'conservative': current_citescore * multiplier_conservative,
            'balanced': current_citescore * multiplier_balanced,
            'optimistic': current_citescore * multiplier_optimistic
        }

        return {
            'current_if': current_if,
            'current_citescore': current_citescore,
            'if_forecasts': if_forecasts,
            'citescore_forecasts': citescore_forecasts,
            'multipliers': {
                'conservative': multiplier_conservative,
                'balanced': multiplier_balanced,
                'optimistic': multiplier_optimistic
            },
            'total_cites_if': A_if_current,
            'total_articles_if': B_if,
            'total_cites_cs': A_cs_current,
            'total_articles_cs': B_cs,
            'citation_distribution': dict(seasonal_coefficients),
            'if_citation_data': if_citation_data,
            'cs_citation_data': cs_citation_data,
            'analysis_date': current_date,
            'if_publication_years': if_publication_years,
            'cs_publication_years': cs_publication_years,
            'seasonal_coefficients': seasonal_coefficients,
            'journal_field': journal_field,
            'self_citation_rate': 0.05,
            'total_self_citations': int(A_if_current * 0.05),
            'issn': issn,
            'journal_name': journal_name
        }

    except Exception as e:
        st.error(f"❌ Ошибка при расчете метрик: {e}")
        import traceback
        traceback.print_exc()
        return None

# === 17. Расчет IF и дней (ОБНОВЛЕННАЯ ВЕРСИЯ) ===
def calculate_if_and_days(analyzed_metadata, all_citing_metadata, current_date, state, issn, journal_name):
    """Обновленная функция расчета IF с использованием корректной логики"""
    
    # Используем корректный расчет IF и CiteScore
    metrics_data = calculate_correct_impact_factor_and_citescore(issn, journal_name, analyzed_metadata, state)
    
    if not metrics_data:
        # Возвращаем значения по умолчанию в случае ошибки
        return {
            'if_value': 0.0,
            'citescore_value': 0.0,
            'c_num': 0,
            'p_den': 0,
            'cs_c_num': 0,
            'cs_p_den': 0,
            'citation_years': [],
            'publication_years': [],
            'cs_publication_years': [],
            'days_min': 0,
            'days_max': 0,
            'days_mean': 0,
            'days_median': 0,
            'articles_with_timing_data': 0,
            'first_citation_details': [],
            'accumulation_curves': {},
            'yearly_citations': [],
            'total_years_covered': 0,
            'if_forecasts': {},
            'citescore_forecasts': {},
            'multipliers': {},
            'citation_distribution': {},
            'journal_field': 'general'
        }
    
    # Расчет времени цитирования (сохраняем старую логику)
    timing_stats = calculate_citation_timing_stats(analyzed_metadata, state)
    accumulation_stats = analyze_citation_accumulation(analyzed_metadata, state)
    
    return {
        'if_value': metrics_data['current_if'],
        'citescore_value': metrics_data['current_citescore'],
        'c_num': metrics_data['total_cites_if'],
        'p_den': metrics_data['total_articles_if'],
        'cs_c_num': metrics_data['total_cites_cs'],
        'cs_p_den': metrics_data['total_articles_cs'],
        'citation_years': [current_date.year - 1, current_date.year],
        'publication_years': metrics_data['if_publication_years'],
        'cs_publication_years': metrics_data['cs_publication_years'],
        'days_min': timing_stats['min_days_to_first_citation'],
        'days_max': timing_stats['max_days_to_first_citation'],
        'days_mean': timing_stats['mean_days_to_first_citation'],
        'days_median': timing_stats['median_days_to_first_citation'],
        'articles_with_timing_data': timing_stats['articles_with_citation_timing_data'],
        'first_citation_details': timing_stats['first_citation_details'],
        'accumulation_curves': accumulation_stats['accumulation_curves'],
        'yearly_citations': accumulation_stats['yearly_citations'],
        'total_years_covered': accumulation_stats['total_years_covered'],
        'if_forecasts': metrics_data['if_forecasts'],
        'citescore_forecasts': metrics_data['citescore_forecasts'],
        'multipliers': metrics_data['multipliers'],
        'citation_distribution': metrics_data['citation_distribution'],
        'journal_field': metrics_data['journal_field']
    }

# === 18. Создание расширенного Excel отчета (ОБНОВЛЕННАЯ ВЕРСИЯ) ===
def create_enhanced_excel_report(analyzed_data, citing_data, analyzed_stats, citing_stats, enhanced_stats, if_days, overlap_details, filename):
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Лист 1: Анализируемые статьи
        analyzed_list = []
        for item in analyzed_data:
            if item and item.get('crossref'):
                cr = item['crossref']
                oa = item.get('openalex', {})
                authors_list, affiliations_list, countries_list = extract_affiliations_and_countries(oa)
                journal_info = extract_journal_info(item)
                
                analyzed_list.append({
                    'DOI': cr.get('DOI', ''),
                    'Название': cr.get('title', [''])[0] if cr.get('title') else 'Без названия',
                    'Авторы_Crossref': '; '.join([f"{a.get('given', '')} {a.get('family', '')}" for a in cr.get('author', [])]),
                    'Авторы_OpenAlex': '; '.join(authors_list),
                    'Аффилиации': '; '.join(affiliations_list),
                    'Страны': '; '.join(countries_list),
                    'Год публикации': cr.get('published', {}).get('date-parts', [[0]])[0][0],
                    'Журнал': journal_info['journal_name'],
                    'Издатель': journal_info['publisher'],
                    'ISSN': '; '.join(journal_info['issn']),
                    'Количество ссылок': cr.get('reference-count', 0),
                    'Цитирования Crossref': cr.get('is-referenced-by-count', 0),
                    'Цитирования OpenAlex': oa.get('cited_by_count', 0),
                    'Количество авторов': len(cr.get('author', [])),
                    'Тип работы': cr.get('type', '')
                })
        
        if analyzed_list:
            analyzed_df = pd.DataFrame(analyzed_list)
            analyzed_df.to_excel(writer, sheet_name='Анализируемые_статьи', index=False)

        # Лист 2: Цитирующие работы
        citing_list = []
        for item in citing_data:
            if item and item.get('crossref'):
                cr = item['crossref']
                oa = item.get('openalex', {})
                authors_list, affiliations_list, countries_list = extract_affiliations_and_countries(oa)
                journal_info = extract_journal_info(item)
                
                citing_list.append({
                    'DOI': cr.get('DOI', ''),
                    'Название': cr.get('title', [''])[0] if cr.get('title') else 'Без названия',
                    'Авторы_Crossref': '; '.join([f"{a.get('given', '')} {a.get('family', '')}" for a in cr.get('author', [])]),
                    'Авторы_OpenAlex': '; '.join(authors_list),
                    'Аффилиации': '; '.join(affiliations_list),
                    'Страны': '; '.join(countries_list),
                    'Год публикации': cr.get('published', {}).get('date-parts', [[0]])[0][0],
                    'Журнал': journal_info['journal_name'],
                    'Издатель': journal_info['publisher'],
                    'ISSN': '; '.join(journal_info['issn']),
                    'Количество ссылок': cr.get('reference-count', 0),
                    'Цитирования Crossref': cr.get('is-referenced-by-count', 0),
                    'Цитирования OpenAlex': oa.get('cited_by_count', 0),
                    'Количество авторов': len(cr.get('author', [])),
                    'Тип работы': cr.get('type', '')
                })
        
        if citing_list:
            citing_df = pd.DataFrame(citing_list)
            citing_df.to_excel(writer, sheet_name='Цитирующие_работы', index=False)

        # Лист 3: Пересечения анализируемых и цитирующих работ
        overlap_list = []
        for overlap in overlap_details:
            overlap_list.append({
                'DOI анализируемой работы': overlap['analyzed_doi'],
                'DOI цитирующей работы': overlap['citing_doi'],
                'Совпадающие авторы': '; '.join(overlap['common_authors']),
                'Количество совпадающих авторов': overlap['common_authors_count'],
                'Совпадающие аффилиации': '; '.join(overlap['common_affiliations']),
                'Количество совпадающих аффилиаций': overlap['common_affiliations_count']
            })
        
        if overlap_list:
            overlap_df = pd.DataFrame(overlap_list)
            overlap_df.to_excel(writer, sheet_name='Пересечения_работ', index=False)

        # Лист 4: Время до первого цитирования
        first_citation_list = []
        for detail in if_days.get('first_citation_details', []):
            first_citation_list.append({
                'DOI анализируемой работы': detail['analyzed_doi'],
                'DOI первой цитирующей работы': detail['citing_doi'],
                'Дата публикации': detail['analyzed_date'].strftime('%Y-%m-%d'),
                'Дата первого цитирования': detail['first_citation_date'].strftime('%Y-%m-%d'),
                'Дней до первого цитирования': detail['days_to_first_citation']
            })
        
        if first_citation_list:
            first_citation_df = pd.DataFrame(first_citation_list)
            first_citation_df.to_excel(writer, sheet_name='Первые_цитирования', index=False)

        # Лист 5: Статистика анализируемых статей
        analyzed_stats_data = {
            'Метрика': [
                'Всего статей', 
                'Общее количество ссылок', 
                'Ссылки с DOI', 'Количество ссылок с DOI', 'Процент ссылок с DOI',
                'Ссылки без DOI', 'Количество ссылок без DOI', 'Процент ссылок без DOI',
                'Самоцитирования', 'Количество самоцитирований', 'Процент самоцитирований',
                'Статьи с одним автором',
                'Статьи с >10 авторами', 
                'Минимальное число ссылок', 
                'Максимальное число ссылок', 
                'Среднее число ссылок',
                'Медиана ссылок', 
                'Минимальное число авторов',
                'Максимальное число авторов', 
                'Среднее число авторов',
                'Медиана авторов', 
                'Статьи из одной страны', 'Процент статей из одной страны',
                'Статьи из нескольких стран', 'Процент статей из нескольких стран',
                'Статьи без данных о странах', 'Процент статей без данных о странах',
                'Всего аффилиаций',
                'Уникальных аффилиаций', 
                'Уникальных стран',
                'Уникальных журналов',
                'Уникальных издателей',
                'Статьи с ≥10 цитированиями',
                'Статьи с ≥50 цитированиями',
                'Статьи с ≥100 цитированиями',
                'Статьи с ≥200 цитированиями'
            ],
            'Значение': [
                analyzed_stats['n_items'],
                analyzed_stats['total_refs'],
                'Ссылки с DOI', analyzed_stats['refs_with_doi'], f"{analyzed_stats['refs_with_doi_pct']:.1f}%",
                'Ссылки без DOI', analyzed_stats['refs_without_doi'], f"{analyzed_stats['refs_without_doi_pct']:.1f}%",
                'Самоцитирования', analyzed_stats['self_cites'], f"{analyzed_stats['self_cites_pct']:.1f}%",
                analyzed_stats['single_authors'],
                analyzed_stats['multi_authors_gt10'],
                analyzed_stats['ref_min'],
                analyzed_stats['ref_max'],
                f"{analyzed_stats['ref_mean']:.1f}",
                analyzed_stats['ref_median'],
                analyzed_stats['auth_min'],
                analyzed_stats['auth_max'],
                f"{analyzed_stats['auth_mean']:.1f}",
                analyzed_stats['auth_median'],
                analyzed_stats['single_country_articles'], f"{analyzed_stats['single_country_pct']:.1f}%",
                analyzed_stats['multi_country_articles'], f"{analyzed_stats['multi_country_pct']:.1f}%",
                analyzed_stats['no_country_articles'], f"{analyzed_stats['no_country_pct']:.1f}%",
                analyzed_stats['total_affiliations_count'],
                analyzed_stats['unique_affiliations_count'],
                analyzed_stats['unique_countries_count'],
                analyzed_stats['unique_journals_count'],
                analyzed_stats['unique_publishers_count'],
                analyzed_stats['articles_with_10_citations'],
                analyzed_stats['articles_with_50_citations'],
                analyzed_stats['articles_with_100_citations'],
                analyzed_stats['articles_with_200_citations']
            ]
        }
        analyzed_stats_df = pd.DataFrame(analyzed_stats_data)
        analyzed_stats_df.to_excel(writer, sheet_name='Статистика_анализируемых', index=False)

        # Лист 6: Статистика цитирующих статей
        citing_stats_data = {
            'Метрика': [
                'Всего цитирующих статей', 
                'Общее количество ссылок', 
                'Ссылки с DOI', 'Количество ссылок с DOI', 'Процент ссылок с DOI',
                'Ссылки без DOI', 'Количество ссылок без DOI', 'Процент ссылок без DOI',
                'Самоцитирования', 'Количество самоцитирований', 'Процент самоцитирований',
                'Статьи с одним автором',
                'Статьи с >10 авторами', 
                'Минимальное число ссылок', 
                'Максимальное число ссылок', 
                'Среднее число ссылок',
                'Медиана ссылок', 
                'Минимальное число авторов',
                'Максимальное число авторов', 
                'Среднее число авторов',
                'Медиана авторов', 
                'Статьи из одной страны', 'Процент статей из одной страны',
                'Статьи из нескольких стран', 'Процент статей из нескольких стран',
                'Статьи без данных о странах', 'Процент статей без данных о странах',
                'Всего аффилиаций',
                'Уникальных аффилиаций', 
                'Уникальных стран',
                'Уникальных журналов',
                'Уникальных издателей'
            ],
            'Значение': [
                citing_stats['n_items'],
                citing_stats['total_refs'],
                'Ссылки с DOI', citing_stats['refs_with_doi'], f"{citing_stats['refs_with_doi_pct']:.1f}%",
                'Ссылки без DOI', citing_stats['refs_without_doi'], f"{citing_stats['refs_without_doi_pct']:.1f}%",
                'Самоцитирования', citing_stats['self_cites'], f"{citing_stats['self_cites_pct']:.1f}%",
                citing_stats['single_authors'],
                citing_stats['multi_authors_gt10'],
                citing_stats['ref_min'],
                citing_stats['ref_max'],
                f"{citing_stats['ref_mean']:.1f}",
                citing_stats['ref_median'],
                citing_stats['auth_min'],
                citing_stats['auth_max'],
                f"{citing_stats['auth_mean']:.1f}",
                citing_stats['auth_median'],
                citing_stats['single_country_articles'], f"{citing_stats['single_country_pct']:.1f}%",
                citing_stats['multi_country_articles'], f"{citing_stats['multi_country_pct']:.1f}%",
                citing_stats['no_country_articles'], f"{citing_stats['no_country_pct']:.1f}%",
                citing_stats['total_affiliations_count'],
                citing_stats['unique_affiliations_count'],
                citing_stats['unique_countries_count'],
                citing_stats['unique_journals_count'],
                citing_stats['unique_publishers_count']
            ]
        }
        citing_stats_df = pd.DataFrame(citing_stats_data)
        citing_stats_df.to_excel(writer, sheet_name='Статистика_цитирующих', index=False)

        # Лист 7: Расширенная статистика
        enhanced_stats_data = {
            'Метрика': [
                'H-index', 'Общее количество цитирований',
                'Среднее цитирований на статью', 'Максимальное цитирований',
                'Минимальное цитирований', 'Статьи с цитированиями',
                'Статьи без цитирований'
            ],
            'Значение': [
                enhanced_stats['h_index'],
                enhanced_stats['total_citations'],
                f"{enhanced_stats['avg_citations_per_article']:.1f}",
                enhanced_stats['max_citations'],
                enhanced_stats['min_citations'],
                enhanced_stats['articles_with_citations'],
                enhanced_stats['articles_without_citations']
            ]
        }
        enhanced_stats_df = pd.DataFrame(enhanced_stats_data)
        enhanced_stats_df.to_excel(writer, sheet_name='Расширенная_статистика', index=False)

        # Лист 8: Impact Factor, CiteScore и время цитирования (ОБНОВЛЕННЫЙ)
        if_days_data = {
            'Метрика': [
                'Impact Factor (текущий)', 
                'Impact Factor (консервативный прогноз)',
                'Impact Factor (сбалансированный прогноз)',
                'Impact Factor (оптимистичный прогноз)',
                'CiteScore (текущий)',
                'CiteScore (консервативный прогноз)',
                'CiteScore (сбалансированный прогноз)',
                'CiteScore (оптимистичный прогноз)',
                'Числитель IF (цитирования)', 
                'Знаменатель IF (публикации)', 
                'Числитель CiteScore (цитирования)',
                'Знаменатель CiteScore (публикации)',
                'Годы публикаций для IF',
                'Годы публикаций для CiteScore',
                'Минимальные дни до первого цитирования',
                'Максимальные дни до первого цитирования', 
                'Средние дни до первого цитирования',
                'Медиана дней до первого цитирования', 
                'Статьи с данными о времени цитирования',
                'Всего лет покрыто данными о цитированиях',
                'Область журнала',
                'Множитель (консервативный)',
                'Множитель (сбалансированный)',
                'Множитель (оптимистичный)'
            ],
            'Значение': [
                f"{if_days.get('if_value', 0):.4f}",
                f"{if_days.get('if_forecasts', {}).get('conservative', 0):.4f}",
                f"{if_days.get('if_forecasts', {}).get('balanced', 0):.4f}",
                f"{if_days.get('if_forecasts', {}).get('optimistic', 0):.4f}",
                f"{if_days.get('citescore_value', 0):.4f}",
                f"{if_days.get('citescore_forecasts', {}).get('conservative', 0):.4f}",
                f"{if_days.get('citescore_forecasts', {}).get('balanced', 0):.4f}",
                f"{if_days.get('citescore_forecasts', {}).get('optimistic', 0):.4f}",
                if_days.get('c_num', 0),
                if_days.get('p_den', 0),
                if_days.get('cs_c_num', 0),
                if_days.get('cs_p_den', 0),
                f"{if_days.get('publication_years', ['N/A', 'N/A'])[0] if if_days.get('publication_years') else 'N/A'}-{if_days.get('publication_years', ['N/A', 'N/A'])[1] if if_days.get('publication_years') and len(if_days['publication_years']) > 1 else 'N/A'}",
                f"{if_days.get('cs_publication_years', ['N/A', 'N/A'])[0] if if_days.get('cs_publication_years') else 'N/A'}-{if_days.get('cs_publication_years', ['N/A', 'N/A'])[-1] if if_days.get('cs_publication_years') else 'N/A'}",
                if_days.get('days_min', 0),
                if_days.get('days_max', 0),
                f"{if_days.get('days_mean', 0):.1f}",
                if_days.get('days_median', 0),
                if_days.get('articles_with_timing_data', 0),
                if_days.get('total_years_covered', 0),
                if_days.get('journal_field', 'general'),
                f"{if_days.get('multipliers', {}).get('conservative', 1):.2f}",
                f"{if_days.get('multipliers', {}).get('balanced', 1):.2f}",
                f"{if_days.get('multipliers', {}).get('optimistic', 1):.2f}"
            ]
        }
        if_days_df = pd.DataFrame(if_days_data)
        if_days_df.to_excel(writer, sheet_name='Impact_Factor_CiteScore_Время', index=False)

        # Лист 9: Цитирования по годам
        yearly_citations_data = []
        for yearly_stat in if_days.get('yearly_citations', []):
            yearly_citations_data.append({
                'Год': yearly_stat.get('year', 0),
                'Количество цитирований': yearly_stat.get('citations_count', 0)
            })
        
        if yearly_citations_data:
            yearly_citations_df = pd.DataFrame(yearly_citations_data)
            yearly_citations_df.to_excel(writer, sheet_name='Цитирования_по_годам', index=False)

        # Лист 10: Кривые накопления цитирований
        accumulation_data = []
        for pub_year, curve_data in if_days.get('accumulation_curves', {}).items():
            for data_point in curve_data:
                accumulation_data.append({
                    'Год публикации': pub_year,
                    'Лет после публикации': data_point.get('years_since_publication', 0),
                    'Накопительные цитирования': data_point.get('cumulative_citations', 0)
                })
        
        if accumulation_data:
            accumulation_df = pd.DataFrame(accumulation_data)
            accumulation_df.to_excel(writer, sheet_name='Кривые_накопления_цитирований', index=False)

        # Лист 11: Сеть цитирований
        citation_network_data = []
        for year, citing_years in enhanced_stats.get('citation_network', {}).items():
            year_counts = Counter(citing_years)
            for citing_year, count in year_counts.items():
                citation_network_data.append({
                    'Год публикации': year,
                    'Год цитирования': citing_year,
                    'Количество цитирований': count
                })
        
        if citation_network_data:
            citation_network_df = pd.DataFrame(citation_network_data)
            citation_network_df.to_excel(writer, sheet_name='Сеть_цитирований', index=False)

        # Лист 12: Все авторы анализируемых
        all_authors_data = {
            'Автор': [author[0] for author in analyzed_stats['all_authors']],
            'Количество статей': [author[1] for author in analyzed_stats['all_authors']]
        }
        all_authors_df = pd.DataFrame(all_authors_data)
        all_authors_df.to_excel(writer, sheet_name='Все_авторы_анализируемые', index=False)

        # Лист 13: Все авторы цитирующих
        all_citing_authors_data = {
            'Автор': [author[0] for author in citing_stats['all_authors']],
            'Количество статей': [author[1] for author in citing_stats['all_authors']]
        }
        all_citing_authors_df = pd.DataFrame(all_citing_authors_data)
        all_citing_authors_df.to_excel(writer, sheet_name='Все_авторы_цитирующие', index=False)

        # Лист 14: Все аффилиации анализируемых
        all_affiliations_data = {
            'Аффилиация': [aff[0] for aff in analyzed_stats['all_affiliations']],
            'Количество упоминаний': [aff[1] for aff in analyzed_stats['all_affiliations']]
        }
        all_affiliations_df = pd.DataFrame(all_affiliations_data)
        all_affiliations_df.to_excel(writer, sheet_name='Все_аффилиации_анализируемые', index=False)

        # Лист 15: Все аффилиации цитирующих
        all_citing_affiliations_data = {
            'Аффилиация': [aff[0] for aff in citing_stats['all_affiliations']],
            'Количество упоминаний': [aff[1] for aff in citing_stats['all_affiliations']]
        }
        all_citing_affiliations_df = pd.DataFrame(all_citing_affiliations_data)
        all_citing_affiliations_df.to_excel(writer, sheet_name='Все_аффилиации_цитирующие', index=False)

        # Лист 16: Все страны анализируемых
        all_countries_data = {
            'Страна': [country[0] for country in analyzed_stats['all_countries']],
            'Количество упоминаний': [country[1] for country in analyzed_stats['all_countries']]
        }
        all_countries_df = pd.DataFrame(all_countries_data)
        all_countries_df.to_excel(writer, sheet_name='Все_страны_анализируемые', index=False)

        # Лист 17: Все страны цитирующих
        all_citing_countries_data = {
            'Страна': [country[0] for country in citing_stats['all_countries']],
            'Количество упоминаний': [country[1] for country in citing_stats['all_countries']]
        }
        all_citing_countries_df = pd.DataFrame(all_citing_countries_data)
        all_citing_countries_df.to_excel(writer, sheet_name='Все_страны_цитирующие', index=False)

        # Лист 18: Все журналы цитирующих (ИЗМЕНЕНО - теперь только цитирующие журналы)
        all_citing_journals_data = {
            'Журнал': [journal[0] for journal in citing_stats['all_journals']],
            'Количество статей': [journal[1] for journal in citing_stats['all_journals']]
        }
        all_citing_journals_df = pd.DataFrame(all_citing_journals_data)
        all_citing_journals_df.to_excel(writer, sheet_name='Все_журналы_цитирующие', index=False)

        # Лист 19: Все издатели цитирующих (ИЗМЕНЕНО - теперь только цитирующие издатели)
        all_citing_publishers_data = {
            'Издатель': [publisher[0] for publisher in citing_stats['all_publishers']],
            'Количество статей': [publisher[1] for publisher in citing_stats['all_publishers']]
        }
        all_citing_publishers_df = pd.DataFrame(all_citing_publishers_data)
        all_citing_publishers_df.to_excel(writer, sheet_name='Все_издатели_цитирующие', index=False)

    return filename

# === 19. Визуализация данных (ОБНОВЛЕННАЯ ВЕРСИЯ) ===
def create_visualizations(analyzed_stats, citing_stats, enhanced_stats, if_days, overlap_details):
    """Создание визуализаций для дашборда"""
    
    # Создаем вкладки для разных типов визуализаций
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📈 Основные метрики", 
        "👥 Авторы и организации", 
        "🌍 География", 
        "📊 Цитирования",
        "🔀 Пересечения",
        "⏱️ Время цитирования",
        "🎯 IF & CiteScore"
    ])
    
    with tab1:
        st.subheader("📈 Ключевые метрики журнала")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Impact Factor", 
                f"{if_days.get('if_value', 0):.4f}",
                help=f"Расчет для публикаций {if_days.get('publication_years', [0, 0])[0]}-{if_days.get('publication_years', [0, 0])[1]}"
            )
        with col2:
            st.metric(
                "CiteScore", 
                f"{if_days.get('citescore_value', 0):.4f}",
                help=f"Расчет для публикаций {if_days.get('cs_publication_years', [0, 0])[0]}-{if_days.get('cs_publication_years', [0, 0])[-1]}"
            )
        with col3:
            st.metric("H-index", enhanced_stats.get('h_index', 0))
        with col4:
            st.metric("Всего статей", analyzed_stats.get('n_items', 0))
        
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.metric("Среднее цитирований", f"{enhanced_stats.get('avg_citations_per_article', 0):.1f}")
        with col6:
            st.metric("Статьи с цитированиями", enhanced_stats.get('articles_with_citations', 0))
        with col7:
            st.metric("Самоцитирования", f"{analyzed_stats.get('self_cites_pct', 0):.1f}%")
        with col8:
            st.metric("Международные статьи", f"{analyzed_stats.get('multi_country_pct', 0):.1f}%")
        
        # График цитирований по годам
        if if_days.get('yearly_citations'):
            years = [item.get('year', 0) for item in if_days['yearly_citations']]
            citations = [item.get('citations_count', 0) for item in if_days['yearly_citations']]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=years, 
                y=citations, 
                name='Цитирования',
                marker_color='lightblue'
            ))
            fig.update_layout(
                title='Цитирования по годам',
                xaxis_title='Год',
                yaxis_title='Количество цитирований',
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("👥 Анализ авторов и организаций")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Топ авторов анализируемых статей
            if analyzed_stats.get('all_authors'):
                top_authors = analyzed_stats['all_authors'][:15]
                authors_df = pd.DataFrame(top_authors, columns=['Автор', 'Статей'])
                fig = px.bar(
                    authors_df, 
                    x='Статей', 
                    y='Автор', 
                    orientation='h',
                    title='Топ-15 авторов анализируемых статей'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Распределение количества авторов
            author_counts_data = {
                'Категория': ['1 автор', '2-5 авторов', '6-10 авторов', '>10 авторов'],
                'Статьи': [
                    analyzed_stats.get('single_authors', 0),
                    analyzed_stats.get('n_items', 0) - analyzed_stats.get('single_authors', 0) - analyzed_stats.get('multi_authors_gt10', 0),
                    analyzed_stats.get('multi_authors_gt10', 0),
                    0  # Можно добавить дополнительную категоризацию
                ]
            }
            fig = px.pie(
                author_counts_data, 
                values='Статьи', 
                names='Категория',
                title='Распределение по количеству авторов'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Топ аффилиаций
        if analyzed_stats.get('all_affiliations'):
            top_affiliations = analyzed_stats['all_affiliations'][:10]
            aff_df = pd.DataFrame(top_affiliations, columns=['Аффилиация', 'Упоминаний'])
            fig = px.bar(
                aff_df, 
                x='Упоминаний', 
                y='Аффилиация', 
                orientation='h',
                title='Топ-10 аффилиаций анализируемых статей',
                color='Упоминаний'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("🌍 Географическое распределение")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Распределение по странам
            if analyzed_stats.get('all_countries'):
                countries_df = pd.DataFrame(analyzed_stats['all_countries'], columns=['Страна', 'Статей'])
                fig = px.pie(
                    countries_df, 
                    values='Статей', 
                    names='Страна',
                    title='Распределение статей по странам'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Международная коллаборация
            collaboration_data = {
                'Тип': ['Одна страна', 'Несколько стран', 'Нет данных'],
                'Статьи': [
                    analyzed_stats.get('single_country_articles', 0),
                    analyzed_stats.get('multi_country_articles', 0),
                    analyzed_stats.get('no_country_articles', 0)
                ]
            }
            fig = px.bar(
                collaboration_data, 
                x='Тип', 
                y='Статьи',
                title='Международная коллаборация',
                color='Тип'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("📊 Анализ цитирований")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Цитирования по порогам
            citation_thresholds = {
                'Порог': ['≥10', '≥50', '≥100', '≥200'],
                'Статьи': [
                    analyzed_stats.get('articles_with_10_citations', 0),
                    analyzed_stats.get('articles_with_50_citations', 0),
                    analyzed_stats.get('articles_with_100_citations', 0),
                    analyzed_stats.get('articles_with_200_citations', 0)
                ]
            }
            fig = px.bar(
                citation_thresholds, 
                x='Порог', 
                y='Статьи',
                title='Статьи по порогам цитирований',
                color='Порог'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Статьи с/без цитирований
            citation_status = {
                'Статус': ['С цитированиями', 'Без цитирований'],
                'Количество': [
                    enhanced_stats.get('articles_with_citations', 0),
                    enhanced_stats.get('articles_without_citations', 0)
                ]
            }
            fig = px.pie(
                citation_status, 
                values='Количество', 
                names='Статус',
                title='Распределение статей по наличию цитирований'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.subheader("🔀 Пересечения между анализируемыми и цитирующими работами")
        
        if overlap_details:
            # Сводная статистика по пересечениям
            total_overlaps = len(overlap_details)
            articles_with_overlaps = len(set([o.get('analyzed_doi', '') for o in overlap_details]))
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Всего пересечений", total_overlaps)
            with col2:
                st.metric("Статей с пересечениями", articles_with_overlaps)
            with col3:
                avg_overlaps = total_overlaps / articles_with_overlaps if articles_with_overlaps > 0 else 0
                st.metric("Среднее пересечений на статью", f"{avg_overlaps:.1f}")
            
            # Распределение по количеству пересечений
            overlap_counts = [o.get('common_authors_count', 0) + o.get('common_affiliations_count', 0) for o in overlap_details]
            if overlap_counts:
                fig = px.histogram(
                    x=overlap_counts,
                    title='Распределение пересечений по количеству',
                    labels={'x': 'Количество пересечений', 'y': 'Частота'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Таблица с деталями пересечений
            st.subheader("Детали пересечений")
            overlap_df = pd.DataFrame(overlap_details)
            st.dataframe(overlap_df[['analyzed_doi', 'citing_doi', 'common_authors_count', 'common_affiliations_count']])
        else:
            st.info("❌ Пересечения между анализируемыми и цитирующими работами не найдены")
    
    with tab6:
        st.subheader("⏱️ Анализ времени цитирования")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Мин. дней до цитирования", if_days.get('days_min', 0))
        with col2:
            st.metric("Макс. дней до цитирования", if_days.get('days_max', 0))
        with col3:
            st.metric("Среднее дней", f"{if_days.get('days_mean', 0):.1f}")
        with col4:
            st.metric("Медиана дней", if_days.get('days_median', 0))
        
        # Детали первых цитирований
        if if_days.get('first_citation_details'):
            st.subheader("Детали первых цитирований")
            first_citation_df = pd.DataFrame(if_days['first_citation_details'])
            st.dataframe(first_citation_df)
            
            # Гистограмма времени до первого цитирования
            days_data = [d.get('days_to_first_citation', 0) for d in if_days['first_citation_details']]
            fig = px.histogram(
                x=days_data,
                title='Распределение времени до первого цитирования (дни)',
                labels={'x': 'Дни до первого цитирования', 'y': 'Количество статей'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab7:
        st.subheader("🎯 Impact Factor и CiteScore - детальный анализ")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Impact Factor")
            st.metric("Текущий IF", f"{if_days.get('if_value', 0):.4f}")
            st.metric("Числитель (цитирования)", if_days.get('c_num', 0))
            st.metric("Знаменатель (публикации)", if_days.get('p_den', 0))
            st.metric("Годы публикаций", f"{if_days.get('publication_years', ['N/A', 'N/A'])[0] if if_days.get('publication_years') else 'N/A'}-{if_days.get('publication_years', ['N/A', 'N/A'])[1] if if_days.get('publication_years') and len(if_days['publication_years']) > 1 else 'N/A'}")
            
            st.markdown("##### Прогнозы IF")
            forecast_data = {
                'Тип прогноза': ['Консервативный', 'Сбалансированный', 'Оптимистичный'],
                'Значение IF': [
                    if_days.get('if_forecasts', {}).get('conservative', 0),
                    if_days.get('if_forecasts', {}).get('balanced', 0),
                    if_days.get('if_forecasts', {}).get('optimistic', 0)
                ],
                'Множитель': [
                    if_days.get('multipliers', {}).get('conservative', 1),
                    if_days.get('multipliers', {}).get('balanced', 1),
                    if_days.get('multipliers', {}).get('optimistic', 1)
                ]
            }
            forecast_df = pd.DataFrame(forecast_data)
            st.dataframe(forecast_df)
        
        with col2:
            st.markdown("##### CiteScore")
            st.metric("Текущий CiteScore", f"{if_days.get('citescore_value', 0):.4f}")
            st.metric("Числитель (цитирования)", if_days.get('cs_c_num', 0))
            st.metric("Знаменатель (публикации)", if_days.get('cs_p_den', 0))
            st.metric("Годы публикаций CiteScore", f"{if_days.get('cs_publication_years', ['N/A', 'N/A'])[0] if if_days.get('cs_publication_years') else 'N/A'}-{if_days.get('cs_publication_years', ['N/A', 'N/A'])[-1] if if_days.get('cs_publication_years') else 'N/A'}")
            
            st.markdown("##### Прогнозы CiteScore")
            cs_forecast_data = {
                'Тип прогноза': ['Консервативный', 'Сбалансированный', 'Оптимистичный'],
                'Значение CiteScore': [
                    if_days.get('citescore_forecasts', {}).get('conservative', 0),
                    if_days.get('citescore_forecasts', {}).get('balanced', 0),
                    if_days.get('citescore_forecasts', {}).get('optimistic', 0)
                ],
                'Множитель': [
                    if_days.get('multipliers', {}).get('conservative', 1),
                    if_days.get('multipliers', {}).get('balanced', 1),
                    if_days.get('multipliers', {}).get('optimistic', 1)
                ]
            }
            cs_forecast_df = pd.DataFrame(cs_forecast_data)
            st.dataframe(cs_forecast_df)
        
        # График сезонности цитирований
        if if_days.get('citation_distribution'):
            months = list(range(1, 13))
            coefficients = [if_days['citation_distribution'].get(month, 1) for month in months]
            month_names = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=month_names,
                y=coefficients,
                name='Коэффициент цитирований',
                marker_color='orange'
            ))
            fig.update_layout(
                title='Сезонность цитирований по месяцам',
                xaxis_title='Месяц',
                yaxis_title='Коэффициент',
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

# === 20. Основная функция анализа (ОБНОВЛЕННАЯ) ===
def analyze_journal(issn, period_str):
    global delayer
    delayer = AdaptiveDelayer()
    
    state = get_analysis_state()
    state.analysis_complete = False
    
    # Общий прогресс
    overall_progress = st.progress(0)
    overall_status = st.empty()
    
    # Парсинг периода
    overall_status.text("📅 Парсинг периода...")
    years = parse_period(period_str)
    if not years:
        return
    from_date = f"{min(years)}-01-01"
    until_date = f"{max(years)}-12-31"
    overall_progress.progress(0.1)
    
    # Название журнала
    overall_status.text("📖 Получение названия журнала...")
    journal_name = get_journal_name(issn)
    st.success(f"📖 Журнал: **{journal_name}** (ISSN: {issn})")
    overall_progress.progress(0.2)
    
    # Получение статей
    overall_status.text("📥 Загрузка статей из Crossref...")
    items = fetch_articles_by_issn_period(issn, from_date, until_date)
    if not items:
        st.error("❌ Статьи не найдены.")
        return

    n_analyzed = len(items)
    st.success(f"📄 Найдено анализируемых статей: **{n_analyzed}**")
    overall_progress.progress(0.3)
    
    # Валидация данных
    overall_status.text("🔍 Валидация данных...")
    validated_items = validate_and_clean_data(items)
    journal_prefix = get_doi_prefix(validated_items[0].get('DOI', '')) if validated_items else ''
    overall_progress.progress(0.4)
    
    # Обработка анализируемых статей
    overall_status.text("🔄 Обработка анализируемых статей...")
    
    analyzed_metadata = []
    dois = [item.get('DOI') for item in validated_items if item.get('DOI')]
    
    # Прогресс-бар для обработки метаданных
    meta_progress = st.progress(0)
    meta_status = st.empty()
    
    # Подготавливаем аргументы для потоков
    args_list = [(doi, state) for doi in dois]
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(get_unified_metadata, args): args for args in args_list}
        
        for i, future in enumerate(as_completed(futures)):
            args = futures[future]
            doi = args[0]
            try:
                result = future.result()
                analyzed_metadata.append({
                    'doi': doi,
                    'crossref': result['crossref'],
                    'openalex': result['openalex']
                })
            except Exception as e:
                st.error(f"Ошибка при обработке DOI {doi}: {e}")
            
            progress = (i + 1) / len(dois)
            meta_progress.progress(progress)
            meta_status.text(f"Получение метаданных: {i + 1}/{len(dois)}")
    
    meta_progress.empty()
    meta_status.empty()
    overall_progress.progress(0.6)
    
    # Получение цитирующих работ
    overall_status.text("🔗 Сбор цитирующих работ...")
    
    all_citing_metadata = []
    analyzed_dois = [am['doi'] for am in analyzed_metadata if am.get('doi')]
    
    # Прогресс-бар для сбора цитирований
    citing_progress = st.progress(0)
    citing_status = st.empty()
    
    # Подготавливаем аргументы для потоков
    citing_args_list = [(doi, state) for doi in analyzed_dois]
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(get_citing_dois_and_metadata, args): args for args in citing_args_list}
        
        for i, future in enumerate(as_completed(futures)):
            args = futures[future]
            doi = args[0]
            try:
                citings = future.result()
                all_citing_metadata.extend(citings)
            except Exception as e:
                st.error(f"Ошибка при сборе цитирований для {doi}: {e}")
            
            progress = (i + 1) / len(analyzed_dois)
            citing_progress.progress(progress)
            citing_status.text(f"Сбор цитирований: {i + 1}/{len(analyzed_dois)}")
    
    citing_progress.empty()
    citing_status.empty()
    
    # Уникальные цитирующие работы
    unique_citing_dois = set(c['doi'] for c in all_citing_metadata if c.get('doi'))
    n_citing = len(unique_citing_dois)
    st.success(f"📄 Уникальных цитирующих работ: **{n_citing}**")
    overall_progress.progress(0.8)
    
    # Расчет статистики
    overall_status.text("📊 Расчет статистики...")
    
    analyzed_stats = extract_stats_from_metadata(analyzed_metadata, journal_prefix=journal_prefix)
    citing_stats = extract_stats_from_metadata(all_citing_metadata, is_analyzed=False)
    enhanced_stats = enhanced_stats_calculation(analyzed_metadata, all_citing_metadata, state)
    
    # Анализ пересечений
    overlap_details = analyze_overlaps(analyzed_metadata, all_citing_metadata, state)
    
    current_date = datetime.now()
    if_days = calculate_if_and_days(analyzed_metadata, all_citing_metadata, current_date, state, issn, journal_name)
    
    overall_progress.progress(0.9)
    
    # Создание отчета
    overall_status.text("💾 Создание отчета...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'journal_analysis_{issn}_{timestamp}.xlsx'
    
    # Создаем Excel файл в памяти
    excel_buffer = io.BytesIO()
    create_enhanced_excel_report(analyzed_metadata, all_citing_metadata, analyzed_stats, citing_stats, enhanced_stats, if_days, overlap_details, excel_buffer)
    
    excel_buffer.seek(0)
    state.excel_buffer = excel_buffer
    
    overall_progress.progress(1.0)
    overall_status.text("✅ Анализ завершен!")
    
    # Сохраняем результаты
    state.analysis_results = {
        'analyzed_stats': analyzed_stats,
        'citing_stats': citing_stats,
        'enhanced_stats': enhanced_stats,
        'if_days': if_days,
        'overlap_details': overlap_details,
        'journal_name': journal_name,
        'issn': issn,
        'period': period_str,
        'n_analyzed': n_analyzed,
        'n_citing': n_citing
    }
    
    state.analysis_complete = True
    
    time.sleep(1)
    overall_progress.empty()
    overall_status.empty()

# === 21. Главный интерфейс ===
def main():
    initialize_analysis_state()
    state = get_analysis_state()
    
    # Заголовок
    st.title("🔬 Комплексный анализатор научных журналов")
    st.markdown("---")
    
    # Боковая панель с вводом данных
    with st.sidebar:
        st.header("📝 Параметры анализа")
        
        issn = st.text_input(
            "ISSN журнала:",
            value="2411-1414",
            help="Введите ISSN журнала для анализа"
        )
        
        period = st.text_input(
            "Период анализа:",
            value="2022-2024",
            help="Примеры: 2022, 2022-2024, 2022,2024"
        )
        
        st.markdown("---")
        st.header("💡 Информация")
        
        st.info("""
        **Возможности анализа:**
        - 📊 Impact Factor и CiteScore
        - 👥 Анализ авторов и аффилиаций
        - 🌍 Географическое распределение
        - 🔗 Пересечения между работами
        - ⏱️ Время до цитирования
        - 📈 Визуализация данных
        - 🎯 Прогнозирование метрик
        """)
        
        st.warning("""
        **Примечание:** 
        - Анализ может занять несколько минут
        - Убедитесь в корректности ISSN
        - Для больших периодов время анализа увеличивается
        """)
    
    # Основная область
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🚀 Запуск анализа")
        
        if st.button("Начать анализ", type="primary", use_container_width=True):
            if not issn:
                st.error("❌ Введите ISSN журнала")
                return
                
            if not period:
                st.error("❌ Введите период анализа")
                return
                
            with st.spinner("Запуск анализа..."):
                analyze_journal(issn, period)
    
    with col2:
        st.subheader("📤 Результаты")
        
        if state.analysis_complete and state.excel_buffer is not None:
            results = state.analysis_results
            
            st.download_button(
                label="📥 Скачать Excel отчет",
                data=state.excel_buffer,
                file_name=f"journal_analysis_{results['issn']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    # Отображение результатов
    if state.analysis_complete:
        st.markdown("---")
        st.header("📊 Результаты анализа")
        
        results = state.analysis_results
        
        # Сводная информация
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Журнал", results['journal_name'])
        with col2:
            st.metric("ISSN", results['issn'])
        with col3:
            st.metric("Период", results['period'])
        with col4:
            st.metric("Статей проанализировано", results['n_analyzed'])
        
        # Визуализации
        create_visualizations(
            results['analyzed_stats'],
            results['citing_stats'], 
            results['enhanced_stats'],
            results['if_days'],
            results['overlap_details']
        )
        
        # Детальная статистика
        st.markdown("---")
        st.header("📈 Детальная статистика")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Анализируемые статьи", "Цитирующие работы", "Сравнительный анализ", "Метрики журнала"])
        
        with tab1:
            st.subheader("Статистика анализируемых статей")
            stats = results['analyzed_stats']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Всего статей", stats['n_items'])
                st.metric("Статьи с одним автором", stats['single_authors'])
                st.metric("Международные статьи", f"{stats['multi_country_pct']:.1f}%")
                st.metric("Уникальных аффилиаций", stats['unique_affiliations_count'])
                
            with col2:
                st.metric("Общее количество ссылок", stats['total_refs'])
                st.metric("Самоцитирования", f"{stats['self_cites_pct']:.1f}%")
                st.metric("Уникальных стран", stats['unique_countries_count'])
                st.metric("Статьи с ≥10 цитированиями", stats['articles_with_10_citations'])
        
        with tab2:
            st.subheader("Статистика цитирующих работ")
            stats = results['citing_stats']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Всего цитирующих статей", stats['n_items'])
                st.metric("Уникальных журналов", stats['unique_journals_count'])
                st.metric("Уникальных издателей", stats['unique_publishers_count'])
                
            with col2:
                st.metric("Общее количество ссылок", stats['total_refs'])
                st.metric("Уникальных аффилиаций", stats['unique_affiliations_count'])
                st.metric("Уникальных стран", stats['unique_countries_count'])
        
        with tab3:
            st.subheader("Сравнительный анализ")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "Среднее авторов на статью (анализируемые)", 
                    f"{results['analyzed_stats']['auth_mean']:.1f}"
                )
                st.metric(
                    "Среднее ссылок на статью (анализируемые)", 
                    f"{results['analyzed_stats']['ref_mean']:.1f}"
                )
                
            with col2:
                st.metric(
                    "Среднее авторов на статью (цитирующие)", 
                    f"{results['citing_stats']['auth_mean']:.1f}"
                )
                st.metric(
                    "Среднее ссылок на статью (цитирующие)", 
                    f"{results['citing_stats']['ref_mean']:.1f}"
                )
        
        with tab4:
            st.subheader("Метрики журнала")
            if_days = results['if_days']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Impact Factor", f"{if_days.get('if_value', 0):.4f}")
                st.metric("Числитель IF", if_days.get('c_num', 0))
                st.metric("Знаменатель IF", if_days.get('p_den', 0))
                st.metric("Годы публикаций IF", f"{if_days.get('publication_years', [0, 0])[0]}-{if_days.get('publication_years', [0, 0])[1]}")
                
            with col2:
                st.metric("CiteScore", f"{if_days.get('citescore_value', 0):.4f}")
                st.metric("Числитель CiteScore", if_days.get('cs_c_num', 0))
                st.metric("Знаменатель CiteScore", if_days.get('cs_p_den', 0))
                st.metric("Годы публикаций CiteScore", f"{if_days.get('cs_publication_years', [0, 0])[0]}-{if_days.get('cs_publication_years', [0, 0])[-1]}")

# Запуск приложения
if __name__ == "__main__":
    main()


