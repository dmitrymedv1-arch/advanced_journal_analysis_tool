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


# Import translation manager
from languages import translation_manager

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
        self.if_data = None
        self.cs_data = None

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
def get_doi_prefix(doi):
    if not doi or doi == 'N/A':
        return ''
    return doi.split('/')[0] if '/' in doi else doi[:7]

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
            for concept in concepts[:3]:  # Take top-3 concepts
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
        'top_concepts': concept_freq.most_common(5)
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
    
    # Load CS data (Scopus)
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
        if not issn:
            continue
            
        normalized_issn = normalize_issn_for_comparison(issn)
        
        # Search in Web of Science data
        if not state.if_data.empty:
            # Apply normalization with error handling
            def safe_normalize_issn(issn_series):
                try:
                    return issn_series.astype(str).apply(normalize_issn_for_comparison)
                except:
                    return pd.Series([""] * len(issn_series))
    
            if_match = state.if_data[
                (safe_normalize_issn(state.if_data['ISSN']) == normalized_issn) |
                (safe_normalize_issn(state.if_data['eISSN']) == normalized_issn)
            ]
            
            if not if_match.empty:
                if_metrics = {
                    'if': if_match.iloc[0]['IF'],
                    'quartile': if_match.iloc[0]['Quartile']
                }
                break  # Use first match
                  
        # Search in Scopus data - FIXED VERSION
        if not state.cs_data.empty:
            # Use exact column names from your file
            print_issn_col = 'Print ISSN'
            eissn_col = 'E-ISSN'
            citescore_col = 'CiteScore' 
            quartile_col = 'Quartile'
            
            # Check for required columns
            required_cols = [print_issn_col, eissn_col, citescore_col, quartile_col]
            missing_cols = [col for col in required_cols if col not in state.cs_data.columns]
            
            if missing_cols:
                print(f"❌ CS.xlsx missing columns: {missing_cols}")
                print(f"   Available columns: {state.cs_data.columns.tolist()}")
            else:
                # Function for safe ISSN normalization with debug
                def safe_normalize_issn_cs(issn_series):
                    try:
                        # Handle NaN values and convert to string
                        return issn_series.fillna('').astype(str).apply(normalize_issn_for_comparison)
                    except Exception as e:
                        print(f"Error normalizing CS ISSN: {e}")
                        return pd.Series([""] * len(issn_series))
                
                # Normalize ISSN columns
                normalized_print_issn = safe_normalize_issn_cs(state.cs_data[print_issn_col])
                normalized_eissn = safe_normalize_issn_cs(state.cs_data[eissn_col])
                
                # Debug: show sample of normalized ISSNs
                print(f"Sample normalized Print ISSN: {normalized_print_issn.head(3).tolist()}")
                print(f"Sample normalized E-ISSN: {normalized_eissn.head(3).tolist()}")
                
                # Search by Print ISSN and E-ISSN
                cs_match = state.cs_data[
                    (normalized_print_issn == normalized_issn) |
                    (normalized_eissn == normalized_issn)
                ]
                
                print(f"🔍 CS search result: {len(cs_match)} matches for {normalized_issn}")
                
                if not cs_match.empty:
                    # Remove duplicates and find best quartile
                    unique_matches = cs_match.drop_duplicates(subset=[citescore_col, quartile_col])
                    
                    if len(unique_matches) > 0:
                        # Convert quartiles to numeric format for correct comparison
                        def quartile_to_number(q):
                            if isinstance(q, (int, float)):
                                return int(q)
                            elif isinstance(q, str) and q.startswith('Q'):
                                return int(q[1:])
                            else:
                                try:
                                    return int(q)
                                except:
                                    return 5  # Worst case if not recognized
                        
                        # Find minimum (best) quartile
                        unique_matches['quartile_num'] = unique_matches[quartile_col].apply(quartile_to_number)
                        best_quartile_row = unique_matches.loc[unique_matches['quartile_num'].idxmin()]
                        
                        # Take CiteScore from row with best quartile
                        best_citescore = best_quartile_row[citescore_col]
                        best_quartile = best_quartile_row[quartile_col]
                        
                        # If quartile is in numeric format, convert to Q-format
                        if isinstance(best_quartile, (int, float)):
                            best_quartile = f"Q{int(best_quartile)}"
                        
                        cs_metrics = {
                            'citescore': best_citescore,
                            'quartile': best_quartile
                        }
                        break  # Use first successful match
    
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

