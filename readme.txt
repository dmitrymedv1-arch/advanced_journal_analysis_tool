# Journal Analysis Tool - Complete User Guide
# Инструмент анализа журналов - Полное руководство пользователя
# 期刊分析工具 - 完整用户指南
# Outil d'analyse de revues - Guide complet de l'utilisateur
# ジャーナル分析ツール - 完全ユーザーガイド
# 도구 분석 저널 - 완전한 사용자 안내서
# Instrumento de análisis de revistas - Guía completa del usuario
# أداة تحليل المجلة - دليل المستخدم الكامل

================================================================================
ENGLISH / АНГЛИЙСКИЙ / 英语
================================================================================

## 🎯 About the Program

**Journal Analysis Tool** is a professional tool for comprehensive analysis of scientific journals that provides deep analytics of citations, metrics, and journal development trends.

### 🌟 Main Features

- **📊 Complete bibliometric analysis** - statistics of publications, citations, authors
- **🚀 Fast metrics** - 10+ key indicators without long loading
- **🎯 Special Analysis Mode** - calculation of CiteScore and Impact Factor analogues
- **🌍 Multilingual interface** - English and Russian languages
- **📚 Built-in dictionary** - learning scientific terms with progress tracking
- **🔮 Predictive analytics** - publication timing recommendations, reviewer search
- **📈 Interactive visualizations** - graphs and dashboards
- **📥 Detailed reports** - Excel files with 20+ data sheets

## 🚀 Quick Start

### Step 1: Main Analysis Parameters
- **Journal ISSN**: Enter the ISSN of the journal to analyze (e.g.: `2411-1414`)
- **Analysis Period**: Years or range (e.g.: `2020-2023`)
- **Special Analysis Mode**: Enable for calculating CiteScore/Impact Factor metrics

### Step 2: Starting Analysis
Click the **"Start Analysis"** button - the process will take from 5 to 30 minutes depending on data volume.

### Step 3: Exploring Results
- View results in dashboard tabs
- Download full Excel report
- Study metrics using the built-in dictionary

## 📊 Description of Main Metrics

### 🔬 Basic Indicators

| Metric | Description | Interpretation |
|--------|-------------|----------------|
| **H-index** | Hirsch index - productivity and impact | Higher = better. H-index 10 means 10 articles with ≥10 citations each |
| **Total Articles** | Number of analyzed publications | Scientific output volume of the journal |
| **Total Citations** | Sum of all article citations | Overall journal impact |
| **Average Citations per Article** | Citations/articles | Average influence of articles |

### 📈 Fast Metrics (calculation without API)

| Metric | Description | Normal Values |
|--------|-------------|---------------|
| **Reference Age** | Average age of references in articles | 5-8 years - modern journal, >10 years - classical |
| **JSCR** | Journal Self-Citation Rate | 10-20% - normal, >30% - possible isolation |
| **Cited Half-Life** | Time to receive half of citations | 2-4 years - fast sciences, >5 years - fundamental |
| **FWCI** | Field-Weighted Citation Impact | 1.0 - field average, >1.2 - above average |
| **Citation Velocity** | Citation speed (first 2 years) | Higher = faster recognition |
| **OA Impact Premium** | Open Access premium | +10-50% - normal range |
| **Elite Index** | Articles in top-10% by citations | >15% - excellent indicator |
| **Author Gini** | Publication inequality among authors | 0.1-0.3 - uniform, >0.6 - dominance |
| **DBI** | Thematic diversity | 0-1, higher = more diversified |

## 🎯 Special Analysis Mode

### What is it?
Special mode for calculating **CiteScore** and **Impact Factor** analogues according to Scopus and Web of Science methodology.

### How does it work?
- **CiteScore**: Analyzes period 1580-120 days from current date
- **Impact Factor**: Uses specific time windows (2+2 years)
- **Adjustments**: Considers only citations from indexed journals

### Result Interpretation:
- **CiteScore > 1.0** - above field average
- **Impact Factor > 3.0** - high-impact journal
- **Large difference** between regular and adjusted metrics indicates citations from non-indexed sources

## 📋 Excel Report Structure

### Main Sheets:

1. **Analyzed_Articles** - details of analyzed journal articles
2. **Citing_Works** - information about citing works
3. **Work_Overlaps** - author and affiliation overlaps
4. **First_Citations** - time to first citation (excluding editorial notes)
5. **Statistics** - combined statistics for all indicators

### Analytical Sheets:

6. **Citing_Stats** - citation metrics (H-index, citation accumulation)
7. **Citations_by_Year** - citation dynamics by year
8. **Citation_Accumulation_Curves** - citation accumulation curves
9. **Citation_Network** - citation network between years

### Participant Sheets:

10. **All_Authors_Analyzed** - journal authors (with name normalization)
11. **All_Authors_Citing** - citing work authors
12. **All_Affiliations_Analyzed/Citing** - affiliations
13. **All_Countries_Analyzed/Citing** - geographical distribution
14. **All_Journals_Citing** - citing journals with IF/CS metrics

### Special Sheets:

15. **Fast_Metrics** - all fast metrics in one table
16. **Top_Concepts** - top-10 thematic concepts
17. **Title_Keywords** - keyword analysis in titles
18. **Citation_Seasonality** - citation seasonality
19. **Optimal_Publication_Months** - publication timing recommendations
20. **Potential_Reviewers** - potential reviewers
21. **Special_Analysis_Metrics** - Special Analysis mode metrics

## 🌍 Multilingual Support

### Available Languages:
- **English** - default language
- **Russian** - complete interface and terms translation

### How to Change Language:
1. Open sidebar (left panel)
2. In "Language" section select desired language
3. Interface will switch immediately

## 📚 Dictionary of Terms

### Learning Features:
- **Term Search** - dropdown list of all metrics
- **Detailed Explanations** - definition, calculation, interpretation, examples
- **Progress Tracking** - statistics of learned terms
- **Categorization** - 7 metric categories for systematic learning

### Term Categories:
- 🔵 **Citations** - citation metrics
- 🟢 **References** - reference analysis
- 🟠 **Authors** - author statistics
- 🟣 **Themes** - thematic analysis
- 🔴 **Journal** - journal identifiers
- ⚫ **Technical** - technical aspects
- 🟤 **Databases** - databases

## 🔮 Predictive Analytics

### Citation Seasonality Analysis:
- **Identifying months** with highest citability
- **Publication timing recommendations** considering time to first citation
- **Visualization** of monthly citation distribution

### Potential Reviewer Search:
- **Automatic search** for authors who cite the journal but never published in it
- **Conflict of interest exclusion** - authors without journal connections
- **Ranking** by citation count

### Keyword Analysis:
- **Content words** - meaningful terms in titles
- **Compound words** - compound terms with hyphens
- **Scientific stopwords** - frequently used scientific terms
- **Comparison** of analyzed and citing articles

## 💡 Usage Tips

### For Best Results:
1. **Use exact ISSN** - check identifier correctness
2. **Start with short periods** - 2-3 years for testing
3. **Enable Special Analysis** for Scopus/WoS journals
4. **Study the dictionary** before deep metric analysis
5. **Download Excel report** for detailed study

### Data Interpretation:
- **Compare metrics** with journal's field of knowledge
- **Consider journal age** - young journals have different patterns
- **Analyze trends** - dynamics are more important than absolute values
- **Use multiple metrics** for comprehensive assessment

## ⚠️ Important Notes

### Data Limitations:
- Dependency on Crossref and OpenAlex data quality
- Processing time depends on number of articles and citations
- Some metrics require minimum data volume

### Recommendations:
- For large journals analyze sample periods
- Check data completeness via Crossref before analysis
- Use stable internet connection
- Save Excel reports for subsequent comparison

## 🆘 Support

### If Problems Occur:
1. **Check internet connection**
2. **Ensure ISSN correctness**
3. **Try reducing analysis period**
4. **Refresh browser page**

### For Complex Cases:
- Use Special Analysis mode for data verification
- Analyze journals with known metrics for calibration
- Refer to built-in dictionary for metric understanding

================================================================================
RUSSIAN / РУССКИЙ / 俄语
================================================================================

## 🎯 О программе

**Инструмент анализа журналов** - это профессиональный инструмент для комплексного анализа научных журналов, который предоставляет глубокую аналитику цитирования, метрик и тенденций развития журналов с использованием данных Crossref и OpenAlex.

### 🌟 Основные возможности

