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

# === 16. Расчет времени цитирования ===
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

# === НОВЫЕ ФУНКЦИИ: БЫСТРЫЕ МЕТРИКИ БЕЗ API ЗАПРОСОВ ===

def calculate_reference_age_fast(analyzed_metadata, state):
    """Расчет возраста ссылок без дополнительных запросов к API"""
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
            # 1. Пробуем year из unstructured
            if 'year' in ref:
                try:
                    ref_year = int(ref['year'])
                    if 1900 <= ref_year <= current_year + 1:
                        ref_ages.append(current_year - ref_year)
                        continue
                except: 
                    pass
            
            # 2. Пробуем DOI из кэша (уже загружено!)
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
    """Journal Self-Citation Rate - процент самоцитирований"""
    total = len(citing_metadata)
    if total == 0: 
        return {
            'JSCR': 0,
            'self_cites': 0,
            'total_cites': 0
        }
    
    self_cites = 0
    for c in citing_metadata:
        oa = c.get('openalex')
        if not oa: 
            continue
        issns = oa.get('host_venue', {}).get('issn', [])
        if journal_issn in issns:
            self_cites += 1
    
    return {
        'JSCR': round(self_cites / total * 100, 2),
        'self_cites': self_cites,
        'total_cites': total
    }

def calculate_cited_half_life_fast(analyzed_metadata, state):
    """Cited Half-Life - медианное время до получения половины цитирований"""
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
            y = c.get('openalex', {}).get('publication_year')
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
    """Field-Weighted Citation Impact - взвешенный по тематике индекс цитирования"""
    total_cites = 0
    expected = 0.0
    
    for meta in analyzed_metadata:
        oa = meta.get('openalex')
        if not oa: 
            continue
            
        cites = oa.get('cited_by_count', 0)
        total_cites += cites
        
        concepts = oa.get('concepts', [])
        if not concepts: 
            continue
            
        main = max(concepts, key=lambda x: x.get('score', 0))
        works = max(main.get('works_count', 1), 1)
        field_cites = main.get('cited_by_count', 0)
        expected += (field_cites / works)
    
    fwci = total_cites / expected if expected > 0 else 0
    return {
        'FWCI': round(fwci, 2),
        'total_cites': total_cites,
        'expected_cites': round(expected, 2)
    }

def calculate_citation_velocity_fast(analyzed_metadata, state):
    """Citation Velocity - среднее цитирований в год за первые 2 года"""
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
        early = sum(1 for c in citings 
                   if c.get('openalex', {}).get('publication_year', 0) <= pub_year + 2)
        velocities.append(early / 2.0)
    
    return {
        'citation_velocity': round(np.mean(velocities), 2) if velocities else 0,
        'articles_with_velocity': len(velocities)
    }

def calculate_oa_impact_premium_fast(analyzed_metadata):
    """Open Access Impact Premium - разница в цитированиях между OA и не-OA"""
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
    """Elite Index - процент статей в топ-10% по цитированиям"""
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
    
    threshold = np.percentile(citations, 90)
    elite_count = sum(1 for c in citations if c >= threshold)
    
    return {
        'elite_index': round(elite_count / len(citations) * 100, 2),
        'elite_articles': elite_count,
        'total_articles': len(citations),
        'citation_threshold': int(threshold)
    }

def calculate_author_gini_fast(analyzed_metadata):
    """Author Gini Index - индекс неравенства распределения публикаций по авторам"""
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
    
    # Расчет индекса Джини
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
    """Diversity Balance Index - индекс диверсификации тематик"""
    concept_freq = Counter()
    total_concepts = 0
    
    for meta in analyzed_metadata:
        oa = meta.get('openalex')
        if oa and 'concepts' in oa:
            concepts = oa['concepts']
            for concept in concepts[:3]:  # Берем топ-3 концепта
                concept_name = concept.get('display_name', '')
                if concept_name:
                    concept_freq[concept_name] += 1
                    total_concepts += 1
    
    if total_concepts == 0:
        return {'DBI': 0}
    
    # Индекс Шеннона
    proportions = [count / total_concepts for count in concept_freq.values()]
    shannon = -sum(p * np.log(p) for p in proportions if p > 0)
    
    # Нормализация (максимум = log(n))
    max_shannon = np.log(len(concept_freq)) if concept_freq else 1
    dbi = shannon / max_shannon if max_shannon > 0 else 0
    
    return {
        'DBI': round(dbi, 3),
        'unique_concepts': len(concept_freq),
        'total_concept_mentions': total_concepts,
        'top_concepts': concept_freq.most_common(5)
    }