# === 17. Enhanced Excel Report Creation ===
def create_enhanced_excel_report(analyzed_data, citing_data, analyzed_stats, citing_stats, enhanced_stats, citation_timing, overlap_details, fast_metrics, excel_buffer, additional_data):
    """Create enhanced Excel report with error handling for large data"""

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
            
    try:
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            # Sheet 1: Analyzed articles (with optimization)
            analyzed_list = []
            MAX_ROWS = 50000  # Limit for large data
            
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
                        'Title': (cr.get('title', [''])[0] if cr.get('title') else 'No title')[:200],
                        'Authors_Crossref': '; '.join([f"{a.get('given', '')} {a.get('family', '')}" for a in cr.get('author', [])])[:300],
                        'Authors_OpenAlex': '; '.join(authors_list)[:300],
                        'Affiliations': '; '.join(affiliations_list)[:500],
                        'Countries': '; '.join(countries_list)[:100],
                        'Publication_Year': cr.get('published', {}).get('date-parts', [[0]])[0][0],
                        'Journal': journal_info['journal_name'][:100],
                        'Publisher': journal_info['publisher'][:100],
                        'ISSN': '; '.join(journal_info['issn'])[:50],
                        'Reference_Count': cr.get('reference-count', 0),
                        'Citations_Crossref': cr.get('is-referenced-by-count', 0),
                        'Citations_OpenAlex': oa.get('cited_by_count', 0) if oa else 0,
                        'Author_Count': len(cr.get('author', [])),
                        'Work_Type': cr.get('type', '')[:50]
                    })
            
            if analyzed_list:
                analyzed_df = pd.DataFrame(analyzed_list)
                analyzed_df.to_excel(writer, sheet_name='Analyzed_Articles', index=False)

            # Sheet 2: Citing works (with optimization)
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
                        'Title': (cr.get('title', [''])[0] if cr.get('title') else 'No title')[:200],
                        'Authors_Crossref': '; '.join([f"{a.get('given', '')} {a.get('family', '')}" for a in cr.get('author', [])])[:300],
                        'Authors_OpenAlex': '; '.join(authors_list)[:300],
                        'Affiliations': '; '.join(affiliations_list)[:500],
                        'Countries': '; '.join(countries_list)[:100],
                        'Publication_Year': cr.get('published', {}).get('date-parts', [[0]])[0][0],
                        'Journal': journal_info['journal_name'][:100],
                        'Publisher': journal_info['publisher'][:100],
                        'ISSN': '; '.join(journal_info['issn'])[:50],
                        'Reference_Count': cr.get('reference-count', 0),
                        'Citations_Crossref': cr.get('is-referenced-by-count', 0),
                        'Citations_OpenAlex': oa.get('cited_by_count', 0) if oa else 0,
                        'Author_Count': len(cr.get('author', [])),
                        'Work_Type': cr.get('type', '')[:50]
                    })
            
            if citing_list:
                citing_df = pd.DataFrame(citing_list)
                citing_df.to_excel(writer, sheet_name='Citing_Works', index=False)

            # Sheet 3: Overlaps between analyzed and citing works
            overlap_list = []
            for overlap in overlap_details:
                overlap_list.append({
                    'Analyzed_DOI': overlap['analyzed_doi'][:100],
                    'Citing_DOI': overlap['citing_doi'][:100],
                    'Common_Authors': '; '.join(overlap['common_authors'])[:300],
                    'Common_Authors_Count': overlap['common_authors_count'],
                    'Common_Affiliations': '; '.join(overlap['common_affiliations'])[:500],
                    'Common_Affiliations_Count': overlap['common_affiliations_count']
                })
            
            if overlap_list:
                overlap_df = pd.DataFrame(overlap_list)
                overlap_df.to_excel(writer, sheet_name='Work_Overlaps', index=False)

            # Sheet 4: Time to first citation
            first_citation_list = []
            for detail in citation_timing.get('first_citation_details', []):
                first_citation_list.append({
                    'Analyzed_DOI': detail['analyzed_doi'][:100],
                    'First_Citing_DOI': detail['citing_doi'][:100],
                    'Publication_Date': detail['analyzed_date'].strftime('%Y-%m-%d'),
                    'First_Citation_Date': detail['first_citation_date'].strftime('%Y-%m-%d'),
                    'Days_to_First_Citation': detail['days_to_first_citation']
                })
            
            if first_citation_list:
                first_citation_df = pd.DataFrame(first_citation_list)
                first_citation_df.to_excel(writer, sheet_name='First_Citations', index=False)

            # Sheet 5: Analyzed articles statistics
            analyzed_stats_data = {
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
                'Value': [
                    analyzed_stats['n_items'],
                    analyzed_stats['total_refs'],
                    'References with DOI', analyzed_stats['refs_with_doi'], f"{analyzed_stats['refs_with_doi_pct']:.1f}%",
                    'References without DOI', analyzed_stats['refs_without_doi'], f"{analyzed_stats['refs_without_doi_pct']:.1f}%",
                    'Self-Citations', analyzed_stats['self_cites'], f"{analyzed_stats['self_cites_pct']:.1f}%",
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
            analyzed_stats_df.to_excel(writer, sheet_name='Analyzed_Statistics', index=False)

            # Sheet 6: Citing works statistics
            citing_stats_data = {
                'Metric': [
                    'Total Citing Articles', 
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
                    'Unique Publishers'
                ],
                'Value': [
                    citing_stats['n_items'],
                    citing_stats['total_refs'],
                    'References with DOI', citing_stats['refs_with_doi'], f"{citing_stats['refs_with_doi_pct']:.1f}%",
                    'References without DOI', citing_stats['refs_without_doi'], f"{citing_stats['refs_without_doi_pct']:.1f}%",
                    'Self-Citations', citing_stats['self_cites'], f"{citing_stats['self_cites_pct']:.1f}%",
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
            citing_stats_df.to_excel(writer, sheet_name='Citing_Statistics', index=False)

            # Sheet 7: Enhanced statistics
            enhanced_stats_data = {
                'Metric': [
                    'H-index', 'Total Citations',
                    'Average Citations per Article', 'Maximum Citations',
                    'Minimum Citations', 'Articles with Citations',
                    'Articles without Citations'
                ],
                'Value': [
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
            enhanced_stats_df.to_excel(writer, sheet_name='Enhanced_Statistics', index=False)

            # Sheet 8: Citation timing
            citation_timing_data = {
                'Metric': [
                    'Minimum Days to First Citation',
                    'Maximum Days to First Citation', 
                    'Average Days to First Citation',
                    'Median Days to First Citation', 
                    'Articles with Citation Timing Data',
                    'Total Years Covered by Citation Data'
                ],
                'Value': [
                    citation_timing['days_min'],
                    citation_timing['days_max'],
                    f"{citation_timing['days_mean']:.1f}",
                    citation_timing['days_median'],
                    citation_timing['articles_with_timing_data'],
                    citation_timing['total_years_covered']
                ]
            }
            citation_timing_df = pd.DataFrame(citation_timing_data)
            citation_timing_df.to_excel(writer, sheet_name='Citation_Timing', index=False)

            # Sheet 9: Citations by year
            yearly_citations_data = []
            for yearly_stat in citation_timing['yearly_citations']:
                yearly_citations_data.append({
                    'Year': yearly_stat['year'],
                    'Citations_Count': yearly_stat['citations_count']
                })
            
            if yearly_citations_data:
                yearly_citations_df = pd.DataFrame(yearly_citations_data)
                yearly_citations_df.to_excel(writer, sheet_name='Citations_by_Year', index=False)

            # Sheet 10: Citation accumulation curves
            accumulation_data = []
            for pub_year, curve_data in citation_timing['accumulation_curves'].items():
                for data_point in curve_data:
                    accumulation_data.append({
                        'Publication_Year': pub_year,
                        'Years_Since_Publication': data_point['years_since_publication'],
                        'Cumulative_Citations': data_point['cumulative_citations']
                    })
            
            if accumulation_data:
                accumulation_df = pd.DataFrame(accumulation_data)
                accumulation_df.to_excel(writer, sheet_name='Citation_Accumulation_Curves', index=False)

            # Sheet 11: Citation network
            citation_network_data = []
            for year, citing_years in enhanced_stats.get('citation_network', {}).items():
                year_counts = Counter(citing_years)
                for citing_year, count in year_counts.items():
                    citation_network_data.append({
                        'Publication_Year': year,
                        'Citation_Year': citing_year,
                        'Citations_Count': count
                    })
            
            if citation_network_data:
                citation_network_df = pd.DataFrame(citation_network_data)
                citation_network_df.to_excel(writer, sheet_name='Citation_Network', index=False)

            # Sheet 12: All authors analyzed (with percentages)
            if analyzed_stats['all_authors']:
                all_authors_data = []
                total_articles = analyzed_stats['n_items']
                for author, count in analyzed_stats['all_authors']:
                    percentage = (count / total_articles * 100) if total_articles > 0 else 0
                    all_authors_data.append({
                        'Author': author,
                        'Articles_Count': count,
                        'Percentage': round(percentage, 2)
                    })
                all_authors_df = pd.DataFrame(all_authors_data)
                all_authors_df.to_excel(writer, sheet_name='All_Authors_Analyzed', index=False)

            # Sheet 13: All authors citing (with percentages)
            if citing_stats['all_authors']:
                all_citing_authors_data = []
                total_citing_articles = citing_stats['n_items']
                for author, count in citing_stats['all_authors']:
                    percentage = (count / total_citing_articles * 100) if total_citing_articles > 0 else 0
                    all_citing_authors_data.append({
                        'Author': author,
                        'Articles_Count': count,
                        'Percentage': round(percentage, 2)
                    })
                all_citing_authors_df = pd.DataFrame(all_citing_authors_data)
                all_citing_authors_df.to_excel(writer, sheet_name='All_Authors_Citing', index=False)

            # Sheet 14: All affiliations analyzed (with percentages)
            if analyzed_stats['all_affiliations']:
                all_affiliations_data = []
                total_mentions = sum(count for _, count in analyzed_stats['all_affiliations'])
                for affiliation, count in analyzed_stats['all_affiliations']:
                    percentage = (count / total_mentions * 100) if total_mentions > 0 else 0
                    all_affiliations_data.append({
                        'Affiliation': affiliation,
                        'Mentions_Count': count,
                        'Percentage': round(percentage, 2)
                    })
                all_affiliations_df = pd.DataFrame(all_affiliations_data)
                all_affiliations_df.to_excel(writer, sheet_name='All_Affiliations_Analyzed', index=False)

            # Sheet 15: All affiliations citing (with percentages)
            if citing_stats['all_affiliations']:
                all_citing_affiliations_data = []
                total_mentions = sum(count for _, count in citing_stats['all_affiliations'])
                for affiliation, count in citing_stats['all_affiliations']:
                    percentage = (count / total_mentions * 100) if total_mentions > 0 else 0
                    all_citing_affiliations_data.append({
                        'Affiliation': affiliation,
                        'Mentions_Count': count,
                        'Percentage': round(percentage, 2)
                    })
                all_citing_affiliations_df = pd.DataFrame(all_citing_affiliations_data)
                all_citing_affiliations_df.to_excel(writer, sheet_name='All_Affiliations_Citing', index=False)

            # Sheet 16: All countries analyzed (with percentages)
            if analyzed_stats['all_countries']:
                all_countries_data = []
                total_mentions = sum(count for _, count in analyzed_stats['all_countries'])
                for country, count in analyzed_stats['all_countries']:
                    percentage = (count / total_mentions * 100) if total_mentions > 0 else 0
                    all_countries_data.append({
                        'Country': country,
                        'Mentions_Count': count,
                        'Percentage': round(percentage, 2)
                    })
                all_countries_df = pd.DataFrame(all_countries_data)
                all_countries_df.to_excel(writer, sheet_name='All_Countries_Analyzed', index=False)

            # Sheet 17: All countries citing (with percentages)
            if citing_stats['all_countries']:
                all_citing_countries_data = []
                total_mentions = sum(count for _, count in citing_stats['all_countries'])
                for country, count in citing_stats['all_countries']:
                    percentage = (count / total_mentions * 100) if total_mentions > 0 else 0
                    all_citing_countries_data.append({
                        'Country': country,
                        'Mentions_Count': count,
                        'Percentage': round(percentage, 2)
                    })
                all_citing_countries_df = pd.DataFrame(all_citing_countries_data)
                all_citing_countries_df.to_excel(writer, sheet_name='All_Countries_Citing', index=False)

            # Sheet 18: All journals citing (with percentages) - CORRECTED VERSION
            if citing_stats['all_journals']:
                all_citing_journals_data = []
                total_articles = citing_stats['n_items']
                
                # Load metrics data if not already loaded
                if get_analysis_state().if_data is None or get_analysis_state().cs_data is None:
                    load_metrics_data()
                
                for journal_info in citing_stats['all_journals']:
                    journal_name = journal_info[0]
                    count = journal_info[1]
                    percentage = (count / total_articles * 100) if total_articles > 0 else 0
                    
                    # Extract ISSNs for this journal from citing data
                    journal_issns = []
                    for citing_item in citing_data:
                        if citing_item and citing_item.get('crossref'):
                            cr = citing_item['crossref']
                            container_title = cr.get('container-title', [''])[0] if cr.get('container-title') else ''
                            if container_title == journal_name:
                                issns = cr.get('ISSN', [])
                                if isinstance(issns, str):
                                    issns = [issns]
                                journal_issns.extend(issns)
                    
                    # Remove duplicates
                    journal_issns = list(set(journal_issns))
                    
                    # Get ISSNs for display
                    issn_1 = journal_issns[0] if len(journal_issns) > 0 else ""
                    issn_2 = journal_issns[1] if len(journal_issns) > 1 else ""
                    
                    # Get metrics for this journal - CORRECTED CALL
                    metrics = get_journal_metrics(journal_issns)
                    
                    # Format values for display
                    cs_value = metrics['cs_metrics'].get('citescore', '') if metrics['cs_metrics'] else ''
                    q_value = metrics['cs_metrics'].get('quartile', '') if metrics['cs_metrics'] else ''
                    
                    # Convert numeric values to strings for nice display
                    if cs_value != '':
                        cs_value = f"{float(cs_value):.1f}" if isinstance(cs_value, (int, float)) else str(cs_value)
                    
                    all_citing_journals_data.append({
                        'Journal': journal_name,
                        'ISSN_1': issn_1,
                        'ISSN_2': issn_2,
                        'Articles_Count': count,
                        'Percentage': round(percentage, 2),
                        '': '',  # Empty column
                        'IF (WoS)': metrics['if_metrics'].get('if', '') if metrics['if_metrics'] else '',
                        'Q(WoS)': metrics['if_metrics'].get('quartile', '') if metrics['if_metrics'] else '',
                        ' ': '',  # Empty column
                        'CS (Scopus)': cs_value,
                        'Q(Scopus)': q_value
                    })
                
                all_citing_journals_df = pd.DataFrame(all_citing_journals_data)
                all_citing_journals_df.to_excel(writer, sheet_name='All_Journals_Citing', index=False)

            # Sheet 19: All publishers citing (with percentages)
            if citing_stats['all_publishers']:
                all_citing_publishers_data = []
                total_articles = citing_stats['n_items']
                for publisher, count in citing_stats['all_publishers']:
                    percentage = (count / total_articles * 100) if total_articles > 0 else 0
                    all_citing_publishers_data.append({
                        'Publisher': publisher,
                        'Articles_Count': count,
                        'Percentage': round(percentage, 2)
                    })
                all_citing_publishers_df = pd.DataFrame(all_citing_publishers_data)
                all_citing_publishers_df.to_excel(writer, sheet_name='All_Publishers_Citing', index=False)

            # Sheet 20: Fast metrics (NEW)
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
            fast_metrics_df.to_excel(writer, sheet_name='Fast_Metrics', index=False)

            # Sheet 21: Top concepts (NEW)
            if fast_metrics.get('top_concepts'):
                top_concepts_data = {
                    'Concept': [concept[0] for concept in fast_metrics['top_concepts']],
                    'Mentions_Count': [concept[1] for concept in fast_metrics['top_concepts']]
                }
                top_concepts_df = pd.DataFrame(top_concepts_data)
                top_concepts_df.to_excel(writer, sheet_name='Top_Concepts', index=False)

            # === REMOVED SHEETS: Reference_Year_Analysis, Reference_Age_Distribution, Reference_Age_Heatmap_Data, Reference_Publication ===

            # Sheet 22: Citation seasonality
            if 'citation_seasonality' in additional_data:
                seasonality_data = []
                citation_seasonality = additional_data['citation_seasonality']
                
                # Citation months
                for month in range(1, 13):
                    month_name = datetime(2023, month, 1).strftime('%B')
                    citation_count = citation_seasonality['citation_months'].get(month, 0)
                    publication_count = citation_seasonality['publication_months'].get(month, 0)
                    
                    seasonality_data.append({
                        'Month_Number': month,
                        'Month_Name': month_name,
                        'Citation_Count': citation_count,
                        'Publication_Count': publication_count
                    })
                
                if seasonality_data:
                    seasonality_df = pd.DataFrame(seasonality_data)
                    seasonality_df.to_excel(writer, sheet_name='Citation_Seasonality', index=False)

                # Optimal publication months
                if citation_seasonality['optimal_publication_months']:
                    optimal_months_data = []
                    for optimal in citation_seasonality['optimal_publication_months']:
                        optimal_months_data.append({
                            'High_Citation_Month': datetime(2023, optimal['citation_month'], 1).strftime('%B'),
                            'Citation_Count': optimal['citation_count'],
                            'Recommended_Publication_Month': datetime(2023, optimal['recommended_publication_month'], 1).strftime('%B'),
                            'Reasoning': optimal['reasoning']
                        })
                    
                    optimal_months_df = pd.DataFrame(optimal_months_data)
                    optimal_months_df.to_excel(writer, sheet_name='Optimal_Publication_Months', index=False)

            # Sheet 23: Potential reviewers
            if 'potential_reviewers' in additional_data:
                reviewers_data = []
                potential_reviewers_info = additional_data['potential_reviewers']
                
                for reviewer in potential_reviewers_info['potential_reviewers']:
                    # Create separate rows for each DOI
                    for i, doi in enumerate(reviewer['citing_dois']):
                        reviewers_data.append({
                            'Author': reviewer['author'] if i == 0 else '',  # Only show author name in first row
                            'Citation_Count': reviewer['citation_count'] if i == 0 else '',
                            'Citing_DOI': doi
                        })
                
                if reviewers_data:
                    reviewers_df = pd.DataFrame(reviewers_data)
                    reviewers_df.to_excel(writer, sheet_name='Potential_Reviewers', index=False)

                # Summary statistics
                summary_data = {
                    'Metric': [
                        'Total Journal Authors',
                        'Total Overlap Authors', 
                        'Total Potential Reviewers Found'
                    ],
                    'Value': [
                        potential_reviewers_info['total_journal_authors'],
                        potential_reviewers_info['total_overlap_authors'],
                        potential_reviewers_info['total_potential_reviewers']
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Reviewer_Discovery_Summary', index=False)

            # Ensure at least one sheet exists
            if len(writer.sheets) == 0:
                error_df = pd.DataFrame({'Message': [translation_manager.get_text('no_data_for_report')]})
                error_df.to_excel(writer, sheet_name='Information', index=False)

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

# === 18. Data Visualization ===
def create_visualizations(analyzed_stats, citing_stats, enhanced_stats, citation_timing, overlap_details, fast_metrics, additional_data):
    """Create visualizations for dashboard"""
    
    # Create tabs for different visualization types
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        translation_manager.get_text('tab_main_metrics'), 
        translation_manager.get_text('tab_authors_organizations'), 
        translation_manager.get_text('tab_geography'), 
        translation_manager.get_text('tab_citations'),
        translation_manager.get_text('tab_overlaps'),
        translation_manager.get_text('tab_citation_timing'),
        translation_manager.get_text('tab_fast_metrics'),
        translation_manager.get_text('tab_predictive_insights')
    ])
    
    with tab1:
        st.subheader(translation_manager.get_text('tab_main_metrics'))
        
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
    
    with tab5:
        st.subheader(translation_manager.get_text('tab_overlaps'))
        
        if overlap_details:
            # Overlap summary statistics
            total_overlaps = len(overlap_details)
            articles_with_overlaps = len(set([o['analyzed_doi'] for o in overlap_details]))
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(translation_manager.get_text('total_overlaps'), total_overlaps)
            with col2:
                st.metric(translation_manager.get_text('articles_with_overlaps'), articles_with_overlaps)
            with col3:
                avg_overlaps = total_overlaps / articles_with_overlaps if articles_with_overlaps > 0 else 0
                st.metric(translation_manager.get_text('average_overlaps_per_article'), f"{avg_overlaps:.1f}")
            
            # Overlap count distribution
            overlap_counts = [o['common_authors_count'] + o['common_affiliations_count'] for o in overlap_details]
            if overlap_counts:
                fig = px.histogram(
                    x=overlap_counts,
                    title=translation_manager.get_text('overlap_count_distribution'),
                    labels={'x': translation_manager.get_text('overlap_count'), 'y': translation_manager.get_text('frequency')}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Overlap details table
            st.subheader(translation_manager.get_text('overlap_details'))
            overlap_df = pd.DataFrame(overlap_details)
            st.dataframe(overlap_df[['analyzed_doi', 'citing_doi', 'common_authors_count', 'common_affiliations_count']])
        else:
            st.info(translation_manager.get_text('no_overlaps_found'))
    
    with tab6:
        st.subheader(translation_manager.get_text('tab_citation_timing'))
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(translation_manager.get_text('min_days_to_citation'), citation_timing['days_min'])
        with col2:
            st.metric(translation_manager.get_text('max_days_to_citation'), citation_timing['days_max'])
        with col3:
            st.metric(translation_manager.get_text('average_days'), f"{citation_timing['days_mean']:.1f}")
        with col4:
            st.metric(translation_manager.get_text('median_days'), citation_timing['days_median'])
        
        # Contextual tooltip for Cited Half-Life
        if fast_metrics.get('cited_half_life_median'):
            with st.expander("⏳ " + translation_manager.get_text('cited_half_life_explanation'), expanded=False):
                chl_info = glossary.get_detailed_info('Cited Half-Life')
                if chl_info:
                    st.write(f"**{translation_manager.get_text('current_value')}:** {fast_metrics['cited_half_life_median']} " + translation_manager.get_text('years'))
                    st.write(f"**{translation_manager.get_text('definition')}:** {chl_info['definition']}")
                    st.write(f"**{translation_manager.get_text('interpretation')}:** {chl_info['interpretation']}")
        
        # First citation details
        if citation_timing['first_citation_details']:
            st.subheader(translation_manager.get_text('first_citation_details'))
            first_citation_df = pd.DataFrame(citation_timing['first_citation_details'])
            st.dataframe(first_citation_df)
            
            # Time to first citation histogram
            days_data = [d['days_to_first_citation'] for d in citation_timing['first_citation_details']]
            fig = px.histogram(
                x=days_data,
                title=translation_manager.get_text('time_to_first_citation_distribution'),
                labels={'x': translation_manager.get_text('days_to_first_citation'), 'y': translation_manager.get_text('article_count')}
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab7:
        st.subheader(translation_manager.get_text('tab_fast_metrics'))
        
        # Main fast metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                translation_manager.get_text('reference_age'), 
                f"{fast_metrics.get('ref_median_age', 'N/A')} " + translation_manager.get_text('years'),
                help=glossary.get_tooltip('Reference Age')
            )
        with col2:
            st.metric(
                translation_manager.get_text('jscr'), 
                f"{fast_metrics.get('JSCR', 0)}%",
                help=glossary.get_tooltip('JSCR')
            )
        with col3:
            st.metric(
                translation_manager.get_text('cited_half_life'), 
                f"{fast_metrics.get('cited_half_life_median', 'N/A')} " + translation_manager.get_text('years'),
                help=glossary.get_tooltip('Cited Half-Life')
            )
        with col4:
            st.metric(
                translation_manager.get_text('fwci'), 
                fast_metrics.get('FWCI', 0),
                help=glossary.get_tooltip('FWCI')
            )
        
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.metric(
                translation_manager.get_text('citation_velocity'), 
                fast_metrics.get('citation_velocity', 0),
                help=glossary.get_tooltip('Citation Velocity')
            )
        with col6:
            st.metric(
                translation_manager.get_text('oa_impact_premium'), 
                f"{fast_metrics.get('OA_impact_premium', 0)}%",
                help=glossary.get_tooltip('OA Impact Premium')
            )
        with col7:
            st.metric(
                translation_manager.get_text('elite_index'), 
                f"{fast_metrics.get('elite_index', 0)}%",
                help=glossary.get_tooltip('Elite Index')
            )
        with col8:
            st.metric(
                translation_manager.get_text('author_gini'), 
                fast_metrics.get('author_gini', 0),
                help=glossary.get_tooltip('Author Gini')
            )
        
        # Detailed fast metrics information
        st.subheader(translation_manager.get_text('fast_metrics_details'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Reference Age distribution
            if fast_metrics.get('ref_median_age') is not None:
                st.write(translation_manager.get_text('reference_age_details'))
                st.write(translation_manager.get_text('reference_age_median').format(value=fast_metrics['ref_median_age']))
                st.write(translation_manager.get_text('reference_age_mean').format(value=fast_metrics['ref_mean_age']))
                st.write(translation_manager.get_text('reference_age_percentile').format(value=f"{fast_metrics['ref_ages_25_75'][0]}-{fast_metrics['ref_ages_25_75'][1]}"))
                st.write(translation_manager.get_text('reference_age_analyzed').format(value=fast_metrics['total_refs_analyzed']))
                
                # Contextual tooltip
                with st.expander("📚 " + translation_manager.get_text('more_about_reference_age'), expanded=False):
                    ra_info = glossary.get_detailed_info('Reference Age')
                    if ra_info:
                        st.write(f"**{translation_manager.get_text('what_does_it_mean')}** {ra_info['interpretation']}")
                        st.write(f"**{translation_manager.get_text('example')}:** {ra_info['example']}")
        
        with col2:
            # JSCR details
            st.write(translation_manager.get_text('jscr_details'))
            st.write(translation_manager.get_text('jscr_self_cites').format(value=fast_metrics.get('self_cites', 0)))
            st.write(translation_manager.get_text('jscr_total_cites').format(value=fast_metrics.get('total_cites', 0)))
            st.write(translation_manager.get_text('jscr_percentage').format(value=fast_metrics.get('JSCR', 0)))
        
        col3, col4 = st.columns(2)
        
        with col3:
            # Citation Velocity
            st.write(translation_manager.get_text('citation_velocity_details'))
            st.write(f"- {translation_manager.get_text('average_citations_per_year')}: {fast_metrics.get('citation_velocity', 0)}")
            st.write(f"- {translation_manager.get_text('articles_with_data')}: {fast_metrics.get('articles_with_velocity', 0)}")
        
        with col4:
            # OA Impact Premium
            st.write(translation_manager.get_text('oa_impact_premium_details'))
            st.write(f"- {translation_manager.get_text('premium')}: {fast_metrics.get('OA_impact_premium', 0)}%")
            st.write(f"- {translation_manager.get_text('oa_articles')}: {fast_metrics.get('OA_articles', 0)}")
            st.write(f"- {translation_manager.get_text('non_oa_articles')}: {fast_metrics.get('non_OA_articles', 0)}")
            
            # Contextual tooltip
            if fast_metrics.get('OA_impact_premium', 0) > 0:
                with st.expander("🔓 " + translation_manager.get_text('open_access_premium'), expanded=False):
                    st.success("📈 " + translation_manager.get_text('oa_premium_positive'))
        
        # Top concepts
        if fast_metrics.get('top_concepts'):
            st.subheader(translation_manager.get_text('top_5_thematic_concepts'))
            concepts_df = pd.DataFrame(fast_metrics['top_concepts'], columns=[translation_manager.get_text('concept'), translation_manager.get_text('mentions')])
            fig = px.bar(
                concepts_df,
                x=translation_manager.get_text('mentions'),
                y=translation_manager.get_text('concept'),
                orientation='h',
                title=translation_manager.get_text('top_thematic_concepts'),
                color=translation_manager.get_text('mentions')
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Contextual tooltip for DBI
            if fast_metrics.get('DBI', 0) > 0:
                with st.expander("🎯 " + translation_manager.get_text('diversity_balance_index'), expanded=False):
                    dbi_info = glossary.get_detailed_info('DBI')
                    if dbi_info:
                        st.write(f"**{translation_manager.get_text('current_dbi_value')}:** {fast_metrics['DBI']}")
                        st.write(f"**{translation_manager.get_text('interpretation')}:** {dbi_info['interpretation']}")
                        st.progress(fast_metrics['DBI'])

    with tab8:
        st.subheader("🔮 Predictive Insights & Recommendations")
        
        # Citation seasonality analysis
        if 'citation_seasonality' in additional_data:
            st.subheader("Citation Seasonality Analysis")
            
            seasonality = additional_data['citation_seasonality']
            
            # Citation by month chart
            months = list(range(1, 13))
            month_names = [datetime(2023, m, 1).strftime('%B') for m in months]
            citation_counts = [seasonality['citation_months'].get(m, 0) for m in months]
            
            fig = px.line(
                x=month_names,
                y=citation_counts,
                title="Citations by Month",
                labels={'x': 'Month', 'y': 'Number of Citations'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Optimal publication months
            if seasonality['optimal_publication_months']:
                st.subheader("Recommended Publication Months")
                
                for optimal in seasonality['optimal_publication_months']:
                    citation_month_name = datetime(2023, int(optimal['citation_month']), 1).strftime('%B')
                    publication_month_name = datetime(2023, int(optimal['recommended_publication_month']), 1).strftime('%B')
                    
                    st.info(
                        f"**Publish in {publication_month_name}** to target high-citation month {citation_month_name} "
                        f"({optimal['citation_count']} citations)"
                    )
        
        # Potential reviewers analysis
        if 'potential_reviewers' in additional_data:
            st.subheader("Potential Reviewer Discovery")
            
            reviewers_info = additional_data['potential_reviewers']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Journal Authors", reviewers_info['total_journal_authors'])
            with col2:
                st.metric("Authors with Overlaps", reviewers_info['total_overlap_authors'])
            with col3:
                st.metric("Potential Reviewers Found", reviewers_info['total_potential_reviewers'])
            
            # Top potential reviewers
            if reviewers_info['potential_reviewers']:
                st.subheader("Top Potential Reviewers")
                
                top_reviewers = reviewers_info['potential_reviewers'][:10]
                
                reviewers_df = pd.DataFrame([
                    {
                        'Author': reviewer['author'],
                        'Citation_Count': reviewer['citation_count'],
                        'Example_Citing_DOIs': ', '.join(reviewer['citing_dois'][:3]) + ('...' if len(reviewer['citing_dois']) > 3 else '')
                    }
                    for reviewer in top_reviewers
                ])
                st.dataframe(reviewers_df)
                
                st.info(
                    "💡 **These authors cite your journal but have never published in it. "
                    "They represent excellent potential reviewers as they are familiar with "
                    "your journal's content but maintain editorial independence.**"
                )

# === 19. Main Analysis Function ===
def analyze_journal(issn, period_str):
    global delayer
    delayer = AdaptiveDelayer()
    
    state = get_analysis_state()
    state.analysis_complete = False
    
    # Load metrics data at the start
    load_metrics_data()
    
    # Overall progress
    overall_progress = st.progress(0)
    overall_status = st.empty()
    
    # Period parsing
    overall_status.text(translation_manager.get_text('parsing_period'))
    years = parse_period(period_str)
    if not years:
        return
    from_date = f"{min(years)}-01-01"
    until_date = f"{max(years)}-12-31"
    overall_progress.progress(0.1)
    
    # Journal name
    overall_status.text(translation_manager.get_text('getting_journal_name'))
    journal_name = get_journal_name(issn)
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
    
    # Analyzed articles processing
    overall_status.text(translation_manager.get_text('processing_articles'))
    
    analyzed_metadata = []
    dois = [item.get('DOI') for item in validated_items if item.get('DOI')]
    
    # Progress bar for metadata processing
    meta_progress = st.progress(0)
    meta_status = st.empty()
    
    # Prepare arguments for threading
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
                st.error(f"Error processing DOI {doi}: {e}")
            
            progress = (i + 1) / len(dois)
            meta_progress.progress(progress)
            meta_status.text(f"{translation_manager.get_text('getting_metadata')}: {i + 1}/{len(dois)}")
    
    meta_progress.empty()
    meta_status.empty()
    overall_progress.progress(0.6)
    
    # Citing works retrieval
    overall_status.text(translation_manager.get_text('collecting_citations'))
    
    all_citing_metadata = []
    analyzed_dois = [am['doi'] for am in analyzed_metadata if am.get('doi')]
    
    # Progress bar for citation collection
    citing_progress = st.progress(0)
    citing_status = st.empty()
    
    # Prepare arguments for threading
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
    overall_progress.progress(0.8)
    
    # Statistics calculation
    overall_status.text(translation_manager.get_text('calculating_statistics'))
    
    analyzed_stats = extract_stats_from_metadata(analyzed_metadata, journal_prefix=journal_prefix)
    citing_stats = extract_stats_from_metadata(all_citing_metadata, is_analyzed=False)
    enhanced_stats = enhanced_stats_calculation(analyzed_metadata, all_citing_metadata, state)
    
    # Overlap analysis
    overlap_details = analyze_overlaps(analyzed_metadata, all_citing_metadata, state)
    
    citation_timing = calculate_citation_timing(analyzed_metadata, state)
    
    # Fast metrics calculation (NEW)
    overall_status.text(translation_manager.get_text('calculating_fast_metrics'))
    fast_metrics = calculate_all_fast_metrics(analyzed_metadata, all_citing_metadata, state, issn)
    
    # === NEW ADDITIONAL ANALYSES ===
    overall_status.text("Calculating additional insights...")
    
    # Citation seasonality analysis
    citation_seasonality = analyze_citation_seasonality(
        analyzed_metadata, 
        state, 
        citation_timing['days_median']
    )
    
    # Potential reviewer discovery
    potential_reviewers = find_potential_reviewers(
        analyzed_metadata, 
        all_citing_metadata, 
        overlap_details, 
        state
    )
    
    # Combine all additional data
    additional_data = {
        'citation_seasonality': citation_seasonality,
        'potential_reviewers': potential_reviewers
    }
    
    overall_progress.progress(0.9)
    
    # Report creation
    overall_status.text(translation_manager.get_text('creating_report'))
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'journal_analysis_{issn}_{timestamp}.xlsx'
    
    # Create Excel file in memory
    excel_buffer = io.BytesIO()
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
    
    overall_progress.progress(1.0)
    overall_status.text(translation_manager.get_text('analysis_complete'))
    
    # Save results
    state.analysis_results = {
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
    
    state.analysis_complete = True
    
    time.sleep(1)
    overall_progress.empty()
    overall_status.empty()

# === 20. Main Interface ===
def main():
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
        
        period = st.text_input(
            translation_manager.get_text('analysis_period'),
            value="2022-2024",
            help=translation_manager.get_text('period_examples')
        )
        
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
                "- **NEW:** Citation seasonality and optimal publication timing\n" +
                "- **NEW:** Potential reviewer discovery")
        
        st.warning("**" + translation_manager.get_text('note') + ":** \n" +
                  "- " + translation_manager.get_text('note_text_1') + "\n" +
                  "- " + translation_manager.get_text('note_text_2') + "\n" +
                  "- " + translation_manager.get_text('note_text_3') + "\n" +
                  "- " + translation_manager.get_text('note_text_4') + "\n" +
                  "- " + translation_manager.get_text('note_text_5'))
    
    # Main area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🚀 " + translation_manager.get_text('start_analysis'))
        
        if st.button(translation_manager.get_text('start_analysis'), type="primary", use_container_width=True):
            if not issn:
                st.error(translation_manager.get_text('issn_required'))
                return
                
            if not period:
                st.error(translation_manager.get_text('period_required'))
                return
                
            with st.spinner(translation_manager.get_text('analysis_starting')):
                analyze_journal(issn, period)
    
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
    
    # Results display
    if state.analysis_complete:
        st.markdown("---")
        st.header("📊 " + translation_manager.get_text('analysis_results'))
        
        results = state.analysis_results
        
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
            results.get('additional_data', {})
        )
        
        # Detailed statistics
        st.markdown("---")
        st.header("📈 " + translation_manager.get_text('detailed_statistics'))
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            translation_manager.get_text('analyzed_articles'), 
            translation_manager.get_text('citing_works'), 
            translation_manager.get_text('comparative_analysis'), 
            translation_manager.get_text('fast_metrics'),
            "🔮 Predictive Insights"
        ])
        
        with tab1:
            st.subheader(translation_manager.get_text('analyzed_articles_statistics'))
            stats = results['analyzed_stats']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(translation_manager.get_text('total_articles'), stats['n_items'])
                st.metric(translation_manager.get_text('single_author_articles'), stats['single_authors'])
                st.metric(translation_manager.get_text('international_collaboration'), f"{stats['multi_country_pct']:.1f}%")
                st.metric(translation_manager.get_text('unique_affiliations'), stats['unique_affiliations_count'])
                
            with col2:
                st.metric(translation_manager.get_text('total_references'), stats['total_refs'])
                st.metric(translation_manager.get_text('self_citations'), f"{stats['self_cites_pct']:.1f}%")
                st.metric(translation_manager.get_text('unique_countries'), stats['unique_countries_count'])
                st.metric(translation_manager.get_text('articles_10_citations'), stats['articles_with_10_citations'])
        
        with tab2:
            st.subheader(translation_manager.get_text('citing_works_statistics'))
            stats = results['citing_stats']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(translation_manager.get_text('total_citing_articles'), stats['n_items'])
                st.metric(translation_manager.get_text('unique_journals'), stats['unique_journals_count'])
                st.metric(translation_manager.get_text('unique_publishers'), stats['unique_publishers_count'])
                
            with col2:
                st.metric(translation_manager.get_text('total_references'), stats['total_refs'])
                st.metric(translation_manager.get_text('unique_affiliations'), stats['unique_affiliations_count'])
                st.metric(translation_manager.get_text('unique_countries'), stats['unique_countries_count'])
        
        with tab3:
            st.subheader(translation_manager.get_text('comparative_analysis'))
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    translation_manager.get_text('average_authors_per_article') + " (" + translation_manager.get_text('analyzed') + ")", 
                    f"{results['analyzed_stats']['auth_mean']:.1f}"
                )
                st.metric(
                    translation_manager.get_text('average_references_per_article') + " (" + translation_manager.get_text('analyzed') + ")", 
                    f"{results['analyzed_stats']['ref_mean']:.1f}"
                )
                
            with col2:
                st.metric(
                    translation_manager.get_text('average_authors_per_article') + " (" + translation_manager.get_text('citing') + ")", 
                    f"{results['citing_stats']['auth_mean']:.1f}"
                )
                st.metric(
                    translation_manager.get_text('average_references_per_article') + " (" + translation_manager.get_text('citing') + ")", 
                    f"{results['citing_stats']['ref_mean']:.1f}"
                )
        
        with tab4:
            st.subheader("🚀 " + translation_manager.get_text('fast_metrics'))
            fast_metrics = results.get('fast_metrics', {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(translation_manager.get_text('reference_age'), f"{fast_metrics.get('ref_median_age', 'N/A')} " + translation_manager.get_text('years'))
                st.metric(translation_manager.get_text('jscr'), f"{fast_metrics.get('JSCR', 0)}%")
                st.metric(translation_manager.get_text('cited_half_life'), f"{fast_metrics.get('cited_half_life_median', 'N/A')} " + translation_manager.get_text('years'))
                st.metric(translation_manager.get_text('fwci'), fast_metrics.get('FWCI', 0))
                
            with col2:
                st.metric(translation_manager.get_text('citation_velocity'), fast_metrics.get('citation_velocity', 0))
                st.metric(translation_manager.get_text('oa_impact_premium'), f"{fast_metrics.get('OA_impact_premium', 0)}%")
                st.metric(translation_manager.get_text('elite_index'), f"{fast_metrics.get('elite_index', 0)}%")
                st.metric(translation_manager.get_text('author_gini'), fast_metrics.get('author_gini', 0))
            
            # Detailed information
            st.subheader(translation_manager.get_text('fast_metrics_details'))
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(translation_manager.get_text('reference_age_details'))
                st.write(translation_manager.get_text('reference_age_median').format(value=fast_metrics.get('ref_median_age', 'N/A')))
                st.write(translation_manager.get_text('reference_age_mean').format(value=fast_metrics.get('ref_mean_age', 'N/A')))
                st.write(translation_manager.get_text('reference_age_percentile').format(value=f"{fast_metrics.get('ref_ages_25_75', ['N/A', 'N/A'])[0]}-{fast_metrics.get('ref_ages_25_75', ['N/A', 'N/A'])[1]}"))
                st.write(translation_manager.get_text('reference_age_analyzed').format(value=fast_metrics.get('total_refs_analyzed', 0)))
                
                st.write(translation_manager.get_text('jscr_details'))
                st.write(translation_manager.get_text('jscr_self_cites').format(value=fast_metrics.get('self_cites', 0)))
                st.write(translation_manager.get_text('jscr_total_cites').format(value=fast_metrics.get('total_cites', 0)))
                st.write(translation_manager.get_text('jscr_percentage').format(value=fast_metrics.get('JSCR', 0)))
            
            with col2:
                st.write(translation_manager.get_text('fwci_details'))
                st.write(translation_manager.get_text('fwci_value').format(value=fast_metrics.get('FWCI', 0)))
                st.write(translation_manager.get_text('fwci_total_cites').format(value=fast_metrics.get('total_cites', 0)))
                st.write(translation_manager.get_text('fwci_expected_cites').format(value=fast_metrics.get('expected_cites', 0)))
                
                st.write(translation_manager.get_text('dbi_details'))
                st.write(translation_manager.get_text('dbi_value').format(value=fast_metrics.get('DBI', 0)))
                st.write(translation_manager.get_text('dbi_unique_concepts').format(value=fast_metrics.get('unique_concepts', 0)))
                st.write(translation_manager.get_text('dbi_total_mentions').format(value=fast_metrics.get('total_concept_mentions', 0)))

        with tab5:
            st.subheader("🔮 Predictive Insights & Advanced Analytics")
            
            additional_data = results.get('additional_data', {})
            
            if additional_data:
                # Citation seasonality
                if 'citation_seasonality' in additional_data:
                    st.subheader("📅 Citation Seasonality")
                    
                    seasonality = additional_data['citation_seasonality']
                    
                    if seasonality['optimal_publication_months']:
                        st.write("**Recommended Publication Months:**")
                        for optimal in seasonality['optimal_publication_months']:
                            citation_month = datetime(2023, optimal['citation_month'], 1).strftime('%B')
                            pub_month = datetime(2023, optimal['recommended_publication_month'], 1).strftime('%B')
                            st.info(f"• Publish in **{pub_month}** to target high-citation month **{citation_month}**")
                
                # Potential reviewers
                if 'potential_reviewers' in additional_data:
                    st.subheader("👥 Potential Reviewer Discovery")
                    
                    reviewers = additional_data['potential_reviewers']
                    st.write(f"**Found {reviewers['total_potential_reviewers']} potential reviewers** who cite your journal but have never published in it.")
                    
                    if reviewers['potential_reviewers']:
                        st.write("**Top candidates:**")
                        for i, reviewer in enumerate(reviewers['potential_reviewers'][:5], 1):
                            st.write(f"{i}. **{reviewer['author']}** - {reviewer['citation_count']} citations")
            else:
                st.info("No additional predictive insights available for this analysis.")

# Run application
if __name__ == "__main__":
    main()