- **📊 Полный библиометрический анализ** - статистика публикаций, цитирований, авторов с использованием параллельной обработки
- **🚀 Быстрые метрики** - 15+ ключевых показателей без долгой загрузки с кэшированием
- **🎯 Режим Special Analysis** - расчет аналогов CiteScore и Impact Factor по методологии Scopus и WoS
- **🌍 Двуязычный интерфейс** - русский и английский языки с менеджером переводов
- **📚 Встроенный словарь** - обучение научным терминам с отслеживанием прогресса и категоризацией
- **🔮 Прогнозная аналитика** - рекомендации по времени публикации, поиск рецензентов, анализ сезонности
- **📈 Интерактивные визуализации** - графики Plotly и дашборды с 4 вкладками
- **📥 Детальные отчеты** - Excel файлы с 21+ листами данных, включая новые объединенные листы
- **🔍 ROR интеграция** - автоматический поиск данных об организациях через Research Organization Registry
- **👤 Author ID данные** - извлечение ORCID идентификаторов авторов
- **📅 Стратегии дат** - поддержка разных стратегий фильтрации статей по датам
- **⚡ Оптимизации** - параллельная обработка, ленивые вычисления, прогрессивная загрузка

## 🚀 Быстрый старт

### Шаг 1: Основные параметры анализа
- **ISSN журнала**: Введите ISSN анализируемого журнала (например: `2411-1414`)
- **Период анализа**: Годы или диапазон (например: `2020-2023`)
- **Режим Special Analysis**: Включите для расчета метрик CiteScore/Impact Factor по методологии Scopus/WoS
- **Стратегия дат**: Выберите стратегию определения дат публикации:
  - *Issue Priority*: Официальные даты публикации (рекомендуется)
  - *Start/Created*: Ранние даты размещения онлайн

### Шаг 2: Дополнительные опции
- **Включить ROR данные**: Получение информации об организациях для листа Combined_Affiliations
- **Включить Author ID данные**: Извлечение ORCID идентификаторов авторов
- **Сравнить стратегии дат**: Анализ различий между стратегиями фильтрации

### Шаг 3: Запуск анализа
Нажмите кнопку **"Start Optimized Analysis"** - процесс использует параллельную обработку и займет от 5 до 30 минут в зависимости от объема данных.

### Шаг 4: Изучение результатов
- Просматривайте результаты во вкладках дашборда
- Скачайте полный Excel отчет с 21+ листами
- Изучайте метрики с помощью встроенного словаря
- Используйте таймер анализа для отслеживания времени выполнения

## 📊 Подробное описание метрик

### 🔬 Базовые показатели

| Метрика | Описание | Интерпретация |
|---------|----------|---------------|
| **H-index** | Индекс Хирша - продуктивность и влияние | Выше = лучше. H-index 10 означает 10 статей с ≥10 цитирований каждая |
| **Общее число статей** | Количество проанализированных публикаций | Объем научной output журнала за выбранный период |
| **Общее число цитирований** | Суммарные цитирования всех статей | Общее влияние журнала в выбранный период |
| **Средние цитирования на статью** | Цитирования/статьи | Средняя влиятельность статей журнала |

### 📈 Быстрые метрики (расчет с кэшированием)

| Метрика | Описание | Нормальные значения | Расчет |
|---------|----------|---------------------|--------|
| **Reference Age** | Медианный возраст ссылок в статьях | 5-8 лет - современный журнал, >10 лет - классический | Возраст ссылок относительно года публикации |
| **JSCR** | Journal Self-Citation Rate | 10-20% - нормально, >30% - возможная изоляция | (Самоцитирования / Все цитирования) × 100% |
| **Cited Half-Life** | Медианное время получения половины цитирований | 2-4 года - быстрые науки, >5 лет - фундаментальные | Время от публикации до накопления 50% цитирований |
| **FWCI** | Field-Weighted Citation Impact | 1.0 - среднее поле, >1.2 - выше среднего | Фактические цитирования / Ожидаемые для данной области |
| **Citation Velocity** | Скорость цитирования (первые 2 года) | Выше = быстрее признание | Средние цитирования в год за первые 2 года |
| **OA Impact Premium** | Премия открытого доступа | +10-50% - обычный диапазон | ((OA цитирования - не-OA) / не-OA) × 100% |
| **Elite Index** | Статьи в топ-10% по цитированиям | >15% - отличный показатель | (Статьи в top-10% / Все статьи) × 100% |
| **Author Gini** | Коэффициент Джини для авторов | 0.1-0.3 - равномерно, >0.6 - доминирование | Статистика неравенства распределения публикаций |
| **DBI** | Индекс диверсификации тематик | 0-1, выше = более диверсифицировано | Нормализованный индекс Шеннона по темам |

### 🎯 Режим Special Analysis

**Что это такое?**
Специальный режим для расчета аналогов **CiteScore** и **Impact Factor** по точной методологии Scopus и Web of Science.

**Временные окна расчета:**
- **CiteScore**: Статьи, опубликованные 1580-120 дней назад, цитирования из того же периода
- **Impact Factor**: 
  - Статьи: опубликованные 1265-535 дней назад
  - Цитирования: опубликованные 534-170 дней назад

**Корректировки:**
- **CiteScore Corrected**: Только цитирования из журналов Scopus
- **Impact Factor Corrected**: Только цитирования из журналов Web of Science

**Интерпретация результатов:**
- **CiteScore > 1.0** - выше среднего по области
- **Impact Factor > 3.0** - высокоимпактный журнал
- **Большая разница** между обычными и скорректированными метриками указывает на цитирования из неиндексируемых источников

## 📋 ДЕТАЛЬНОЕ ОПИСАНИЕ ЛИСТОВ EXCEL ОТЧЕТА

### 📊 Основные листы данных

#### 1. **Лист: Analyzed_Articles**
**Описание:** Детальная информация о всех проанализированных статьях журнала за выбранный период.

| Колонка | Описание | Источник данных |
|---------|----------|-----------------|
| **DOI** | Цифровой идентификатор объекта статьи | Crossref DOI |
| **Title** | Название статьи на английском языке | Crossref title (первый элемент) |
| **Authors_Crossref** | Авторы в формате Crossref | Crossref author[given + family] |
| **Authors_OpenAlex** | Авторы в формате OpenAlex | OpenAlex authorships[display_name] |
| **Affiliations** | Аффилиации авторов | OpenAlex institutions[display_name] |
| **Countries** | Страны аффилиаций | OpenAlex institutions[country_code] |
| **Publication_Year** | Год публикации | Crossref published[date-parts][0] |
| **Journal** | Название журнала | Crossref container-title или OpenAlex host_venue |
| **Publisher** | Издатель | Crossref publisher или OpenAlex host_venue[publisher] |
| **ISSN** | ISSN журнала | Crossref ISSN или OpenAlex host_venue[issn] |
| **Reference_Count** | Количество ссылок в статье | Crossref reference-count или OpenAlex referenced_works_count |
| **Citations_Crossref** | Цитирования по Crossref | Crossref is-referenced-by-count |
| **Citations_OpenAlex** | Цитирования по OpenAlex | OpenAlex cited_by_count |
| **Author_Count** | Количество авторов | Crossref author (длина массива) |
| **Work_Type** | Тип работы (статья, обзор и т.д.) | Crossref type |
| **Used for SC** | Использована для расчета CiteScore | ✓ если статья в периоде 1580-120 дней |
| **Used for IF** | Использована для расчета Impact Factor | ✓ если статья в периоде 1265-535 дней |

#### 2. **Лист: Citing_Works**
**Описание:** Информация о всех работах, цитирующих анализируемые статьи.

| Колонка | Описание | Особенности |
|---------|----------|-------------|
| **DOI** | DOI цитирующей работы | Нормализованный DOI |
| **Title** | Название цитирующей работы | |
| **Authors_Crossref** | Авторы (Crossref) | |
| **Authors_OpenAlex** | Авторы (OpenAlex) | |
| **Affiliations** | Аффилиации авторов | |
| **Countries** | Страны | |
| **Publication_Year** | Год публикации | |
| **Journal** | Журнал публикации | |
| **Publisher** | Издатель | |
| **ISSN** | ISSN журнала | |
| **Reference_Count** | Количество ссылок | |
| **Citations_Crossref** | Цитирования (Crossref) | |
| **Citations_OpenAlex** | Цитирования (OpenAlex) | |
| **Author_Count** | Количество авторов | |
| **Work_Type** | Тип работы | |
| **Used for SC** | Использована для CiteScore | ✓ если в периоде 1580-120 дней |
| **Used for SC_corr** | Использована для скорректированного CiteScore | ✓ если журнал в Scopus |
| **Used for IF** | Использована для Impact Factor | ✓ если в периоде 534-170 дней |
| **Used for IF_corr** | Использована для скорректированного IF | ✓ если журнал в WoS |

#### 3. **Лист: Work_Overlaps**
**Описание:** Пересечения авторов и аффилиаций между анализируемыми и цитирующими статьями.

| Колонка | Описание |
|---------|----------|
| **Analyzed_DOI** | DOI анализируемой статьи |
| **Citing_DOI** | DOI цитирующей статьи |
| **Common_Authors** | Общие авторы между статьями |
| **Common_Authors_Count** | Количество общих авторов |
| **Common_Affiliations** | Общие аффилиации |
| **Common_Affiliations_Count** | Количество общих аффилиаций |