def calculate_all_fast_metrics(analyzed_metadata, citing_metadata, state, journal_issn):
    """Расчет всех быстрых метрик за один проход"""
    fast_metrics = {}
    
    # Reference Age
    fast_metrics.update(calculate_reference_age_fast(analyzed_metadata, state))
    
    # JSCR
    fast_metrics.update(calculate_jscr_fast(citing_metadata, journal_issn))
    
    # Cited Half-Life
    fast_metrics.update(calculate_cited_half_life_fast(analyzed_metadata, state))
    
    # FWCI
    fast_metrics.update(calculate_fwci_fast(analyzed_metadata))
    
    # Citation Velocity
    fast_metrics.update(calculate_citation_velocity_fast(analyzed_metadata, state))
    
    # OA Impact Premium
    fast_metrics.update(calculate_oa_impact_premium_fast(analyzed_metadata))
    
    # Elite Index
    fast_metrics.update(calculate_elite_index_fast(analyzed_metadata))
    
    # Author Gini
    fast_metrics.update(calculate_author_gini_fast(analyzed_metadata))
    
    # DBI
    fast_metrics.update(calculate_dbi_fast(analyzed_metadata))
    
    return fast_metrics

# === 17. Создание расширенного Excel отчета ===
def create_enhanced_excel_report(analyzed_data, citing_data, analyzed_stats, citing_stats, enhanced_stats, citation_timing, overlap_details, fast_metrics, excel_buffer):
    """Создание расширенного Excel отчета с обработкой ошибок для больших данных"""
    try:
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            # Лист 1: Анализируемые статьи (с оптимизацией)
            analyzed_list = []
            MAX_ROWS = 50000  # Ограничиваем для больших данных
            
            for i, item in enumerate(analyzed_data):
                if i >= MAX_ROWS:
                    break
                if item and item.get('crossref'):
                    cr = item['crossref']
                    oa = item.get('openalex', {})
                    authors_list, affiliations_list, countries_list = extract_affiliations_and_countries(oa)
                    journal_info = extract_journal_info(item)
                    
                    analyzed_list.append({
                        'DOI': cr.get('DOI', '')[:100],
                        'Название': (cr.get('title', [''])[0] if cr.get('title') else 'Без названия')[:200],
                        'Авторы_Crossref': '; '.join([f"{a.get('given', '')} {a.get('family', '')}" for a in cr.get('author', [])])[:300],
                        'Авторы_OpenAlex': '; '.join(authors_list)[:300],
                        'Аффилиации': '; '.join(affiliations_list)[:500],
                        'Страны': '; '.join(countries_list)[:100],
                        'Год публикации': cr.get('published', {}).get('date-parts', [[0]])[0][0],
                        'Журнал': journal_info['journal_name'][:100],
                        'Издатель': journal_info['publisher'][:100],
                        'ISSN': '; '.join(journal_info['issn'])[:50],
                        'Количество ссылок': cr.get('reference-count', 0),
                        'Цитирования Crossref': cr.get('is-referenced-by-count', 0),
                        'Цитирования OpenAlex': oa.get('cited_by_count', 0) if oa else 0,
                        'Количество авторов': len(cr.get('author', [])),
                        'Тип работы': cr.get('type', '')[:50]
                    })
            
            if analyzed_list:
                analyzed_df = pd.DataFrame(analyzed_list)
                analyzed_df.to_excel(writer, sheet_name='Анализируемые_статьи', index=False)

            # Лист 2: Цитирующие работы (с оптимизацией)
            citing_list = []
            for i, item in enumerate(citing_data):
                if i >= MAX_ROWS:
                    break
                if item and item.get('crossref'):
                    cr = item['crossref']
                    oa = item.get('openalex', {})
                    authors_list, affiliations_list, countries_list = extract_affiliations_and_countries(oa)
                    journal_info = extract_journal_info(item)
                    
                    citing_list.append({
                        'DOI': cr.get('DOI', '')[:100],
                        'Название': (cr.get('title', [''])[0] if cr.get('title') else 'Без названия')[:200],
                        'Авторы_Crossref': '; '.join([f"{a.get('given', '')} {a.get('family', '')}" for a in cr.get('author', [])])[:300],
                        'Авторы_OpenAlex': '; '.join(authors_list)[:300],
                        'Аффилиации': '; '.join(affiliations_list)[:500],
                        'Страны': '; '.join(countries_list)[:100],
                        'Год публикации': cr.get('published', {}).get('date-parts', [[0]])[0][0],
                        'Журнал': journal_info['journal_name'][:100],
                        'Издатель': journal_info['publisher'][:100],
                        'ISSN': '; '.join(journal_info['issn'])[:50],
                        'Количество ссылок': cr.get('reference-count', 0),
                        'Цитирования Crossref': cr.get('is-referenced-by-count', 0),
                        'Цитирования OpenAlex': oa.get('cited_by_count', 0) if oa else 0,
                        'Количество авторов': len(cr.get('author', [])),
                        'Тип работы': cr.get('type', '')[:50]
                    })
            
            if citing_list:
                citing_df = pd.DataFrame(citing_list)
                citing_df.to_excel(writer, sheet_name='Цитирующие_работы', index=False)

            # Лист 3: Пересечения анализируемых и цитирующих работ
            overlap_list = []
            for overlap in overlap_details:
                overlap_list.append({
                    'DOI анализируемой работы': overlap['analyzed_doi'][:100],
                    'DOI цитирующей работы': overlap['citing_doi'][:100],
                    'Совпадающие авторы': '; '.join(overlap['common_authors'])[:300],
                    'Количество совпадающих авторов': overlap['common_authors_count'],
                    'Совпадающие аффилиации': '; '.join(overlap['common_affiliations'])[:500],
                    'Количество совпадающих аффилиаций': overlap['common_affiliations_count']
                })
            
            if overlap_list:
                overlap_df = pd.DataFrame(overlap_list)
                overlap_df.to_excel(writer, sheet_name='Пересечения_работ', index=False)

            # Лист 4: Время до первого цитирования
            first_citation_list = []
            for detail in citation_timing.get('first_citation_details', []):
                first_citation_list.append({
                    'DOI анализируемой работы': detail['analyzed_doi'][:100],
                    'DOI первой цитирующей работы': detail['citing_doi'][:100],
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
                    'Статьи с ≥20 цитированиями',
                    'Статьи с ≥30 цитированиями',
                    'Статьи с ≥50 цитированиями'
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
                    analyzed_stats['articles_with_20_citations'],
                    analyzed_stats['articles_with_30_citations'],
                    analyzed_stats['articles_with_50_citations']
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

            # Лист 8: Время цитирования
            citation_timing_data = {
                'Метрика': [
                    'Минимальные дни до первого цитирования',
                    'Максимальные дни до первого цитирования', 
                    'Средние дни до первого цитирования',
                    'Медиана дней до первого цитирования', 
                    'Статьи с данными о времени цитирования',
                    'Всего лет покрыто данными о цитированиях'
                ],
                'Значение': [
                    citation_timing['days_min'],
                    citation_timing['days_max'],
                    f"{citation_timing['days_mean']:.1f}",
                    citation_timing['days_median'],
                    citation_timing['articles_with_timing_data'],
                    citation_timing['total_years_covered']
                ]
            }
            citation_timing_df = pd.DataFrame(citation_timing_data)
            citation_timing_df.to_excel(writer, sheet_name='Время_цитирования', index=False)

            # Лист 9: Цитирования по годам
            yearly_citations_data = []
            for yearly_stat in citation_timing['yearly_citations']:
                yearly_citations_data.append({
                    'Год': yearly_stat['year'],
                    'Количество цитирований': yearly_stat['citations_count']
                })
            
            if yearly_citations_data:
                yearly_citations_df = pd.DataFrame(yearly_citations_data)
                yearly_citations_df.to_excel(writer, sheet_name='Цитирования_по_годам', index=False)

            # Лист 10: Кривые накопления цитирований
            accumulation_data = []
            for pub_year, curve_data in citation_timing['accumulation_curves'].items():
                for data_point in curve_data:
                    accumulation_data.append({
                        'Год публикации': pub_year,
                        'Лет после публикации': data_point['years_since_publication'],
                        'Накопительные цитирования': data_point['cumulative_citations']
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
            if analyzed_stats['all_authors']:
                all_authors_data = {
                    'Автор': [author[0] for author in analyzed_stats['all_authors']],
                    'Количество статей': [author[1] for author in analyzed_stats['all_authors']]
                }
                all_authors_df = pd.DataFrame(all_authors_data)
                all_authors_df.to_excel(writer, sheet_name='Все_авторы_анализируемые', index=False)

            # Лист 13: Все авторы цитирующих
            if citing_stats['all_authors']:
                all_citing_authors_data = {
                    'Автор': [author[0] for author in citing_stats['all_authors']],
                    'Количество статей': [author[1] for author in citing_stats['all_authors']]
                }
                all_citing_authors_df = pd.DataFrame(all_citing_authors_data)
                all_citing_authors_df.to_excel(writer, sheet_name='Все_авторы_цитирующие', index=False)

            # Лист 14: Все аффилиации анализируемых
            if analyzed_stats['all_affiliations']:
                all_affiliations_data = {
                    'Аффилиация': [aff[0] for aff in analyzed_stats['all_affiliations']],
                    'Количество упоминаний': [aff[1] for aff in analyzed_stats['all_affiliations']]
                }
                all_affiliations_df = pd.DataFrame(all_affiliations_data)
                all_affiliations_df.to_excel(writer, sheet_name='Все_аффилиации_анализируемые', index=False)

            # Лист 15: Все аффилиации цитирующих
            if citing_stats['all_affiliations']:
                all_citing_affiliations_data = {
                    'Аффилиация': [aff[0] for aff in citing_stats['all_affiliations']],
                    'Количество упоминаний': [aff[1] for aff in citing_stats['all_affiliations']]
                }
                all_citing_affiliations_df = pd.DataFrame(all_citing_affiliations_data)
                all_citing_affiliations_df.to_excel(writer, sheet_name='Все_аффилиации_цитирующие', index=False)

            # Лист 16: Все страны анализируемых
            if analyzed_stats['all_countries']:
                all_countries_data = {
                    'Страна': [country[0] for country in analyzed_stats['all_countries']],
                    'Количество упоминаний': [country[1] for country in analyzed_stats['all_countries']]
                }
                all_countries_df = pd.DataFrame(all_countries_data)
                all_countries_df.to_excel(writer, sheet_name='Все_страны_анализируемые', index=False)

            # Лист 17: Все страны цитирующих
            if citing_stats['all_countries']:
                all_citing_countries_data = {
                    'Страна': [country[0] for country in citing_stats['all_countries']],
                    'Количество упоминаний': [country[1] for country in citing_stats['all_countries']]
                }
                all_citing_countries_df = pd.DataFrame(all_citing_countries_data)
                all_citing_countries_df.to_excel(writer, sheet_name='Все_страны_цитирующие', index=False)

            # Лист 18: Все журналы цитирующих
            if citing_stats['all_journals']:
                all_citing_journals_data = {
                    'Журнал': [journal[0] for journal in citing_stats['all_journals']],
                    'Количество статей': [journal[1] for journal in citing_stats['all_journals']]
                }
                all_citing_journals_df = pd.DataFrame(all_citing_journals_data)
                all_citing_journals_df.to_excel(writer, sheet_name='Все_журналы_цитирующие', index=False)

            # Лист 19: Все издатели цитирующих
            if citing_stats['all_publishers']:
                all_citing_publishers_data = {
                    'Издатель': [publisher[0] for publisher in citing_stats['all_publishers']],
                    'Количество статей': [publisher[1] for publisher in citing_stats['all_publishers']]
                }
                all_citing_publishers_df = pd.DataFrame(all_citing_publishers_data)
                all_citing_publishers_df.to_excel(writer, sheet_name='Все_издатели_цитирующие', index=False)

            # Лист 20: Быстрые метрики (НОВЫЙ)
            fast_metrics_data = {
                'Метрика': [
                    'Reference Age (медиана)', 'Reference Age (среднее)',
                    'Reference Age (25-75 перцентиль)', 'Проанализировано ссылок',
                    'Journal Self-Citation Rate (JSCR)', 'Самоцитирования журнала',
                    'Всего цитирований для JSCR',
                    'Cited Half-Life (медиана)', 'Cited Half-Life (среднее)',
                    'Статьи с данными для CHL',
                    'Field-Weighted Citation Impact (FWCI)', 'Общие цитирования',
                    'Ожидаемые цитирования',
                    'Citation Velocity', 'Статьи с данными для velocity',
                    'OA Impact Premium', 'OA статей', 'Не-OA статей',
                    'Средние цитирования OA', 'Средние цитирования не-OA',
                    'Elite Index', 'Элитные статьи', 'Порог цитирований',
                    'Author Gini Index', 'Всего авторов',
                    'Среднее статей на автора', 'Медиана статей на автора',
                    'Diversity Balance Index (DBI)', 'Уникальных концептов',
                    'Всего упоминаний концептов'
                ],
                'Значение': [
                    fast_metrics.get('ref_median_age', 'N/A'),
                    fast_metrics.get('ref_mean_age', 'N/A'),
                    f"{fast_metrics.get('ref_ages_25_75', ['N/A', 'N/A'])[0]}-{fast_metrics.get('ref_ages_25_75', ['N/A', 'N/A'])[1]}",
                    fast_metrics.get('total_refs_analyzed', 0),
                    f"{fast_metrics.get('JSCR', 0)}%",
                    fast_metrics.get('self_cites', 0),
                    fast_metrics.get('total_cites', 0),
                    fast_metrics.get('cited_half_life_median', 'N/A'),
                    fast_metrics.get('cited_half_life_mean', 'N/A'),
                    fast_metrics.get('articles_with_chl', 0),
                    fast_metrics.get('FWCI', 0),
                    fast_metrics.get('total_cites', 0),
                    fast_metrics.get('expected_cites', 0),
                    fast_metrics.get('citation_velocity', 0),
                    fast_metrics.get('articles_with_velocity', 0),
                    f"{fast_metrics.get('OA_impact_premium', 0)}%",
                    fast_metrics.get('OA_articles', 0),
                    fast_metrics.get('non_OA_articles', 0),
                    fast_metrics.get('OA_avg_citations', 0),
                    fast_metrics.get('non_OA_avg_citations', 0),
                    f"{fast_metrics.get('elite_index', 0)}%",
                    fast_metrics.get('elite_articles', 0),
                    fast_metrics.get('citation_threshold', 0),
                    fast_metrics.get('author_gini', 0),
                    fast_metrics.get('total_authors', 0),
                    fast_metrics.get('articles_per_author_avg', 0),
                    fast_metrics.get('articles_per_author_median', 0),
                    fast_metrics.get('DBI', 0),
                    fast_metrics.get('unique_concepts', 0),
                    fast_metrics.get('total_concept_mentions', 0)
                ]
            }
            fast_metrics_df = pd.DataFrame(fast_metrics_data)
            fast_metrics_df.to_excel(writer, sheet_name='Быстрые_метрики', index=False)

            # Лист 21: Топ концепты (НОВЫЙ)
            if fast_metrics.get('top_concepts'):
                top_concepts_data = {
                    'Концепт': [concept[0] for concept in fast_metrics['top_concepts']],
                    'Количество упоминаний': [concept[1] for concept in fast_metrics['top_concepts']]
                }
                top_concepts_df = pd.DataFrame(top_concepts_data)
                top_concepts_df.to_excel(writer, sheet_name='Топ_концепты', index=False)

            # Гарантируем, что есть хотя бы один лист
            if len(writer.sheets) == 0:
                error_df = pd.DataFrame({'Сообщение': ['Нет данных для отчета']})
                error_df.to_excel(writer, sheet_name='Информация', index=False)

        excel_buffer.seek(0)
        return True

    except Exception as e:
        st.error(f"❌ Ошибка при создании Excel отчета: {str(e)}")
        # Создаем минимальный отчет с ошибкой
        try:
            excel_buffer.seek(0)
            excel_buffer.truncate(0)
            
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                error_df = pd.DataFrame({
                    'Ошибка': [f'Не удалось создать полный отчет: {str(e)}'],
                    'Рекомендация': ['Попробуйте уменьшить объем анализируемых данных или период анализа']
                })
                error_df.to_excel(writer, sheet_name='Информация', index=False)
            
            excel_buffer.seek(0)
            st.warning("⚠️ Создан упрощенный отчет из-за ограничений памяти")
            return True
            
        except Exception as e2:
            st.error(f"❌ Критическая ошибка при создании упрощенного отчета: {str(e2)}")
            return False

# === 18. Визуализация данных ===
def create_visualizations(analyzed_stats, citing_stats, enhanced_stats, citation_timing, overlap_details, fast_metrics):
    """Создание визуализаций для дашборда"""
    
    # Создаем вкладки для разных типов визуализаций
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📈 Основные метрики", 
        "👥 Авторы и организации", 
        "🌍 География", 
        "📊 Цитирования",
        "🔀 Пересечения",
        "⏱️ Время цитирования",
        "🚀 Быстрые метрики"  # НОВАЯ ВКЛАДКА
    ])
    
    with tab1:
        st.subheader("📈 Ключевые метрики журнала")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("H-index", enhanced_stats['h_index'])
        with col2:
            st.metric("Всего статей", analyzed_stats['n_items'])
        with col3:
            st.metric("Всего цитирований", enhanced_stats['total_citations'])
        with col4:
            st.metric("Среднее цитирований", f"{enhanced_stats['avg_citations_per_article']:.1f}")
        
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.metric("Статьи с цитированиями", enhanced_stats['articles_with_citations'])
        with col6:
            st.metric("Самоцитирования", f"{analyzed_stats['self_cites_pct']:.1f}%")
        with col7:
            st.metric("Международные статьи", f"{analyzed_stats['multi_country_pct']:.1f}%")
        with col8:
            st.metric("Уникальных аффилиаций", analyzed_stats['unique_affiliations_count'])
        
        # График цитирований по годам
        if citation_timing['yearly_citations']:
            years = [item['year'] for item in citation_timing['yearly_citations']]
            citations = [item['citations_count'] for item in citation_timing['yearly_citations']]
            
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
            if analyzed_stats['all_authors']:
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
                    analyzed_stats['single_authors'],
                    analyzed_stats['n_items'] - analyzed_stats['single_authors'] - analyzed_stats['multi_authors_gt10'],
                    analyzed_stats['multi_authors_gt10'],
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
        if analyzed_stats['all_affiliations']:
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
            if analyzed_stats['all_countries']:
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
                    analyzed_stats['single_country_articles'],
                    analyzed_stats['multi_country_articles'],
                    analyzed_stats['no_country_articles']
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
                'Порог': ['≥10', '≥20', '≥30', '≥50'],
                'Статьи': [
                    analyzed_stats['articles_with_10_citations'],
                    analyzed_stats['articles_with_20_citations'],
                    analyzed_stats['articles_with_30_citations'],
                    analyzed_stats['articles_with_50_citations']
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
                    enhanced_stats['articles_with_citations'],
                    enhanced_stats['articles_without_citations']
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
            articles_with_overlaps = len(set([o['analyzed_doi'] for o in overlap_details]))
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Всего пересечений", total_overlaps)
            with col2:
                st.metric("Статей с пересечениями", articles_with_overlaps)
            with col3:
                avg_overlaps = total_overlaps / articles_with_overlaps if articles_with_overlaps > 0 else 0
                st.metric("Среднее пересечений на статью", f"{avg_overlaps:.1f}")
            
            # Распределение по количеству пересечений
            overlap_counts = [o['common_authors_count'] + o['common_affiliations_count'] for o in overlap_details]
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
            st.metric("Мин. дней до цитирования", citation_timing['days_min'])
        with col2:
            st.metric("Макс. дней до цитирования", citation_timing['days_max'])
        with col3:
            st.metric("Среднее дней", f"{citation_timing['days_mean']:.1f}")
        with col4:
            st.metric("Медиана дней", citation_timing['days_median'])
        
        # Детали первых цитирований
        if citation_timing['first_citation_details']:
            st.subheader("Детали первых цитирований")
            first_citation_df = pd.DataFrame(citation_timing['first_citation_details'])
            st.dataframe(first_citation_df)
            
            # Гистограмма времени до первого цитирования
            days_data = [d['days_to_first_citation'] for d in citation_timing['first_citation_details']]
            fig = px.histogram(
                x=days_data,
                title='Распределение времени до первого цитирования (дни)',
                labels={'x': 'Дни до первого цитирования', 'y': 'Количество статей'}
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab7:
        st.subheader("🚀 Быстрые метрики (рассчитано без API запросов)")
        
        # Основные быстрые метрики
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Reference Age", f"{fast_metrics.get('ref_median_age', 'N/A')} лет")
        with col2:
            st.metric("JSCR", f"{fast_metrics.get('JSCR', 0)}%")
        with col3:
            st.metric("Cited Half-Life", f"{fast_metrics.get('cited_half_life_median', 'N/A')} лет")
        with col4:
            st.metric("FWCI", fast_metrics.get('FWCI', 0))
        
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.metric("Citation Velocity", fast_metrics.get('citation_velocity', 0))
        with col6:
            st.metric("OA Impact Premium", f"{fast_metrics.get('OA_impact_premium', 0)}%")
        with col7:
            st.metric("Elite Index", f"{fast_metrics.get('elite_index', 0)}%")
        with col8:
            st.metric("Author Gini", fast_metrics.get('author_gini', 0))
        
        # Детальная информация о быстрых метриках
        st.subheader("📊 Детали быстрых метрик")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Reference Age распределение
            if fast_metrics.get('ref_median_age') is not None:
                st.write("**Reference Age:**")
                st.write(f"- Медиана: {fast_metrics['ref_median_age']} лет")
                st.write(f"- Среднее: {fast_metrics['ref_mean_age']} лет")
                st.write(f"- 25-75 перцентиль: {fast_metrics['ref_ages_25_75'][0]}-{fast_metrics['ref_ages_25_75'][1]} лет")
                st.write(f"- Проанализировано ссылок: {fast_metrics['total_refs_analyzed']}")
        
        with col2:
            # JSCR детали
            st.write("**Journal Self-Citation Rate:**")
            st.write(f"- Самоцитирования: {fast_metrics.get('self_cites', 0)}")
            st.write(f"- Всего цитирований: {fast_metrics.get('total_cites', 0)}")
            st.write(f"- Процент: {fast_metrics.get('JSCR', 0)}%")
        
        col3, col4 = st.columns(2)
        
        with col3:
            # Citation Velocity
            st.write("**Citation Velocity:**")
            st.write(f"- Среднее цитирований/год: {fast_metrics.get('citation_velocity', 0)}")
            st.write(f"- Статьи с данными: {fast_metrics.get('articles_with_velocity', 0)}")
        
        with col4:
            # OA Impact Premium
            st.write("**OA Impact Premium:**")
            st.write(f"- Премия: {fast_metrics.get('OA_impact_premium', 0)}%")
            st.write(f"- OA статей: {fast_metrics.get('OA_articles', 0)}")
            st.write(f"- Не-OA статей: {fast_metrics.get('non_OA_articles', 0)}")
        
        # Топ концепты
        if fast_metrics.get('top_concepts'):
            st.subheader("🏷️ Топ-5 тематических концептов")
            concepts_df = pd.DataFrame(fast_metrics['top_concepts'], columns=['Концепт', 'Упоминаний'])
            fig = px.bar(
                concepts_df,
                x='Упоминаний',
                y='Концепт',
                orientation='h',
                title='Топ тематических концептов',
                color='Упоминаний'
            )
            st.plotly_chart(fig, use_container_width=True)

# === 19. Основная функция анализа ===
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
    
    citation_timing = calculate_citation_timing(analyzed_metadata, state)
    
    # Расчет быстрых метрик (НОВОЕ)
    overall_status.text("🚀 Расчет быстрых метрик...")
    fast_metrics = calculate_all_fast_metrics(analyzed_metadata, all_citing_metadata, state, issn)
    
    overall_progress.progress(0.9)
    
    # Создание отчета
    overall_status.text("💾 Создание отчета...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'journal_analysis_{issn}_{timestamp}.xlsx'
    
    # Создаем Excel файл в памяти
    excel_buffer = io.BytesIO()
    create_enhanced_excel_report(analyzed_metadata, all_citing_metadata, analyzed_stats, citing_stats, enhanced_stats, citation_timing, overlap_details, fast_metrics, excel_buffer)
    
    excel_buffer.seek(0)
    state.excel_buffer = excel_buffer
    
    overall_progress.progress(1.0)
    overall_status.text("✅ Анализ завершен!")
    
    # Сохраняем результаты
    state.analysis_results = {
        'analyzed_stats': analyzed_stats,
        'citing_stats': citing_stats,
        'enhanced_stats': enhanced_stats,
        'citation_timing': citation_timing,
        'overlap_details': overlap_details,
        'fast_metrics': fast_metrics,  # НОВОЕ
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

# === 20. Главный интерфейс ===
def main():
    initialize_analysis_state()
    state = get_analysis_state()
    
    # Заголовок
    st.title("🔬 Advanced Journal Analysis Tool")
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
        - 📊 H-index и метрики цитирования
        - 👥 Анализ авторов и аффилиаций
        - 🌍 Географическое распределение
        - 🔗 Пересечения между работами
        - ⏱️ Время до цитирования
        - 📈 Визуализация данных
        - 🚀 **НОВОЕ: Быстрые метрики без API**
        """)
        
        st.warning("""
        **Примечание:** 
        - Анализ может занять несколько минут
        - Убедитесь в корректности ISSN
        - Для больших периодов время анализа увеличивается
        - Данная программа не расчитывает IF и CiteScore. Для получения данных об этих метриках используйте https://journal-metrics-app.streamlit.app
        - ©Chimica Techno Acta, https://chimicatechnoacta.ru / ©developed by daM
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
            results['citation_timing'],
            results['overlap_details'],
            results['fast_metrics']  # НОВОЕ
        )
        
        # Детальная статистика
        st.markdown("---")
        st.header("📈 Детальная статистика")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Анализируемые статьи", "Цитирующие работы", "Сравнительный анализ", "Быстрые метрики"])  # НОВАЯ ВКЛАДКА
        
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
        
        with tab4:  # НОВАЯ ВКЛАДКА
            st.subheader("🚀 Быстрые метрики (без API запросов)")
            fast_metrics = results['fast_metrics']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Reference Age", f"{fast_metrics.get('ref_median_age', 'N/A')} лет")
                st.metric("JSCR", f"{fast_metrics.get('JSCR', 0)}%")
                st.metric("Cited Half-Life", f"{fast_metrics.get('cited_half_life_median', 'N/A')} лет")
                st.metric("FWCI", fast_metrics.get('FWCI', 0))
                
            with col2:
                st.metric("Citation Velocity", fast_metrics.get('citation_velocity', 0))
                st.metric("OA Impact Premium", f"{fast_metrics.get('OA_impact_premium', 0)}%")
                st.metric("Elite Index", f"{fast_metrics.get('elite_index', 0)}%")
                st.metric("Author Gini", fast_metrics.get('author_gini', 0))
            
            # Детальная информация
            st.subheader("Детали быстрых метрик")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Reference Age:**")
                st.write(f"- Медиана: {fast_metrics.get('ref_median_age', 'N/A')} лет")
                st.write(f"- Среднее: {fast_metrics.get('ref_mean_age', 'N/A')} лет")
                st.write(f"- 25-75 перцентиль: {fast_metrics.get('ref_ages_25_75', ['N/A', 'N/A'])[0]}-{fast_metrics.get('ref_ages_25_75', ['N/A', 'N/A'])[1]} лет")
                st.write(f"- Проанализировано ссылок: {fast_metrics.get('total_refs_analyzed', 0)}")
                
                st.write("**Journal Self-Citation Rate:**")
                st.write(f"- Самоцитирования: {fast_metrics.get('self_cites', 0)}")
                st.write(f"- Всего цитирований: {fast_metrics.get('total_cites', 0)}")
                st.write(f"- Процент: {fast_metrics.get('JSCR', 0)}%")
            
            with col2:
                st.write("**Field-Weighted Citation Impact:**")
                st.write(f"- FWCI: {fast_metrics.get('FWCI', 0)}")
                st.write(f"- Общие цитирования: {fast_metrics.get('total_cites', 0)}")
                st.write(f"- Ожидаемые цитирования: {fast_metrics.get('expected_cites', 0)}")
                
                st.write("**Diversity Balance Index:**")
                st.write(f"- DBI: {fast_metrics.get('DBI', 0)}")
                st.write(f"- Уникальных концептов: {fast_metrics.get('unique_concepts', 0)}")
                st.write(f"- Всего упоминаний: {fast_metrics.get('total_concept_mentions', 0)}")

# Запуск приложения
if __name__ == "__main__":
    main()