#### 4. **Лист: First_Citations**
**Описание:** Время до первого цитирования с исключением редакторских заметок.

| Колонка | Описание | Фильтрация |
|---------|----------|------------|
| **Analyzed_DOI** | DOI анализируемой статьи | Нормализованный DOI |
| **First_Citing_DOI** | DOI первой цитирующей работы | Нормализованный DOI |
| **Publication_Date** | Дата публикации статьи | Формат ГГГГ-ММ-ДД |
| **First_Citation_Date** | Дата первого цитирования | Формат ГГГГ-ММ-ДД |
| **Days_to_First_Citation** | Дней до первого цитирования | Расчет в днях |
| **Same_DOI_Prefix** | Одинаковый префикс DOI | ✓ если префиксы совпадают |
| **Same_Publication_Date** | Одинаковая дата публикации | ✓ если даты совпадают |
| **Editorial_Note_Excluded** | Редакторская заметка исключена | ✓ если Same_DOI_Prefix AND Same_Publication_Date |

**Важно:** Записи с Editorial_Note_Excluded = TRUE исключаются из статистических расчетов.

### 📈 Аналитические листы

#### 5. **Лист: Statistics**
**Описание:** Объединенная статистика по анализируемым и цитирующим статьям.

| Строка | Описание для анализируемых | Описание для цитирующих |
|--------|----------------------------|-------------------------|
| **Total Articles** | Общее число статей журнала за период | Общее число цитирующих работ |
| **Total References** | Общее число ссылок во всех статьях | Общее число ссылок в цитирующих работах |
| **References with DOI** | Ссылки с указанным DOI | Ссылки с указанным DOI |
| **References without DOI** | Ссылки без DOI | Ссылки без DOI |
| **Self-Citations** | Самоцитирования журнала | Самоцитирования цитирующих журналов |
| **Single Author Articles** | Статьи с одним автором | Цитирующие работы с одним автором |
| **Articles with >10 Authors** | Статьи с более чем 10 авторами | Работы с более чем 10 авторами |
| **Minimum References** | Минимальное число ссылок в статье | Минимальное число ссылок |
| **Maximum References** | Максимальное число ссылок в статье | Максимальное число ссылок |
| **Average References** | Среднее число ссылок на статью | Среднее число ссылок |
| **Median References** | Медианное число ссылок | Медианное число ссылок |
| **Minimum Authors** | Минимальное число авторов в статье | Минимальное число авторов |
| **Maximum Authors** | Максимальное число авторов в статье | Максимальное число авторов |
| **Average Authors** | Среднее число авторов на статью | Среднее число авторов |
| **Median Authors** | Медианное число авторов | Медианное число авторов |
| **Single Country Articles** | Статьи с авторами из одной страны | Работы из одной страны |
| **Multiple Country Articles** | Статьи с международной коллаборацией | Международные работы |
| **No Country Data Articles** | Статьи без данных о стране | Работы без данных о стране |
| **Total Affiliations** | Общее число упоминаний аффилиаций | Общее число упоминаний |
| **Unique Affiliations** | Уникальные аффилиации | Уникальные аффилиации |
| **Unique Countries** | Уникальные страны | Уникальные страны |
| **Unique Journals** | Уникальные журналы (для перекрестных публикаций) | Уникальные цитирующие журналы |
| **Unique Publishers** | Уникальные издатели | Уникальные издатели |
| **Articles with ≥10 citations** | Статьи с ≥10 цитированиями | N/A (не применимо) |
| **Articles with ≥20 citations** | Статьи с ≥20 цитированиями | N/A |
| **Articles with ≥30 citations** | Статьи с ≥30 цитированиями | N/A |
| **Articles with ≥50 citations** | Статьи с ≥50 цитированиями | N/A |

#### 6. **Лист: Citing_Stats**
**Описание:** Статистика цитирования анализируемых статей.

| Строка | Описание |
|--------|----------|
| **H-index** | Индекс Хирша для анализируемых статей |
| **Total Citations** | Общее количество цитирований всех статей |
| **Average Citations per Article** | Среднее количество цитирований на статью |
| **Maximum Citations** | Максимальное количество цитирований у одной статьи |
| **Minimum Citations** | Минимальное количество цитирований (обычно 0) |
| **Articles with Citations** | Количество статей, имеющих хотя бы одно цитирование |
| **Articles without Citations** | Количество статей без цитирований |
| **Minimum Days to First Citation** | Минимальное время до первого цитирования (в днях) |
| **Maximum Days to First Citation** | Максимальное время до первого цитирования |
| **Average Days to First Citation** | Среднее время до первого цитирования |
| **Median Days to First Citation** | Медианное время до первого цитирования |
| **Articles with Citation Timing Data** | Количество статей с данными о времени цитирования |
| **Total Years Covered by Citation Data** | Количество лет, охваченных данными о цитированиях |

#### 7. **Лист: Citations_by_Year**
**Описание:** Распределение цитирований по годам.

| Колонка | Описание |
|---------|----------|
| **Year** | Год цитирования |
| **Citations_Count** | Количество цитирований в этом году |

#### 8. **Лист: Citation_Network**
**Описание:** Сеть цитирований между годами публикации и цитирования.

| Колонка | Описание |
|---------|----------|
| **Publication_Year** | Год публикации статьи |
| **Citation_Year** | Год цитирования статьи |
| **Citations_Count** | Количество цитирований в этой паре лет |

**Сортировка:** Сначала по году публикации, затем по году цитирования.

### 👥 Листы по участникам (объединенные)

#### 9. **Лист: Combined_Authors**
**Описание:** Объединенный список авторов анализируемых и цитирующих статей с нормализацией имен.

| Колонка | Описание | Расчет |
|---------|----------|--------|
| **Author** | Имя автора (Фамилия Первый_инициал.) | Нормализация: Pikalova E.Y. → Pikalova E. |
| **Total** | Общее число публикаций автора | Analyzed_Count + Citing_Count |
| **Status** | Статус автора: "Both", "Analyzed Only", "Citing Only" | Определяется по источникам |
| **Analyzed_Count** | Число публикаций в анализируемом журнале | |
| **Citing_Count** | Число цитирующих работ автора | |
| **Loyalty_Score** | Лояльность автору журнала | (Analyzed_Count / Total) × 100% |
| **Activity_Balance** | Баланс активности: "Publishing-Only", "Citing-Only", "Publishing-Heavy", "Balanced", "Citing-Heavy" | На основе Loyalty_Score |
| **Analyzed_Pct** | Доля среди анализируемых статей | (Analyzed_Count / Total_Analyzed) × 100% |
| **Citing_Pct** | Доля среди цитирующих работ | (Citing_Count / Total_Citing) × 100% |

#### 10. **Лист: Combined_Affiliations**
**Описание:** Объединенный список аффилиаций с данными ROR.

| Колонка | Описание | Источник данных |
|---------|----------|-----------------|
| **Affiliation** | Название организации | OpenAlex institutions[display_name] |
| **Colab-ROR** | Ссылка на организацию в Colab.ws | ROR API → https://colab.ws/organizations/{ror_id} |
| **Website** | Веб-сайт организации | ROR API links[value] |
| **Total** | Общее число упоминаний | Analyzed_Count + Citing_Count |
| **Status** | Статус: "Both", "Analyzed Only", "Citing Only" | |
| **Analyzed_Count** | Упоминания в анализируемых статьях | |
| **Citing_Count** | Упоминания в цитирующих работах | |
| **Engagement_Score** | Уровень вовлеченности с журналом | (Analyzed_Count / Total) × 100% |
| **Activity_Balance** | Баланс активности (аналогично авторам) | |
| **Analyzed_Pct** | Доля среди анализируемых | |
| **Citing_Pct** | Доля среди цитирующих | |

**Примечание:** Данные ROR загружаются только при включении опции "Include ROR data".

#### 11. **Лист: Combined_Countries**
**Описание:** Объединенный список стран.

| Колонка | Описание | Расчет |
|---------|----------|--------|
| **Country** | Код страны (2 буквы) | OpenAlex institutions[country_code] |
| **Total** | Общее число упоминаний | |
| **Status** | Статус: "Both", "Analyzed Only", "Citing Only" | |
| **Analyzed_Count** | Упоминания в анализируемых | |
| **Citing_Count** | Упоминания в цитирующих | |
| **Self_Sufficiency** | Самодостаточность | (Analyzed_Count / Total) × 100% |
| **Global_Reach** | Глобальный охват | (Citing_Count / Total) × 100% |
| **Analyzed_Pct** | Доля среди анализируемых | |
| **Citing_Pct** | Доля среди цитирующих | |

#### 12. **Лист: All_Journals_Citing**
**Описание:** Журналы, цитирующие анализируемый журнал, с метриками IF/CS.

| Колонка | Описание | Источник данных |
|---------|----------|-----------------|
| **Journal** | Название цитирующего журнала | Crossref container-title |
| **ISSN_1** | Основной ISSN журнала | Crossref ISSN[0] |
| **ISSN_2** | Дополнительный ISSN (e-ISSN) | Crossref ISSN[1] |
| **Journal_Website** | Веб-сайт журнала | OpenAlex host_venue[homepage_url] |
| **Articles_Count** | Количество цитирующих статей из этого журнала | |
| **Percentage** | Доля от общего числа цитирующих работ | (Count / Total_Citing) × 100% |
| **IF (WoS)** | Impact Factor (Web of Science) | IF.xlsx по ISSN |
| **Q(WoS)** | Квартиль в WoS | IF.xlsx Quartile |
| **SC(Scopus)** | CiteScore (Scopus) | CS.xlsx CiteScore |
| **Q(Scopus)** | Квартиль в Scopus | CS.xlsx Quartile |

#### 13. **Лист: All_Publishers_Citing**
**Описание:** Издатели цитирующих работ.

| Колонка | Описание |
|---------|----------|
| **Publisher** | Название издателя |
| **Articles_Count** | Количество работ этого издателя |
| **Percentage** | Доля от общего числа |

### 📊 Специальные аналитические листы

#### 14. **Лист: Fast_Metrics**
**Описание:** Все быстрые метрики в одной таблице.

| Строка | Описание | Метод расчета |
|--------|----------|---------------|
| **Reference Age (median)** | Медианный возраст ссылок | NP.median(возрастов ссылок) |
| **Reference Age (mean)** | Средний возраст ссылок | NP.mean(возрастов ссылок) |
| **Reference Age (25-75 percentile)** | Интерквартильный размах | [25-й перцентиль, 75-й перцентиль] |
| **References Analyzed** | Количество проанализированных ссылок | |
| **Journal Self-Citation Rate (JSCR)** | Процент самоцитирований журнала | (Self-cites / Total cites) × 100% |
| **Journal Self-Citations** | Абсолютное число самоцитирований | |
| **Total Citations for JSCR** | Общее число цитирований для расчета JSCR | |
| **Cited Half-Life (median)** | Медианная полужизнь цитирований | Медиана времени до 50% цитирований |
| **Cited Half-Life (mean)** | Средняя полужизнь цитирований | Среднее время до 50% цитирований |
| **Articles with CHL Data** | Статьи с данными для расчета полужизни | |
| **Field-Weighted Citation Impact (FWCI)** | Взвешенный по области индекс цитирования | Реальные цитирования / Ожидаемые |
| **Total Citations** | Общее число цитирований для FWCI | |
| **Expected Citations** | Ожидаемое число цитирований | На основе концептов OpenAlex |
| **Citation Velocity** | Скорость цитирования | Средние цитирования/год за первые 2 года |
| **Articles with Velocity Data** | Статьи с данными о скорости | |
| **OA Impact Premium** | Премия открытого доступа | ((OA avg - non-OA avg) / non-OA avg) × 100% |
| **OA Articles** | Число статей OA | OpenAlex open_access[is_oa] = true |
| **Non-OA Articles** | Число статей не-OA | OpenAlex open_access[is_oa] = false |
| **Average OA Citations** | Средние цитирования OA статей | |
| **Average Non-OA Citations** | Средние цитирования не-OA статей | |
| **Elite Index** | Индекс элитных статей | % статей в top-10% по цитированиям |
| **Elite Articles** | Число элитных статей | |
| **Citation Threshold** | Порог для elite (абсолютное значение) | |
| **Author Gini Index** | Индекс Джини для авторов | 0 (равенство) - 1 (неравенство) |
| **Total Authors** | Общее число уникальных авторов | |
| **Average Articles per Author** | Среднее число статей на автора | |
| **Median Articles per Author** | Медианное число статей на автора | |
| **Diversity Balance Index (DBI)** | Индекс тематического разнообразия | Нормализованный индекс Шеннона |
| **Unique Concepts** | Уникальные тематические концепты | OpenAlex concepts[display_name] |
| **Total Concept Mentions** | Общее число упоминаний концептов | |

#### 15. **Лист: Terms_and_Topics**
**Описание:** Статистика по терминам и темам с полной иерархией.

| Колонка | Описание | Источник |
|---------|----------|---------|
| **Term** | Термин или тема | OpenAlex concepts[display_name] |
| **Type** | Тип: "Topic", "Subfield", "Field", "Domain", "Concept" | Определяется по позиции в списке |
| **Analyzed count** | Количество в анализируемых статьях | |
| **Citing Count** | Количество в цитирующих работах | |
| **Analyzed norm count** | Нормализованный счетчик (по score концептов) | concepts[score] / total articles |
| **Citing norm Count** | Нормализованный счетчик для цитирующих | |
| **Total norm count** | Общий нормализованный счетчик | Analyzed_norm + Citing_norm |
| **First_Year** | Первый год упоминания термина | |
| **Peak_Year** | Год пикового упоминания | |
| **Recent_5_Years_Count** | Упоминания за последние 5 лет | |

#### 16. **Лист: Combined_Title_Keywords**
**Описание:** Объединенный анализ ключевых слов в названиях.

| Колонка | Описание | Типы ключевых слов |
|---------|----------|-------------------|
| **Rank** | Ранк по популярности | |
| **Keyword Type** | Тип: "Content", "Compound", "Scientific" | Content: обычные слова; Compound: через дефис; Scientific: научные стоп-слова |
| **Keyword** | Ключевое слово | |
| **Norm_Analyzed** | Нормализованная частота в анализируемых | Count / Total_Analyzed_Titles |
| **Norm_Citing** | Нормализованная частота в цитирующих | Count / Total_Citing_Titles |
| **Total_Norm** | Общая нормализованная частота | Norm_Analyzed + Norm_Citing |
| **Ratio_Analyzed/Citing** | Отношение частот | Norm_Analyzed / Norm_Citing |

#### 17. **Лист: Citation_Seasonality**
**Описание:** Сезонность цитирований по месяцам.

| Колонка | Описание |
|---------|----------|
| **Month_Number** | Номер месяца (1-12) |
| **Month_Name** | Название месяца |
| **Citation_Count** | Количество цитирований в этом месяце |
| **Publication_Count** | Количество публикаций в этом месяце |

#### 18. **Лист: Optimal_Publication_Months**
**Описание:** Рекомендации по оптимальным месяцам публикации.

| Колонка | Описание |
|---------|----------|
| **High_Citation_Month** | Месяц с высокой цитируемостью |
| **Citation_Count** | Количество цитирований в этом месяце |
| **Recommended_Publication_Month** | Рекомендуемый месяц публикации |
| **Reasoning** | Обоснование рекомендации |

**Расчет:** Рекомендуемый месяц = Высокоцитируемый месяц - (Медианное время до первого цитирования в днях / 30)

#### 19. **Лист: Potential_Reviewers**
**Описание:** Потенциальные рецензенты из авторов цитирующих работ.

| Колонка | Описание | Критерии отбора |
|---------|----------|-----------------|
| **Author** | Имя автора | |
| **Citation_Count** | Количество цитирований журнала этим автором | |
| **Citing_DOI** | DOI цитирующей работы | Автор НЕ публиковался в журнале и НЕ входит в overlap authors |

#### 20. **Лист: Special_Analysis_Metrics**
**Описание:** Метрики режима Special Analysis.

| Строка | Описание | Формула |
|--------|----------|---------|
| **CiteScore (A/B)** | Обычный CiteScore | A / B |
| **CiteScore Corrected (C/B)** | Скорректированный CiteScore | C / B |
| **Impact Factor (E/D)** | Обычный Impact Factor | E / D |
| **Impact Factor Corrected (F/D)** | Скорректированный Impact Factor | F / D |
| **B (Articles for CiteScore)** | Статьи для расчета CiteScore | Статьи за период 1580-120 дней |
| **A (Citations for CiteScore)** | Цитирования для CiteScore | Все цитирования из того же периода |
| **C (Scopus Citations for CiteScore)** | Цитирования из Scopus | Только из журналов Scopus |
| **D (Articles for Impact Factor)** | Статьи для Impact Factor | Статьи за период 1265-535 дней |
| **E (Citations for Impact Factor)** | Цитирования для Impact Factor | Цитирования за период 534-170 дней |
| **F (WoS Citations for Impact Factor)** | Цитирования из WoS | Только из журналов Web of Science |

#### 21. **Лист: Author_ID_data** (НОВЫЙ)
**Описание:** Данные об идентификаторах авторов.

| Колонка | Описание | Источник данных |
|---------|----------|-----------------|
| **Full Name** | Полное имя автора (Фамилия Имя) | Форматирование из raw_author_name |
| **Surname** | Фамилия | Первое слово из Full Name |
| **Given Name** | Имя | Остальные слова из Full Name |
| **Affiliation** | Основная аффилиация | Первая аффилиация из OpenAlex |
| **.** | Пустая колонка-разделитель | |
| **ORCID ID** | ORCID идентификатор | Crossref ORCID или OpenAlex orcid |
| **Sources** | Источники: "analyzed", "citing" | Указывает откуда извлечен автор |

**Примечание:** Scopus ID и WoS ID временно не поддерживаются в текущей версии.

## 🌍 Мультиязычность

### Доступные языки:
- **Английский** - язык по умолчанию
- **Русский** - полный перевод интерфейса и терминов

### Как сменить язык:
1. Откройте сайдбар (левая панель)
2. В разделе "Language" выберите нужный язык
3. Интерфейс мгновенно переключится через translation_manager

## 📚 Словарь терминов

### Функциональность обучения:
- **Поиск терминов** - выпадающий список всех 16 метрик
- **Детальные объяснения** - определение, расчет, интерпретация, примеры, категория
- **Отслеживание прогресса** - статистика изученных терминов в session_state
- **Категоризация** - 7 категорий метрик для системного изучения
- **Автоматические подсказки** - контекстные тултипы в интерфейсе

### Категории терминов:
- 🔵 **Citations** - метрики цитирования (H-index, JSCR, FWCI, Elite Index)
- 🟢 **References** - анализ ссылок (Reference Age, Self-Cites)
- 🟠 **Authors** - авторская статистика (Author Gini)
- 🟣 **Themes** - тематический анализ (DBI)
- 🔴 **Journal** - журнальные идентификаторы (ISSN, DOI)
- ⚫ **Technical** - технические аспекты
- 🟤 **Databases** - базы данных (Crossref, OpenAlex)

## 🔮 Прогнозная аналитика

### Анализ сезонности цитирований:
- **Выявление месяцев** с наибольшей цитируемостью через Counter по месяцам
- **Рекомендации по времени публикации** с учетом медианного времени до первого цитирования
- **Визуализация** помесячного распределения цитирований и публикаций

### Поиск потенциальных рецензентов:
- **Автоматический поиск** авторов, которые цитируют журнал ≥2 раз, но никогда в нем не публиковались
- **Исключение конфликта интересов** - удаление авторов журнала и overlap authors
- **Ранжирование** по количеству цитирований (most_common)
- **Детализация** - список всех цитирующих DOI для каждого автора

### Анализ ключевых слов в названиях:
- **Content words** - значимые термины (удалены стоп-слова и слово "sub")
- **Compound words** - составные термины через дефис (например, "high-performance")
- **Scientific stopwords** - часто используемые научные термины (более 200 слов)
- **Сравнение** анализируемых и цитирующих статей через нормализованные частоты
- **Стемминг Porter** для приведения к основной форме

### Анализ терминов и тем:
- **Полная иерархия**: Topic → Subfield → Field → Domain → Concepts
- **Взвешивание по score** концептов OpenAlex
- **Исторический анализ** - первый год, пиковый год, активность за 5 лет
- **Нормализация** по количеству статей с концептами

## ⚡ Технические оптимизации

### Параллельная обработка:
- **ThreadPoolExecutor** для загрузки метаданных (max_workers=5)
- **Parallel metrics calculation** - одновременный расчет 4 групп метрик
- **Parallel analyses** - 5 независимых анализов одновременно
- **Smart batching** - адаптивные размеры батчей по типу операции

### Кэширование:
- **Многоуровневое кэширование** - 10+ специализированных кэшей
- **Дисковый кэш** CacheManager для persistence
- **In-memory кэши** для частых операций
- **Прогрессивное кэширование** predictive_cache_warmup

### Оптимизации производительности:
- **Ленивые вычисления** LazyMetricsCalculator
- **Прогрессивная загрузка** progressive_analysis
- **Обработка чанками** process_data_in_chunks (по 500 записей)
- **Адаптивные задержки** AdaptiveDelayer

### Обработка ошибок:
- **Retry декоратор** с exponential backoff
- **Грациозная обработка** через handle_analysis_errors
- **Валидация данных** на всех этапах
- **Резервные стратегии** для API failures

## 💡 Расширенные советы по использованию

### Для лучших результатов:
1. **Используйте точный ISSN** - проверьте корректность идентификатора в Crossref
2. **Начинайте с коротких периодов** - 2-3 года для тестирования, затем расширяйте
3. **Включите Special Analysis** для журналов из Scopus/WoS для сравнения метрик
4. **Изучайте словарь** перед глубоким анализом метрик - отметьте "I understood"
5. **Скачивайте Excel отчет** для детального изучения всех 21 листов
6. **Используйте ROR данные** для полной информации об организациях
7. **Проверяйте Author ID данные** для поиска ORCID исследователей
8. **Сравнивайте стратегии дат** если возникают расхождения в количестве статей

### Интерпретация данных:
- **Сравнивайте метрики** с областью знаний журнала (разные области имеют разные baseline)
- **Учитывайте возраст журнала** - молодые журналы имеют другие паттерны цитирования
- **Анализируйте тренды** - динамика изменения метрик важнее абсолютных значений
- **Используйте несколько метрик** для комплексной оценки (не полагайтесь на одну метрику)
- **Обращайте внимание на JSCR** - высокие значения (>30%) требуют дополнительного исследования
- **Используйте Combined листы** для анализа связей между журналом и цитирующим сообществом

### Работа с большими объемами данных:
- **Для больших журналов** анализируйте выборочные периоды (например, по 2 года)
- **Используйте прогрессивную загрузку** - сначала базовые метрики, затем детальные
- **Мониторьте использование памяти** - инструмент очищает кэши автоматически
- **Сохраняйте промежуточные результаты** через download Excel

## ⚠️ Важные примечания и ограничения

### Ограничения данных:
- **Зависимость от API** - качество данных зависит от Crossref и OpenAlex
- **Время обработки** зависит от количества статей и цитирований (30+ минут для больших журналов)
- **Некоторые метрики** требуют минимального объема данных для корректного расчета
- **Лицензионные ограничения** - метрики IF/CS доступны только если загружены файлы IF.xlsx и CS.xlsx
- **ROR API лимиты** - ограничения на количество запросов к Research Organization Registry

### Особенности расчета:
- **Editorial notes исключаются** из времени до первого цитирования
- **Нормализация имен авторов** - используются только первые инициалы
- **Стратегии дат** могут давать разные результаты - используйте сравнение
- **Кэширование агрессивное** - перезапустите анализ для обновления данных

### Рекомендации по файлам метрик:
- **IF.xlsx** должен содержать колонки: ISSN, eISSN, IF, Quartile
- **CS.xlsx** должен содержать колонки: Print ISSN, E-ISSN, CiteScore, Quartile
- **Формат ISSN** - поддерживаются как с дефисом, так и без
- **Обновление файлов** - загружайте актуальные версии для корректных метрик

## 🆘 Поддержка и устранение проблем

### Типичные проблемы и решения:

1. **"No articles found"**
   - Проверьте корректность ISSN
   - Увеличьте период анализа
   - Попробуйте другую стратегию дат
   - Проверьте доступность Crossref API

2. **Долгая обработка**
   - Сократите период анализа
   - Отключите дополнительные опции (ROR, Author ID)
   - Используйте более узкий диапазон лет
   - Проверьте интернет-соединение

3. **Ошибки Excel генерации**
   - Уменьшите объем данных
   - Проверьте доступную память
   - Используйте более простой период
   - Перезапустите приложение

4. **Проблемы с метриками IF/CS**
   - Проверьте наличие файлов IF.xlsx и CS.xlsx
   - Убедитесь в корректности формата файлов
   - Проверьте соответствие ISSN в файлах
   - Используйте нормализованные ISSN

### Для сложных случаев:
- Используйте режим **Special Analysis** для проверки корректности данных
- Анализируйте **журналы с известными метриками** для калибровки инструмента
- Обращайтесь к **встроенному словарю** для понимания методологии расчета метрик
- Проверяйте **логи в консоли** разработчика для диагностики ошибок
- Используйте **параллельную обработку** для ускорения работы с большими данными

### Контакты для поддержки:
- **Документация**: README.txt (доступен для скачивания в сайдбаре)
- **Исходный код**: Полный код с комментариями
- **Версия**: Journal Analysis Tool v2.0 с оптимизациями
- **Обновления**: Регулярные улучшения производительности и функциональности

---

**Инструмент анализа журналов** предоставляет профессиональный инструментарий для редакторов, библиометриков, исследователей и научных администраторов, позволяющий проводить комплексный анализ научных журналов с использованием современных методов, метрик и технологий параллельной обработки данных.

**Обновления в версии 2.0:**
- Добавлены 3 новых листа Excel (Combined_Authors, Combined_Affiliations, Combined_Countries)
- Реализована интеграция с ROR для данных об организациях
- Добавлен лист Author_ID_data с ORCID идентификаторами
- Улучшена производительность через параллельную обработку
- Добавлены стратегии работы с датами публикации
- Расширен словарь терминов с системой обучения
- Улучшена обработка ошибок и устойчивость к API сбоям

================================================================================
CHINESE / КИТАЙСКИЙ / 中文
================================================================================

## 🎯 关于程序

**期刊分析工具**是一个用于全面分析科学期刊的专业工具，提供引用、指标和期刊发展趋势的深入分析。

### 🌟 主要功能

- **📊 完整的文献计量分析** - 出版物、引用、作者的统计数据
- **🚀 快速指标** - 10+个关键指标，无需长时间加载
- **🎯 特殊分析模式** - 计算CiteScore和影响因子类似指标
- **🌍 多语言界面** - 英语和俄语
- **📚 内置词典** - 学习科技术语并跟踪进度
- **🔮 预测分析** - 发表时间建议、审稿人搜索
- **📈 交互式可视化** - 图表和仪表板
- **📥 详细报告** - 包含20+个工作表的Excel文件

## 🚀 快速入门

### 第1步：主要分析参数
- **期刊ISSN**：输入要分析的期刊ISSN（例如：`2411-1414`）
- **分析期间**：年份或范围（例如：`2020-2023`）
- **特殊分析模式**：启用以计算CiteScore/影响因子指标

### 第2步：开始分析
点击**"开始分析"**按钮 - 根据数据量，过程需要5到30分钟。

### 第3步：探索结果
- 在仪表板选项卡中查看结果
- 下载完整的Excel报告
- 使用内置词典研究指标

## 📊 主要指标说明

### 🔬 基本指标

| 指标 | 描述 | 解释 |
|------|------|------|
| **H指数** | 赫希指数 - 生产力和影响力 | 越高越好。H指数10表示10篇文章，每篇≥10次引用 |
| **总文章数** | 分析的出版物数量 | 期刊的科学产出量 |
| **总引用数** | 所有文章引用的总和 | 期刊的总体影响力 |
| **每篇文章平均引用** | 引用数/文章数 | 文章的平均影响力 |

### 📈 快速指标（无需API计算）

| 指标 | 描述 | 正常值 |
|------|------|--------|
| **参考文献年龄** | 文章中参考文献的平均年龄 | 5-8年 - 现代期刊，>10年 - 经典期刊 |
| **JSCR** | 期刊自引率 | 10-20% - 正常，>30% - 可能孤立 |
| **被引半衰期** | 获得一半引用的时间 | 2-4年 - 快速科学，>5年 - 基础科学 |
| **FWCI** | 领域加权引用影响 | 1.0 - 领域平均，>1.2 - 高于平均 |
| **引用速度** | 引用速度（前2年） | 越高 = 认可越快 |
| **OA影响溢价** | 开放获取溢价 | +10-50% - 正常范围 |
| **精英指数** | 按引用排名前10%的文章 | >15% - 优秀指标 |
| **作者基尼系数** | 作者间的发表不平等 | 0.1-0.3 - 均匀，>0.6 - 主导 |
| **DBI** | 主题多样性 | 0-1，越高 = 越多样化 |

## 🎯 特殊分析模式

### 这是什么？
根据Scopus和Web of Science方法计算**CiteScore**和**影响因子**类似指标的特殊模式。

### 工作原理？
- **CiteScore**：分析当前日期前1580-120天的期间
- **影响因子**：使用特定时间窗口（2+2年）
- **调整**：仅考虑来自索引期刊的引用

### 结果解释：
- **CiteScore > 1.0** - 高于领域平均
- **影响因子 > 3.0** - 高影响力期刊
- **常规与调整指标之间的巨大差异**表明来自非索引来源的引用

================================================================================
FRENCH / ФРАНЦУЗСКИЙ / 法语
================================================================================

## 🎯 À propos du programme

**Outil d'analyse de revues** est un outil professionnel pour l'analyse complète des revues scientifiques qui fournit des analyses approfondies des citations, des métriques et des tendances de développement des revues.

### 🌟 Principales fonctionnalités

- **📊 Analyse bibliométrique complète** - statistiques des publications, citations, auteurs
- **🚀 Métriques rapides** - 10+ indicateurs clés sans chargement long
- **🎯 Mode d'analyse spéciale** - calcul des analogues de CiteScore et du facteur d'impact
- **🌍 Interface multilingue** - anglais et russe
- **📚 Dictionnaire intégré** - apprentissage des termes scientifiques avec suivi des progrès
- **🔮 Analyse prédictive** - recommandations de calendrier de publication, recherche de réviseurs
- **📈 Visualisations interactives** - graphiques et tableaux de bord
- **📥 Rapports détaillés** - fichiers Excel avec 20+ feuilles de données

## 🚀 Démarrage rapide

### Étape 1 : Paramètres principaux d'analyse
- **ISSN de la revue** : Entrez l'ISSN de la revue à analyser (ex. : `2411-1414`)
- **Période d'analyse** : Années ou plage (ex. : `2020-2023`)
- **Mode d'analyse spéciale** : Activez pour calculer les métriques CiteScore/facteur d'impact

### Étape 2 : Lancement de l'analyse
Cliquez sur le bouton **"Start Analysis"** - le processus prendra de 5 à 30 minutes selon le volume de données.

### Étape 3 : Exploration des résultats
- Consultez les résultats dans les onglets du tableau de bord
- Téléchargez le rapport Excel complet
- Étudiez les métriques à l'aide du dictionnaire intégré

## 📊 Description des principales métriques

### 🔬 Indicateurs de base

| Métrique | Description | Interprétation |
|----------|-------------|----------------|
| **H-index** | Indice de Hirsch - productivité et impact | Plus élevé = mieux. H-index 10 signifie 10 articles avec ≥10 citations chacun |
| **Nombre total d'articles** | Nombre de publications analysées | Volume de production scientifique de la revue |
| **Nombre total de citations** | Somme de toutes les citations d'articles | Impact global de la revue |
| **Moyenne de citations par article** | Citations/articles | Influence moyenne des articles |

### 📈 Métriques rapides (calcul sans API)

| Métrique | Description | Valeurs normales |
|----------|-------------|------------------|
| **Âge des références** | Âge moyen des références dans les articles | 5-8 ans - revue moderne, >10 ans - classique |
| **JSCR** | Taux d'auto-citation de la revue | 10-20% - normal, >30% - isolement possible |
| **Demi-vie de citation** | Temps pour recevoir la moitié des citations | 2-4 ans - sciences rapides, >5 ans - fondamentales |
| **FWCI** | Impact de citation pondéré par domaine | 1.0 - moyenne du domaine, >1.2 - au-dessus de la moyenne |
| **Vitesse de citation** | Vitesse de citation (2 premières années) | Plus élevé = reconnaissance plus rapide |
| **Prime d'impact OA** | Prime d'accès ouvert | +10-50% - plage normale |
| **Indice d'élite** | Articles dans le top 10% par citations | >15% - indicateur excellent |
| **Gini des auteurs** | Inégalité des publications parmi les auteurs | 0.1-0.3 - uniforme, >0.6 - dominance |
| **DBI** | Diversité thématique | 0-1, plus élevé = plus diversifié |

## 🎯 Mode d'analyse spéciale

### Qu'est-ce que c'est ?
Mode spécial pour calculer les analogues de **CiteScore** et du **facteur d'impact** selon la méthodologie Scopus et Web of Science.

### Comment ça marche ?
- **CiteScore** : Analyse la période de 1580 à 120 jours avant la date actuelle
- **Facteur d'impact** : Utilise des fenêtres temporelles spécifiques (2+2 ans)
- **Ajustements** : Ne considère que les citations des revues indexées

### Interprétation des résultats :
- **CiteScore > 1.0** - au-dessus de la moyenne du domaine
- **Facteur d'impact > 3.0** - revue à fort impact
- **Grande différence** entre les métriques régulières et ajustées indique des citations provenant de sources non indexées

================================================================================
JAPANESE / ЯПОНСКИЙ / 日本語
================================================================================

## 🎯 プログラムについて

**ジャーナル分析ツール**は、科学雑誌の包括的分析のための専門ツールで、引用、メトリクス、雑誌の発展傾向の深い分析を提供します。

### 🌟 主な機能

- **📊 完全な書誌計量分析** - 出版物、引用、著者の統計
- **🚀 高速メトリクス** - 10+の主要指標を長時間のロードなしで
- **🎯 特別分析モード** - CiteScoreとインパクトファクターの類似指標の計算
- **🌍 多言語インターフェース** - 英語とロシア語
- **📚 内蔵辞書** - 科学用語の学習と進捗追跡
- **🔮 予測分析** - 出版時期の推奨、査読者検索
- **📈 インタラクティブな可視化** - グラフとダッシュボード
- **📥 詳細なレポート** - 20+のデータシートを含むExcelファイル

## 🚀 クイックスタート

### ステップ1：主な分析パラメータ
- **雑誌ISSN**：分析する雑誌のISSNを入力（例：`2411-1414`）
- **分析期間**：年または範囲（例：`2020-2023`）
- **特別分析モード**：CiteScore/インパクトファクターメトリクスの計算を有効化

### ステップ2：分析開始
**「分析開始」**ボタンをクリック - データ量に応じて5〜30分かかります。

### ステップ3：結果の探索
- ダッシュボードタブで結果を表示
- 完全なExcelレポートをダウンロード
- 内蔵辞書を使用してメトリクスを研究

## 📊 主要メトリクスの説明

### 🔬 基本指標

| メトリクス | 説明 | 解釈 |
|-----------|------|------|
| **H指数** | ハーシュ指数 - 生産性と影響力 | 高いほど良い。H指数10は10本の論文がそれぞれ≥10回引用されていることを意味 |
| **総論文数** | 分析された出版物の数 | 雑誌の科学アウトプット量 |
| **総引用数** | 全論文の引用の合計 | 雑誌の全体的な影響力 |
| **論文あたりの平均引用** | 引用数/論文数 | 論文の平均的な影響力 |

### 📈 高速メトリクス（APIなしで計算）

| メトリクス | 説明 | 正常値 |
|-----------|------|--------|
| **参考文献年齢** | 論文内の参考文献の平均年齢 | 5-8年 - 現代雑誌、>10年 - 古典的雑誌 |
| **JSCR** | 雑誌自己引用率 | 10-20% - 正常、>30% - 孤立の可能性 |
| **被引用半減期** | 引用の半分を得るまでの時間 | 2-4年 - 速い科学、>5年 - 基礎科学 |
| **FWCI** | 分野加重引用影響 | 1.0 - 分野平均、>1.2 - 平均以上 |
| **引用速度** | 引用速度（最初の2年間） | 高いほど = 認知が速い |
| **OA影響プレミアム** | オープンアクセスプレミアム | +10-50% - 正常範囲 |
| **エリート指数** | 引用でトップ10%の論文 | >15% - 優れた指標 |
| **著者ジニ係数** | 著者間の出版不平等 | 0.1-0.3 - 均一、>0.6 - 支配的 |
| **DBI** | 主題的多様性 | 0-1、高いほど = より多様化 |

## 🎯 特別分析モード

### これは何？
ScopusとWeb of Scienceの方法論に従って**CiteScore**と**インパクトファクター**の類似指標を計算する特別モード。

### どのように機能する？
- **CiteScore**：現在日から1580-120日前の期間を分析
- **インパクトファクター**：特定の時間ウィンドウを使用（2+2年）
- **調整**：索引付けされた雑誌からの引用のみを考慮

### 結果の解釈：
- **CiteScore > 1.0** - 分野平均以上
- **インパクトファクター > 3.0** - 高インパクト雑誌
- **通常と調整済みメトリクスの大きな差**は、非索引ソースからの引用を示唆

================================================================================
KOREAN / КОРЕЙСКИЙ / 한국어
================================================================================

## 🎯 프로그램 정보

**저널 분석 도구**는 과학 저널의 종합적인 분석을 위한 전문 도구로, 인용, 메트릭 및 저널 발전 추세에 대한 심층 분석을 제공합니다.

### 🌟 주요 기능

- **📊 완전한 서지계량 분석** - 출판물, 인용, 저자의 통계
- **🚀 빠른 메트릭** - 10+개의 주요 지표, 긴 로딩 없이
- **🎯 특수 분석 모드** - CiteScore 및 영향력 지수 유사 지표 계산
- **🌍 다국어 인터페이스** - 영어와 러시아어
- **📚 내장 사전** - 과학 용어 학습 및 진행 상황 추적
- **🔮 예측 분석** - 게시 시기 권장사항, 심사자 검색
- **📈 대화형 시각화** - 그래프 및 대시보드
- **📥 상세 보고서** - 20+개 데이터 시트가 포함된 Excel 파일

## 🚀 빠른 시작

### 1단계: 주요 분석 매개변수
- **저널 ISSN**: 분석할 저널의 ISSN 입력 (예: `2411-1414`)
- **분석 기간**: 연도 또는 범위 (예: `2020-2023`)
- **특수 분석 모드**: CiteScore/영향력 지수 메트릭 계산 활성화

### 2단계: 분석 시작
**"분석 시작"** 버튼 클릭 - 데이터 양에 따라 5~30분 소요됩니다.

### 3단계: 결과 탐색
- 대시보드 탭에서 결과 보기
- 전체 Excel 보고서 다운로드
- 내장 사전을 사용하여 메트릭 연구

## 📊 주요 메트릭 설명

### 🔬 기본 지표

| 메트릭 | 설명 | 해석 |
|--------|------|------|
| **H-지수** | 허쉬 지수 - 생산성 및 영향력 | 높을수록 좋음. H-지수 10은 10편의 논문이 각각 ≥10회 인용됨을 의미 |
| **총 논문 수** | 분석된 출판물 수 | 저널의 과학적 산출량 |
| **총 인용 수** | 모든 논문 인용의 합계 | 저널의 전반적인 영향력 |
| **논문당 평균 인용** | 인용수/논문수 | 논문의 평균적 영향력 |

### 📈 빠른 메트릭 (API 없이 계산)

| 메트릭 | 설명 | 정상값 |
|--------|------|--------|
| **참고문헌 연령** | 논문 내 참고문헌의 평균 연령 | 5-8년 - 현대 저널, >10년 - 고전적 저널 |
| **JSCR** | 저널 자체인용률 | 10-20% - 정상, >30% - 가능한 고립 |
| **인용 반감기** | 인용의 절반을 받는 시간 | 2-4년 - 빠른 과학, >5년 - 기초 과학 |
| **FWCI** | 분야 가중 인용 영향 | 1.0 - 분야 평균, >1.2 - 평균 이상 |
| **인용 속도** | 인용 속도 (첫 2년) | 높을수록 = 인식이 빠름 |
| **OA 영향 프리미엄** | 오픈액세스 프리미엄 | +10-50% - 정상 범위 |
| **엘리트 지수** | 인용 기준 상위 10% 논문 | >15% - 우수한 지표 |
| **저자 지니 계수** | 저자 간 출판 불평등 | 0.1-0.3 - 균일, >0.6 - 지배적 |
| **DBI** | 주제적 다양성 | 0-1, 높을수록 = 더 다양화 |

## 🎯 특수 분석 모드

### 무엇인가요?
Scopus 및 Web of Science 방법론에 따른 **CiteScore** 및 **영향력 지수** 유사 지표를 계산하는 특수 모드.

### 어떻게 작동하나요?
- **CiteScore**: 현재 날짜 기준 1580-120일 전 기간 분석
- **영향력 지수**: 특정 시간 창 사용 (2+2년)
- **조정**: 색인된 저널의 인용만 고려

### 결과 해석:
- **CiteScore > 1.0** - 분야 평균 이상
- **영향력 지수 > 3.0** - 고영향력 저널
- **일반 및 조정 메트릭 간 큰 차이**는 비색인 소스의 인용을 나타냄

================================================================================
SPANISH / ИСПАНСКИЙ / 西班牙语
================================================================================

## 🎯 Acerca del programa

**Instrumento de análisis de revistas** es una herramienta profesional para el análisis integral de revistas científicas que proporciona análisis profundos de citas, métricas y tendencias de desarrollo de revistas.

### 🌟 Características principales

- **📊 Análisis bibliométrico completo** - estadísticas de publicaciones, citas, autores
- **🚀 Métricas rápidas** - 10+ indicadores clave sin carga prolongada
- **🎯 Modo de análisis especial** - cálculo de análogos de CiteScore y factor de impacto
- **🌍 Interfaz multilingüe** - inglés y ruso
- **📚 Diccionario integrado** - aprendizaje de términos científicos con seguimiento de progreso
- **🔮 Análisis predictivo** - recomendaciones de tiempo de publicación, búsqueda de revisores
- **📈 Visualizaciones interactivas** - gráficos y paneles
- **📥 Informes detallados** - archivos Excel con 20+ hojas de datos

## 🚀 Inicio rápido

### Paso 1: Parámetros principales de análisis
- **ISSN de la revista**: Ingrese el ISSN de la revista a analizar (ej.: `2411-1414`)
- **Período de análisis**: Años o rango (ej.: `2020-2023`)
- **Modo de análisis especial**: Habilite para calcular métricas CiteScore/factor de impacto

### Paso 2: Inicio del análisis
Haga clic en el botón **"Iniciar análisis"** - el proceso tomará de 5 a 30 minutos según el volumen de datos.

### Paso 3: Exploración de resultados
- Vea los resultados en las pestañas del panel
- Descargue el informe Excel completo
- Estudie las métricas usando el diccionario integrado

## 📊 Descripción de las métricas principales

### 🔬 Indicadores básicos

| Métrica | Descripción | Interpretación |
|---------|-------------|----------------|
| **H-index** | Índice de Hirsch - productividad e impacto | Más alto = mejor. H-index 10 significa 10 artículos con ≥10 citas cada uno |
| **Total de artículos** | Número de publicaciones analizadas | Volumen de producción científica de la revista |
| **Total de citas** | Suma de todas las citas de artículos | Impacto general de la revista |
| **Promedio de citas por artículo** | Citas/artículos | Influencia promedio de los artículos |

### 📈 Métricas rápidas (cálculo sin API)

| Métrica | Descripción | Valores normales |
|---------|-------------|------------------|
| **Edad de referencias** | Edad promedio de referencias en artículos | 5-8 años - revista moderna, >10 años - clásica |
| **JSCR** | Tasa de autocitación de la revista | 10-20% - normal, >30% - posible aislamiento |
| **Vida media de citación** | Tiempo para recibir la mitad de las citas | 2-4 años - ciencias rápidas, >5 años - fundamentales |
| **FWCI** | Impacto de citación ponderado por campo | 1.0 - promedio del campo, >1.2 - por encima del promedio |
| **Velocidad de citación** | Velocidad de citación (primeros 2 años) | Más alta = reconocimiento más rápido |
| **Prima de impacto OA** | Prima de acceso abierto | +10-50% - rango normal |
| **Índice de élite** | Artículos en el top 10% por citas | >15% - indicador excelente |
| **Gini de autores** | Desigualdad de publicaciones entre autores | 0.1-0.3 - uniforme, >0.6 - dominancia |
| **DBI** | Diversidad temática | 0-1, más alto = más diversificado |

## 🎯 Modo de análisis especial

### ¿Qué es?
Modo especial para calcular análogos de **CiteScore** y **factor de impacto** según la metodología de Scopus y Web of Science.

### ¿Cómo funciona?
- **CiteScore**: Analiza el período de 1580 a 120 días antes de la fecha actual
- **Factor de impacto**: Usa ventanas de tiempo específicas (2+2 años)
- **Ajustes**: Considera solo citas de revistas indexadas

### Interpretación de resultados:
- **CiteScore > 1.0** - por encima del promedio del campo
- **Factor de impacto > 3.0** - revista de alto impacto
- **Gran diferencia** entre métricas regulares y ajustadas indica citas de fuentes no indexadas

================================================================================
ARABIC / АРАБСКИЙ / 阿拉伯语
================================================================================

## 🎯 حول البرنامج

**أداة تحليل المجلة** هي أداة احترافية للتحليل الشامل للمجلات العلمية التي توفر تحليلات متعمقة للاقتباسات والمقاييس واتجاهات تطور المجلة.

### 🌟 الميزات الرئيسية

- **📊 تحليل ببليومتري كامل** - إحصائيات المنشورات، الاقتباسات، المؤلفين
- **🚀 مقاييس سريعة** - 10+ مؤشرات رئيسية بدون تحميل طويل
- **🎯 وضع التحليل الخاص** - حساب نظائر CiteScore وعامل التأثير
- **🌍 واجهة متعددة اللغات** - الإنجليزية والروسية
- **📚 قاموس مدمج** - تعلم المصطلحات العلمية مع تتبع التقدم
- **🔮 تحليل تنبؤي** - توصيات بتوقيت النشر، البحث عن المراجعين
- **📈 تصورات تفاعلية** - رسوم بيانية ولوحات تحكم
- **📥 تقارير مفصلة** - ملفات إكسل تحتوي على 20+ ورقة بيانات

## 🚀 بدء سريع

### الخطوة 1: معلمات التحليل الرئيسية
- **رقم ISSN للمجلة**: أدخل ISSN للمجلة المراد تحليلها (مثال: `2411-1414`)
- **فترة التحليل**: سنوات أو نطاق (مثال: `2020-2023`)
- **وضع التحليل الخاص**: قم بتمكينه لحساب مقاييس CiteScore/عامل التأثير

### الخطوة 2: بدء التحليل
انقر على زر **"بدء التحليل"** - تستغرق العملية من 5 إلى 30 دقيقة حسب حجم البيانات.

### الخطوة 3: استكشاف النتائج
- عرض النتائج في علامات تبويب لوحة التحكم
- قم بتنزيل تقرير إكسل الكامل
- ادرس المقاييس باستخدام القاموس المدمج

## 📊 وصف المقاييس الرئيسية

### 🔬 المؤشرات الأساسية

| المقياس | الوصف | التفسير |
|---------|-------|---------|
| **مؤشر H** | مؤشر هيرش - الإنتاجية والتأثير | أعلى = أفضل. مؤشر H بقيمة 10 يعني 10 مقالات مع ≥10 اقتباسات لكل منها |
| **إجمالي المقالات** | عدد المنشورات التي تم تحليلها | حجم المخرجات العلمية للمجلة |
| **إجمالي الاقتباسات** | مجموع جميع اقتباسات المقالات | التأثير العام للمجلة |
| **متوسط الاقتباسات لكل مقال** | اقتباسات/مقالات | متوسط تأثير المقالات |

### 📈 المقاييس السريعة (حساب بدون API)

| المقياس | الوصف | القيم الطبيعية |
|---------|-------|---------------|
| **عمر المراجع** | متوسط عمر المراجع في المقالات | 5-8 سنوات - مجلة حديثة، >10 سنوات - كلاسيكية |
| **JSCR** | معدل الاقتباس الذاتي للمجلة | 10-20% - طبيعي، >30% - عزلة محتملة |
| **نصف عمر الاقتباس** | الوقت اللازم للحصول على نصف الاقتباسات | 2-4 سنوات - علوم سريعة، >5 سنوات - أساسية |
| **FWCI** | تأثير الاقتباس المرجح حسب المجال | 1.0 - متوسط المجال، >1.2 - أعلى من المتوسط |
| **سرعة الاقتباس** | سرعة الاقتباس (أول سنتين) | أعلى = اعتراف أسرع |
| **علاوة تأثير OA** | علاوة الوصول المفتوح | +10-50% - نطاق طبيعي |
| **مؤشر النخبة** | مقالات في أعلى 10% حسب الاقتباسات | >15% - مؤشر ممتاز |
| **جيني المؤلف** | عدم المساواة في النشر بين المؤلفين | 0.1-0.3 - موحد، >0.6 - هيمنة |
| **DBI** | التنوع الموضوعي | 0-1، أعلى = أكثر تنوعًا |

## 🎯 وضع التحليل الخاص

### ما هذا؟
وضع خاص لحساب نظائر **CiteScore** و**عامل التأثير** وفقًا منهجية Scopus وWeb of Science.

### كيف يعمل؟
- **CiteScore**: يحلل الفترة من 1580 إلى 120 يومًا قبل التاريخ الحالي
- **عامل التأثير**: يستخدم نوافذ زمنية محددة (2+2 سنة)
- **التعديلات**: يأخذ في الاعتبار فقط الاقتباسات من المجلات المفهرسة

### تفسير النتائج:
- **CiteScore > 1.0** - أعلى من متوسط المجال
- **عامل التأثير > 3.0** - مجلة عالية التأثير
- **الفرق الكبير** بين المقاييس العادية والمعدلة يشير إلى اقتباسات من مصادر غير مفهرسة

================================================================================
END OF DOCUMENT / КОНЕЦ ДОКУМЕНТА / 文档结束
================================================================================

**Journal Analysis Tool** provides professional toolkit for editors, bibliometricians and researchers, allowing comprehensive analysis of scientific journals using modern methods and metrics.

**Инструмент анализа журналов** предоставляет профессиональный инструментарий для редакторов, библиометриков и исследователей, позволяющий проводить комплексный анализ научных журналов с использованием современных методов и метрик.

**期刊分析工具**为编辑、文献计量学家和研究人员提供专业工具包，允许使用现代方法和指标对科学期刊进行全面分析。

**Outil d'analyse de revues** fournit une boîte à outils professionnelle pour les éditeurs, les bibliométriciens et les chercheurs, permettant une analyse complète des revues scientifiques en utilisant des méthodes et des métriques modernes.

**ジャーナル分析ツール**は、編集者、書誌計量学者、研究者向けの専門ツールキットを提供し、現代的な方法とメトリクスを使用した科学雑誌の包括的分析を可能にします。

**저널 분석 도구**는 편집자, 서지계량학자 및 연구자를 위한 전문 도구 키트를 제공하여 현대적 방법과 메트릭을 사용한 과학 저널의 종합적 분석을 가능하게 합니다.

**Instrumento de análisis de revistas** proporciona un conjunto de herramientas profesional para editores, bibliometristas e investigadores, permitiendo un análisis integral de revistas científicas utilizando métodos y métricas modernas.

**يوفر أداة تحليل المجلة** مجموعة أدوات احترافية للمحررين وعلماء الببليومتريا والباحثين، مما يسمح بإجراء تحليل شامل للمجلات العلمية باستخدام الأساليب والمقاييس الحديثة.
