# Journal Analysis Tool - Complete User Guide

## 🎯 About the Program

**Journal Analysis Tool** is a professional tool for comprehensive analysis of scientific journals, providing in-depth citation analytics, metrics, and journal development trends.

### 🌟 Key Features

- **📊 Complete Bibliometric Analysis** - publication statistics, citations, authors
- **🚀 Fast Metrics** - 10+ key indicators without long loading times
- **🎯 Special Analysis Mode** - calculation of CiteScore and Impact Factor analogs
- **🌍 Bilingual Interface** - Russian and English languages
- **📚 Built-in Dictionary** - learn scientific terms with progress tracking
- **🔮 Predictive Analytics** - publication timing recommendations, reviewer search
- **📈 Interactive Visualizations** - charts and dashboards
- **📥 Detailed Reports** - Excel files with 20+ data sheets

## 🚀 Quick Start

### Step 1: Basic Analysis Parameters
- **Journal ISSN**: Enter the ISSN of the analyzed journal (e.g., `2411-1414`)
- **Analysis Period**: Years or range (e.g., `2020-2023`)
- **Special Analysis Mode**: Enable for CiteScore/Impact Factor metric calculation

### Step 2: Start Analysis
Click the **"Start Analysis"** button - the process takes from 5 to 30 minutes depending on data volume.

### Step 3: Explore Results
- View results in dashboard tabs
- Download full Excel report
- Study metrics using the built-in dictionary

## 📊 Main Metrics Description

### 🔬 Basic Indicators

| Metric | Description | Interpretation |
|---------|----------|---------------|
| **H-index** | Hirsch index - productivity and impact | Higher = better. H-index 10 means 10 articles with ≥10 citations each |
| **Total Articles** | Number of analyzed publications | Journal's scientific output volume |
| **Total Citations** | Sum of citations for all articles | Journal's overall influence |
| **Average Citations per Article** | Citations/articles | Average influence of articles |

### 📈 Fast Metrics (calculation without API)

| Metric | Description | Normal Values |
|---------|----------|---------------------|
| **Reference Age** | Average age of references in articles | 5-8 years - modern journal, >10 years - classical |
| **JSCR** | Journal Self-Citation Rate | 10-20% - normal, >30% - possible isolation |
| **Cited Half-Life** | Time to receive half of citations | 2-4 years - fast sciences, >5 years - fundamental |
| **FWCI** | Field-Weighted Citation Impact | 1.0 - field average, >1.2 - above average |
| **Citation Velocity** | Citation speed (first 2 years) | Higher = faster recognition |
| **OA Impact Premium** | Open Access premium | +10-50% - typical range |
| **Elite Index** | Articles in top-10% by citations | >15% - excellent indicator |
| **Author Gini** | Publication inequality among authors | 0.1-0.3 - even, >0.6 - dominance |
| **DBI** | Thematic diversity | 0-1, higher = more diversified |

## 🎯 Special Analysis Mode

### What is it?
Special mode for calculating **CiteScore** and **Impact Factor** analogs using Scopus and Web of Science methodologies.

### How it works?
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
- **Russian** - complete interface and terminology translation

### How to Change Language:
1. Open sidebar (left panel)
2. In "Language" section select desired language
3. Interface switches instantly

## 📚 Terminology Dictionary

### Learning Functionality:
- **Term Search** - dropdown list of all metrics
- **Detailed Explanations** - definition, calculation, interpretation, examples
- **Progress Tracking** - statistics of studied terms
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
- **Identify months** with highest citation activity
- **Publication timing recommendations** considering time to first citation
- **Visualization** of monthly citation distribution

### Potential Reviewer Search:
- **Automatic search** for authors who cite the journal but never published in it
- **Conflict of interest exclusion** - authors without journal connections
- **Ranking** by citation count

### Keyword Analysis:
- **Content words** - significant terms in titles
- **Compound words** - hyphenated compound terms
- **Scientific stopwords** - frequently used scientific terms
- **Comparison** of analyzed and citing articles

## 💡 Usage Tips

### For Best Results:
1. **Use exact ISSN** - verify identifier correctness
2. **Start with short periods** - 2-3 years for testing
3. **Enable Special Analysis** for Scopus/WoS journals
4. **Study dictionary** before deep metric analysis
5. **Download Excel report** for detailed study

### Data Interpretation:
- **Compare metrics** with journal's field of knowledge
- **Consider journal age** - young journals have different patterns
- **Analyze trends** - dynamics more important than absolute values
- **Use multiple metrics** for comprehensive assessment

## ⚠️ Important Notes

### Data Limitations:
- Dependency on Crossref and OpenAlex data quality
- Processing time depends on article and citation count
- Some metrics require minimum data volume

### Recommendations:
- For large journals, analyze sample periods
- Check data completeness via Crossref before analysis
- Use stable internet connection
- Save Excel reports for subsequent comparison

## 🆘 Support

### If Problems Occur:
1. **Check internet connection**
2. **Verify ISSN correctness**
3. **Try shortening analysis period**
4. **Refresh browser page**

### For Complex Cases:
- Use Special Analysis mode for data verification
- Analyze journals with known metrics for calibration
- Refer to built-in dictionary for metric understanding

---

**Journal Analysis Tool** provides professional toolkit for editors, bibliometricians, and researchers, enabling comprehensive analysis of scientific journals using modern methods and metrics.

=============================================================================
=============================================================================

# Journal Analysis Tool - Полное руководство пользователя

## 🎯 О программе

**Journal Analysis Tool** - это профессиональный инструмент для комплексного анализа научных журналов, который предоставляет глубокую аналитику цитирования, метрик и тенденций развития журналов.

### 🌟 Основные возможности

- **📊 Полный библиометрический анализ** - статистика публикаций, цитирований, авторов
- **🚀 Быстрые метрики** - 10+ ключевых показателей без долгой загрузки
- **🎯 Special Analysis Mode** - расчет аналогов CiteScore и Impact Factor
- **🌍 Двуязычный интерфейс** - русский и английский языки
- **📚 Встроенный словарь** - обучение научным терминам с отслеживанием прогресса
- **🔮 Прогнозная аналитика** - рекомендации по времени публикации, поиск рецензентов
- **📈 Интерактивные визуализации** - графики и дашборды
- **📥 Детальные отчеты** - Excel файлы с 20+ листами данных

## 🚀 Быстрый старт

### Шаг 1: Основные параметры анализа
- **ISSN журнала**: Введите ISSN анализируемого журнала (например: `2411-1414`)
- **Период анализа**: Годы или диапазон (например: `2020-2023`)
- **Special Analysis Mode**: Включите для расчета метрик CiteScore/Impact Factor

### Шаг 2: Запуск анализа
Нажмите кнопку **"Start Analysis"** - процесс займет от 5 до 30 минут в зависимости от объема данных.

### Шаг 3: Изучение результатов
- Просматривайте результаты во вкладках дашборда
- Скачайте полный Excel отчет
- Изучайте метрики с помощью встроенного словаря

## 📊 Описание основных метрик

### 🔬 Базовые показатели

| Метрика | Описание | Интерпретация |
|---------|----------|---------------|
| **H-index** | Индекс Хирша - продуктивность и влияние | Выше = лучше. H-index 10 означает 10 статей с ≥10 цитирований каждая |
| **Общее число статей** | Количество проанализированных публикаций | Объем научной output журнала |
| **Общее число цитирований** | Суммарные цитирования всех статей | Общее влияние журнала |
| **Средние цитирования на статью** | Цитирования/статьи | Средняя влиятельность статей |

### 📈 Быстрые метрики (расчет без API)

| Метрика | Описание | Нормальные значения |
|---------|----------|---------------------|
| **Reference Age** | Средний возраст ссылок в статьях | 5-8 лет - современный журнал, >10 лет - классический |
| **JSCR** | Journal Self-Citation Rate | 10-20% - нормально, >30% - возможная изоляция |
| **Cited Half-Life** | Время получения половины цитирований | 2-4 года - быстрые науки, >5 лет - фундаментальные |
| **FWCI** | Field-Weighted Citation Impact | 1.0 - среднее поле, >1.2 - выше среднего |
| **Citation Velocity** | Скорость цитирования (первые 2 года) | Выше = быстрее признание |
| **OA Impact Premium** | Премия открытого доступа | +10-50% - обычный диапазон |
| **Elite Index** | Статьи в топ-10% по цитированиям | >15% - отличный показатель |
| **Author Gini** | Неравенство публикаций среди авторов | 0.1-0.3 - равномерно, >0.6 - доминирование |
| **DBI** | Тематическое разнообразие | 0-1, выше = более диверсифицировано |

## 🎯 Режим Special Analysis

### Что это такое?
Специальный режим для расчета аналогов **CiteScore** и **Impact Factor** по методологии Scopus и Web of Science.

### Как работает?
- **CiteScore**: Анализирует период 1580-120 дней от текущей даты
- **Impact Factor**: Использует специфичные временные окна (2+2 года)
- **Корректировки**: Учитывает только цитирования из индексируемых журналов

### Интерпретация результатов:
- **CiteScore > 1.0** - выше среднего по области
- **Impact Factor > 3.0** - высокоимпактный журнал
- **Большая разница** между обычными и скорректированными метриками указывает на цитирования из неиндексируемых источников

## 📋 Структура Excel отчета

### Основные листы:

1. **Analyzed_Articles** - детали проанализированных статей журнала
2. **Citing_Works** - информация о цитирующих работах
3. **Work_Overlaps** - пересечения авторов и аффилиаций
4. **First_Citations** - время до первого цитирования (исключая редакторские заметки)
5. **Statistics** - объединенная статистика по всем показателям

### Аналитические листы:

6. **Citing_Stats** - метрики цитирования (H-index, накопление цитирований)
7. **Citations_by_Year** - динамика цитирований по годам
8. **Citation_Accumulation_Curves** - кривые накопления цитирований
9. **Citation_Network** - сеть цитирований между годами

### Листы по участникам:

10. **All_Authors_Analyzed** - авторы журнала (с нормализацией имен)
11. **All_Authors_Citing** - авторы цитирующих работ
12. **All_Affiliations_Analyzed/Citing** - аффилиации
13. **All_Countries_Analyzed/Citing** - географическое распределение
14. **All_Journals_Citing** - журналы-цитенты с метриками IF/CS

### Специальные листы:

15. **Fast_Metrics** - все быстрые метрики в одной таблице
16. **Top_Concepts** - топ-10 тематических концепций
17. **Title_Keywords** - анализ ключевых слов в названиях
18. **Citation_Seasonality** - сезонность цитирований
19. **Optimal_Publication_Months** - рекомендации по времени публикации
20. **Potential_Reviewers** - потенциальные рецензенты
21. **Special_Analysis_Metrics** - метрики Special Analysis режима

## 🌍 Мультиязычность

### Доступные языки:
- **Английский** - язык по умолчанию
- **Русский** - полный перевод интерфейса и терминов

### Как сменить язык:
1. Откройте сайдбар (левая панель)
2. В разделе "Language" выберите нужный язык
3. Интерфейс мгновенно переключится

## 📚 Словарь терминов

### Функциональность обучения:
- **Поиск терминов** - выпадающий список всех метрик
- **Детальные объяснения** - определение, расчет, интерпретация, примеры
- **Отслеживание прогресса** - статистика изученных терминов
- **Категоризация** - 7 категорий метрик для системного изучения

### Категории терминов:
- 🔵 **Citations** - метрики цитирования
- 🟢 **References** - анализ ссылок
- 🟠 **Authors** - авторская статистика
- 🟣 **Themes** - тематический анализ
- 🔴 **Journal** - журнальные идентификаторы
- ⚫ **Technical** - технические аспекты
- 🟤 **Databases** - базы данных

## 🔮 Прогнозная аналитика

### Анализ сезонности цитирований:
- **Выявление месяцев** с наибольшей цитируемостью
- **Рекомендации по времени публикации** с учетом времени до первого цитирования
- **Визуализация** помесячного распределения цитирований

### Поиск потенциальных рецензентов:
- **Автоматический поиск** авторов, которые цитируют журнал, но никогда в нем не публиковались
- **Исключение конфликта интересов** - авторы без связей с журналом
- **Ранжирование** по количеству цитирований

### Анализ ключевых слов:
- **Content words** - значимые термины в названиях
- **Compound words** - составные термины через дефис
- **Scientific stopwords** - часто используемые научные термины
- **Сравнение** анализируемых и цитирующих статей

## 💡 Советы по использованию

### Для лучших результатов:
1. **Используйте точный ISSN** - проверьте корректность идентификатора
2. **Начинайте с коротких периодов** - 2-3 года для тестирования
3. **Включите Special Analysis** для журналов из Scopus/WoS
4. **Изучайте словарь** перед глубоким анализом метрик
5. **Скачивайте Excel отчет** для детального изучения

### Интерпретация данных:
- **Сравнивайте метрики** с областью знаний журнала
- **Учитывайте возраст журнала** - молодые журналы имеют другие паттерны
- **Анализируйте тренды** - динамика важнее абсолютных значений
- **Используйте несколько метрик** для комплексной оценки

## ⚠️ Важные примечания

### Ограничения данных:
- Зависимость от качества данных Crossref и OpenAlex
- Время обработки зависит от количества статей и цитирований
- Некоторые метрики требуют минимального объема данных

### Рекомендации:
- Для больших журналов анализируйте выборочные периоды
- Проверяйте полноту данных через Crossref перед анализом
- Используйте стабильное интернет-соединение
- Сохраняйте Excel отчеты для последующего сравнения

## 🆘 Поддержка

### При возникновении проблем:
1. **Проверьте интернет-соединение**
2. **Убедитесь в корректности ISSN**
3. **Попробуйте сократить период анализа**
4. **Обновите страницу браузера**

### Для сложных случаев:
- Используйте режим Special Analysis для проверки данных
- Анализируйте журналы с известными метриками для калибровки
- Обращайтесь к встроенному словарю для понимания метрик

---

**Journal Analysis Tool** предоставляет профессиональный инструментарий для редакторов, библиометриков и исследователей, позволяющий проводить комплексный анализ научных журналов с использованием современных методов и метрик.

=============================================================================
=============================================================================
# Journal Analysis Tool – Vollständige Benutzeranleitung

## 🎯 Über das Programm

**Journal Analysis Tool** ist ein professionelles Werkzeug für die umfassende Analyse wissenschaftlicher Zeitschriften, das tiefgehende Analysen von Zitierungen, Metriken und Entwicklungstrends von Zeitschriften bereitstellt.

### 🌟 Hauptfunktionen

- **📊 Vollständige bibliometrische Analyse** - Publikationsstatistiken, Zitationen, Autoren
- **🚀 Schnelle Metriken** - 10+ Schlüsselindikatoren ohne lange Ladezeiten
- **🎯 Spezial-Analysemodus** - Berechnung von CiteScore und Impact Factor Analoga
- **🌍 Zweisprachige Oberfläche** - Deutsch und Englisch Sprachen
- **📚 Integriertes Wörterbuch** - Wissenschaftliche Begriffe lernen mit Fortschrittsverfolgung
- **🔮 Prognostische Analytik** - Veröffentlichungszeitpunkt-Empfehlungen, Gutachtersuche
- **📈 Interaktive Visualisierungen** - Diagramme und Dashboards
- **📥 Detaillierte Berichte** - Excel-Dateien mit 20+ Datenblättern

## 🚀 Schnellstart

### Schritt 1: Grundlegende Analyseparameter
- **Zeitschriften-ISSN**: Geben Sie die ISSN der analysierten Zeitschrift ein (zum Beispiel: `2411-1414`)
- **Analysezeitraum**: Jahre oder Bereich (zum Beispiel: `2020-2023`)
- **Spezial-Analysemodus**: Aktivieren für CiteScore/Impact Factor Metrikberechnung

### Schritt 2: Analyse starten
Klicken Sie auf die **"Analyse starten"** Schaltfläche - der Prozess dauert 5 bis 30 Minuten je nach Datenvolumen.

### Schritt 3: Ergebnisse erkunden
- Ergebnisse in Dashboard-Registerkarten ansehen
- Vollständigen Excel-Bericht herunterladen
- Metriken mit dem integrierten Wörterbuch studieren

## 📊 Beschreibung der Hauptmetriken

### 🔬 Grundlegende Indikatoren

| Metrik | Beschreibung | Interpretation |
|---------|----------|---------------|
| **H-Index** | Hirsch-Index - Produktivität und Einfluss | Höher = besser. H-Index 10 bedeutet 10 Artikel mit ≥10 Zitierungen jeweils |
| **Gesamtanzahl Artikel** | Anzahl analysierter Publikationen | Wissenschaftliches Output-Volumen der Zeitschrift |
| **Gesamtzahl Zitierungen** | Summe der Zitierungen aller Artikel | Gesamteinfluss der Zeitschrift |
| **Durchschnittliche Zitierungen pro Artikel** | Zitierungen/Artikel | Durchschnittlicher Einfluss der Artikel |

### 📈 Schnelle Metriken (Berechnung ohne API)

| Metrik | Beschreibung | Normale Werte |
|---------|----------|---------------------|
| **Referenzalter** | Durchschnittsalter der Referenzen in Artikeln | 5-8 Jahre - moderne Zeitschrift, >10 Jahre - klassisch |
| **JSCR** | Zeitschriften-Selbstzitierrate | 10-20% - normal, >30% - mögliche Isolation |
| **Zitierte Halbwertszeit** | Zeit zur Erhaltung der Hälfte der Zitierungen | 2-4 Jahre - schnelle Wissenschaften, >5 Jahre - grundlegend |
| **FWCI** | Feldgewichteter Zitierimpact | 1,0 - Felddurchschnitt, >1,2 - überdurchschnittlich |
| **Zitiergeschwindigkeit** | Zitiergeschwindigkeit (erste 2 Jahre) | Höher = schnellere Anerkennung |
| **OA-Impact-Prämie** | Open-Access-Prämie | +10-50% - typischer Bereich |
| **Elite-Index** | Artikel in Top-10% nach Zitierungen | >15% - ausgezeichneter Indikator |
| **Autor-Gini** | Publikationsungleichheit unter Autoren | 0,1-0,3 - gleichmäßig, >0,6 - Dominanz |
| **DBI** | Thematische Vielfalt | 0-1, höher = diversifizierter |

## 🎯 Spezial-Analysemodus

### Was ist das?
Spezialmodus zur Berechnung von **CiteScore** und **Impact Factor** Analoga nach Scopus und Web of Science Methodologien.

### Wie funktioniert es?
- **CiteScore**: Analysiert Zeitraum 1580-120 Tage ab aktuellem Datum
- **Impact Factor**: Verwendet spezifische Zeitfenster (2+2 Jahre)
- **Anpassungen**: Berücksichtigt nur Zitierungen aus indizierten Zeitschriften

### Ergebnisinterpretation:
- **CiteScore > 1,0** - über Felddurchschnitt
- **Impact Factor > 3,0** - hochimpaktvolle Zeitschrift
- **Großer Unterschied** zwischen regulären und angepassten Metriken weist auf Zitierungen aus nicht-indizierten Quellen hin

## 📋 Excel-Berichtsstruktur

### Hauptblätter:

1. **Analyzed_Articles** - Details analysierter Zeitschriftenartikel
2. **Citing_Works** - Informationen über zitierende Werke
3. **Work_Overlaps** - Autor- und Zugehörigkeitsüberschneidungen
4. **First_Citations** - Zeit bis zur ersten Zitierung (ohne redaktionelle Notizen)
5. **Statistics** - Kombinierte Statistiken für alle Indikatoren

### Analytische Blätter:

6. **Citing_Stats** - Zitierungsmetriken (H-Index, Zitierakkumulation)
7. **Citations_by_Year** - Zitierungsdynamik nach Jahren
8. **Citation_Accumulation_Curves** - Zitierakkumulationskurven
9. **Citation_Network** - Zitiernetzwerk zwischen Jahren

### Teilnehmerblätter:

10. **All_Authors_Analyzed** - Zeitschriftenautoren (mit Namensnormalisierung)
11. **All_Authors_Citing** - Autoren zitierender Werke
12. **All_Affiliations_Analyzed/Citing** - Zugehörigkeiten
13. **All_Countries_Analyzed/Citing** - Geografische Verteilung
14. **All_Journals_Citing** - Zitierende Zeitschriften mit IF/CS Metriken

### Spezialblätter:

15. **Fast_Metrics** - Alle schnellen Metriken in einer Tabelle
16. **Top_Concepts** - Top-10 thematische Konzepte
17. **Title_Keywords** - Schlüsselwortanalyse in Titeln
18. **Citation_Seasonality** - Zitiersaisonalität
19. **Optimal_Publication_Months** - Empfehlungen zum Veröffentlichungszeitpunkt
20. **Potential_Reviewers** - Potenzielle Gutachter
21. **Special_Analysis_Metrics** - Metriken des Spezial-Analysemodus

## 🌍 Mehrsprachige Unterstützung

### Verfügbare Sprachen:
- **Englisch** - Standardsprache
- **Deutsch** - Vollständige Übersetzung der Oberfläche und Terminologie

### Sprachwechsel:
1. Seitenleiste öffnen (linke Leiste)
2. Im Abschnitt "Sprache" gewünschte Sprache auswählen
3. Oberfläche wechselt sofort

## 📚 Terminologie-Wörterbuch

### Lernfunktionalität:
- **Begriffssuche** - Dropdown-Liste aller Metriken
- **Detaillierte Erklärungen** - Definition, Berechnung, Interpretation, Beispiele
- **Fortschrittsverfolgung** - Statistik studierter Begriffe
- **Kategorisierung** - 7 Metrikkategorien für systematisches Lernen

### Begriffskategorien:
- 🔵 **Zitationen** - Zitierungsmetriken
- 🟢 **Referenzen** - Referenzanalyse
- 🟠 **Autoren** - Autorenstatistiken
- 🟣 **Themen** - Thematische Analyse
- 🔴 **Zeitschrift** - Zeitschriftenidentifikatoren
- ⚫ **Technisch** - Technische Aspekte
- 🟤 **Datenbanken** - Datenbanken

## 🔮 Prognostische Analytik

### Zitiersaisonalitätsanalyse:
- **Monate identifizieren** mit höchster Zitieraktivität
- **Veröffentlichungszeitpunkt-Empfehlungen** unter Berücksichtigung der Zeit bis zur ersten Zitierung
- **Visualisierung** der monatlichen Zitierverteilung

### Potenzielle Gutachersuche:
- **Automatische Suche** nach Autoren, die die Zeitschrift zitieren aber nie darin publiziert haben
- **Interessenkonflikt-Ausschluss** - Autoren ohne Zeitschriftenverbindungen
- **Rangfolge** nach Zitieranzahl

### Schlüsselwortanalyse:
- **Inhaltswörter** - bedeutende Begriffe in Titeln
- **Zusammengesetzte Wörter** - zusammengesetzte Begriffe mit Bindestrich
- **Wissenschaftliche Stoppwörter** - häufig verwendete wissenschaftliche Begriffe
- **Vergleich** analysierter und zitierender Artikel

## 💡 Verwendungstipps

### Für beste Ergebnisse:
1. **Exakte ISSN verwenden** - Korrektheit des Identifikators prüfen
2. **Mit kurzen Zeiträumen beginnen** - 2-3 Jahre zum Testen
3. **Spezial-Analyse aktivieren** für Scopus/WoS Zeitschriften
4. **Wörterbuch studieren** vor tiefer Metrikanalyse
5. **Excel-Bericht herunterladen** für detaillierte Studie

### Dateninterpretation:
- **Metriken vergleichen** mit dem Wissensgebiet der Zeitschrift
- **Zeitschriftenalter berücksichtigen** - junge Zeitschriften haben andere Muster
- **Trends analysieren** - Dynamik wichtiger als absolute Werte
- **Mehrere Metriken verwenden** für umfassende Bewertung

## ⚠️ Wichtige Hinweise

### Dateneinschränkungen:
- Abhängigkeit von Crossref und OpenAlex Datenqualität
- Verarbeitungszeit hängt von Artikel- und Zitieranzahl ab
- Einige Metriken erfordern Mindestdatenvolumen

### Empfehlungen:
- Für große Zeitschriften Stichprobenzeiträume analysieren
- Datenvollständigkeit über Crossref vor Analyse prüfen
- Stabile Internetverbindung verwenden
- Excel-Berichte für nachfolgende Vergleiche speichern

## 🆘 Unterstützung

### Bei Problemen:
1. **Internetverbindung prüfen**
2. **Korrektheit der ISSN sicherstellen**
3. **Analysezeitraum verkürzen versuchen**
4. **Browserseite aktualisieren**

### Für komplexe Fälle:
- Spezial-Analysemodus zur Datenüberprüfung verwenden
- Zeitschriften mit bekannten Metriken zur Kalibrierung analysieren
- Auf integriertes Wörterbuch für Metrikverständnis zurückgreifen

---

**Journal Analysis Tool** bietet professionelle Werkzeuge für Redakteure, Bibliometriker und Forscher, ermöglicht umfassende Analyse wissenschaftlicher Zeitschriften mit modernen Methoden und Metriken.

=============================================================================
=============================================================================
# Journal Analysis Tool - Guía Completa del Usuario

## 🎯 Acerca del Programa

**Journal Analysis Tool** es una herramienta profesional para el análisis integral de revistas científicas, que proporciona análisis profundos de citas, métricas y tendencias de desarrollo de revistas.

### 🌟 Características Principales

- **📊 Análisis Bibliométrico Completo** - estadísticas de publicaciones, citas, autores
- **🚀 Métricas Rápidas** - 10+ indicadores clave sin largos tiempos de carga
- **🎯 Modo de Análisis Especial** - cálculo de análogos de CiteScore e Impact Factor
- **🌍 Interfaz Bilingüe** - idiomas español e inglés
- **📚 Diccionario Integrado** - aprendizaje de términos científicos con seguimiento de progreso
- **🔮 Analítica Predictiva** - recomendaciones de tiempo de publicación, búsqueda de revisores
- **📈 Visualizaciones Interactivas** - gráficos y paneles de control
- **📥 Informes Detallados** - archivos Excel con 20+ hojas de datos

## 🚀 Inicio Rápido

### Paso 1: Parámetros Básicos de Análisis
- **ISSN de la Revista**: Ingrese el ISSN de la revista analizada (por ejemplo: `2411-1414`)
- **Período de Análisis**: Años o rango (por ejemplo: `2020-2023`)
- **Modo de Análisis Especial**: Active para cálculo de métricas CiteScore/Impact Factor

### Paso 2: Iniciar Análisis
Presione el botón **"Iniciar Análisis"** - el proceso tomará de 5 a 30 minutos dependiendo del volumen de datos.

### Paso 3: Explorar Resultados
- Vea los resultados en las pestañas del panel de control
- Descargue el informe completo de Excel
- Estudie las métricas usando el diccionario integrado

## 📊 Descripción de las Métricas Principales

### 🔬 Indicadores Básicos

| Métrica | Descripción | Interpretación |
|---------|----------|---------------|
| **H-index** | Índice H - productividad e impacto | Mayor = mejor. H-index 10 significa 10 artículos con ≥10 citas cada uno |
| **Número Total de Artículos** | Cantidad de publicaciones analizadas | Volumen de producción científica de la revista |
| **Número Total de Citas** | Suma de citas de todos los artículos | Influencia general de la revista |
| **Citas Promedio por Artículo** | Citas/artículos | Influencia promedio de los artículos |

### 📈 Métricas Rápidas (cálculo sin API)

| Métrica | Descripción | Valores Normales |
|---------|----------|---------------------|
| **Edad de Referencias** | Edad promedio de referencias en artículos | 5-8 años - revista moderna, >10 años - clásica |
| **JSCR** | Tasa de Autocitas de la Revista | 10-20% - normal, >30% - posible aislamiento |
| **Vida Media de Citación** | Tiempo para recibir la mitad de las citas | 2-4 años - ciencias rápidas, >5 años - fundamentales |
| **FWCI** | Impacto de Citación Ponderado por Campo | 1.0 - promedio del campo, >1.2 - por encima del promedio |
| **Velocidad de Citación** | Velocidad de citación (primeros 2 años) | Mayor = reconocimiento más rápido |
| **Prima de Impacto OA** | Prima de acceso abierto | +10-50% - rango típico |
| **Índice de Élite** | Artículos en top-10% por citas | >15% - indicador excelente |
| **Gini de Autor** | Desigualdad de publicaciones entre autores | 0.1-0.3 - uniforme, >0.6 - dominancia |
| **DBI** | Diversidad Temática | 0-1, mayor = más diversificado |

## 🎯 Modo de Análisis Especial

### ¿Qué es?
Modo especial para cálculo de análogos de **CiteScore** e **Impact Factor** según metodologías Scopus y Web of Science.

### ¿Cómo funciona?
- **CiteScore**: Analiza período 1580-120 días desde fecha actual
- **Impact Factor**: Usa ventanas de tiempo específicas (2+2 años)
- **Ajustes**: Considera solo citas de revistas indexadas

### Interpretación de Resultados:
- **CiteScore > 1.0** - por encima del promedio del campo
- **Impact Factor > 3.0** - revista de alto impacto
- **Gran diferencia** entre métricas regulares y ajustadas indica citas de fuentes no indexadas

## 📋 Estructura del Informe Excel

### Hojas Principales:

1. **Analyzed_Articles** - detalles de artículos de revista analizados
2. **Citing_Works** - información sobre obras citantes
3. **Work_Overlaps** - superposiciones de autores y afiliaciones
4. **First_Citations** - tiempo hasta primera cita (excluyendo notas editoriales)
5. **Statistics** - estadísticas combinadas para todos los indicadores

### Hojas Analíticas:

6. **Citing_Stats** - métricas de citación (H-index, acumulación de citas)
7. **Citations_by_Year** - dinámica de citas por años
8. **Citation_Accumulation_Curves** - curvas de acumulación de citas
9. **Citation_Network** - red de citas entre años

### Hojas de Participantes:

10. **All_Authors_Analyzed** - autores de la revista (con normalización de nombres)
11. **All_Authors_Citing** - autores de obras citantes
12. **All_Affiliations_Analyzed/Citing** - afiliaciones
13. **All_Countries_Analyzed/Citing** - distribución geográfica
14. **All_Journals_Citing** - revistas citantes con métricas IF/CS

### Hojas Especiales:

15. **Fast_Metrics** - todas las métricas rápidas en una tabla
16. **Top_Concepts** - top-10 conceptos temáticos
17. **Title_Keywords** - análisis de palabras clave en títulos
18. **Citation_Seasonality** - estacionalidad de citas
19. **Optimal_Publication_Months** - recomendaciones de tiempo de publicación
20. **Potential_Reviewers** - revisores potenciales
21. **Special_Analysis_Metrics** - métricas del modo Análisis Especial

## 🌍 Multilenguaje

### Idiomas Disponibles:
- **Inglés** - idioma predeterminado
- **Español** - traducción completa de interfaz y terminología

### Cómo Cambiar Idioma:
1. Abra la barra lateral (panel izquierdo)
2. En la sección "Idioma" seleccione el idioma deseado
3. La interfaz cambiará instantáneamente

## 📚 Diccionario de Términos

### Funcionalidad de Aprendizaje:
- **Búsqueda de Términos** - lista desplegable de todas las métricas
- **Explicaciones Detalladas** - definición, cálculo, interpretación, ejemplos
- **Seguimiento de Progreso** - estadística de términos estudiados
- **Categorización** - 7 categorías de métricas para aprendizaje sistemático

### Categorías de Términos:
- 🔵 **Citas** - métricas de citación
- 🟢 **Referencias** - análisis de referencias
- 🟠 **Autores** - estadísticas de autores
- 🟣 **Temas** - análisis temático
- 🔴 **Revista** - identificadores de revista
- ⚫ **Técnico** - aspectos técnicos
- 🟤 **Bases de Datos** - bases de datos

## 🔮 Analítica Predictiva

### Análisis de Estacionalidad de Citas:
- **Identificar meses** con mayor actividad de citas
- **Recomendaciones de tiempo de publicación** considerando tiempo hasta primera cita
- **Visualización** de distribución mensual de citas

### Búsqueda de Revisores Potenciales:
- **Búsqueda automática** de autores que citan la revista pero nunca publicaron en ella
- **Exclusión de conflictos de interés** - autores sin conexiones con la revista
- **Clasificación** por número de citas

### Análisis de Palabras Clave:
- **Palabras de contenido** - términos significativos en títulos
- **Palabras compuestas** - términos compuestos con guión
- **Palabras vacías científicas** - términos científicos de uso frecuente
- **Comparación** de artículos analizados y citantes

## 💡 Consejos de Uso

### Para Mejores Resultados:
1. **Use ISSN exacto** - verifique corrección del identificador
2. **Comience con períodos cortos** - 2-3 años para pruebas
3. **Active Análisis Especial** para revistas de Scopus/WoS
4. **Estudie el diccionario** antes del análisis profundo de métricas
5. **Descargue informe Excel** para estudio detallado

### Interpretación de Datos:
- **Compare métricas** con el campo de conocimiento de la revista
- **Considere edad de la revista** - revistas jóvenes tienen patrones diferentes
- **Analice tendencias** - dinámica más importante que valores absolutos
- **Use múltiples métricas** para evaluación integral

## ⚠️ Notas Importantes

### Limitaciones de Datos:
- Dependencia de calidad de datos de Crossref y OpenAlex
- Tiempo de procesamiento depende de cantidad de artículos y citas
- Algunas métricas requieren volumen mínimo de datos

### Recomendaciones:
- Para revistas grandes analice períodos muestrales
- Verifique integridad de datos mediante Crossref antes del análisis
- Use conexión estable a internet
- Guarde informes Excel para comparaciones posteriores

## 🆘 Soporte

### Si Ocurren Problemas:
1. **Verifique conexión a internet**
2. **Asegure corrección del ISSN**
3. **Intente acortar período de análisis**
4. **Actualice página del navegador**

### Para Casos Complejos:
- Use modo Análisis Especial para verificación de datos
- Analice revistas con métricas conocidas para calibración
- Consulte diccionario integrado para comprensión de métricas

---

**Journal Analysis Tool** proporciona herramientas profesionales para editores, bibliometristas e investigadores, permitiendo análisis integral de revistas científicas usando métodos y métricas modernos.

=============================================================================
=============================================================================
# Journal Analysis Tool - Guida Utente Completa

## 🎯 Informazioni sul Programma

**Journal Analysis Tool** è uno strumento professionale per l'analisi completa di riviste scientifiche, che fornisce analisi approfondite di citazioni, metriche e tendenze di sviluppo delle riviste.

### 🌟 Caratteristiche Principali

- **📊 Analisi Bibliometrica Completa** - statistiche su pubblicazioni, citazioni, autori
- **🚀 Metriche Veloci** - 10+ indicatori chiave senza lunghi tempi di caricamento
- **🎯 Modalità Analisi Speciale** - calcolo di analoghi CiteScore e Impact Factor
- **🌍 Interfaccia Bilingue** - lingue italiano e inglese
- **📚 Dizionario Incorporato** - apprendimento termini scientifici con monitoraggio progresso
- **🔮 Analisi Predittiva** - raccomandazioni tempi pubblicazione, ricerca revisori
- **📈 Visualizzazioni Interattive** - grafici e dashboard
- **📥 Report Dettagliati** - file Excel con 20+ fogli di dati

## 🚀 Guida Rapida

### Passo 1: Parametri di Analisi di Base
- **ISSN Rivista**: Inserire l'ISSN della rivista analizzata (ad esempio: `2411-1414`)
- **Periodo di Analisi**: Anni o intervallo (ad esempio: `2020-2023`)
- **Modalità Analisi Speciale**: Attivare per calcolo metriche CiteScore/Impact Factor

### Passo 2: Avviare Analisi
Premere il pulsante **"Avvia Analisi"** - il processo richiede da 5 a 30 minuti a seconda del volume dati.

### Passo 3: Esplorare Risultati
- Visualizzare risultati nelle schede dashboard
- Scaricare report Excel completo
- Studiare metriche usando il dizionario incorporato

## 📊 Descrizione Metriche Principali

### 🔬 Indicatori di Base

| Metrica | Descrizione | Interpretazione |
|---------|----------|---------------|
| **H-index** | Indice H - produttività e impatto | Più alto = migliore. H-index 10 significa 10 articoli con ≥10 citazioni ciascuno |
| **Numero Totale Articoli** | Numero pubblicazioni analizzate | Volume output scientifico rivista |
| **Numero Totale Citazioni** | Somma citazioni tutti articoli | Influenza complessiva rivista |
| **Citazioni Medie per Articolo** | Citazioni/articoli | Influenza media articoli |

### 📈 Metriche Veloci (calcolo senza API)

| Metrica | Descrizione | Valori Normali |
|---------|----------|---------------------|
| **Età Riferimenti** | Età media riferimenti in articoli | 5-8 anni - rivista moderna, >10 anni - classica |
| **JSCR** | Tasso Auto-citazione Rivista | 10-20% - normale, >30% - possibile isolamento |
| **Emivita Citazioni** | Tempo ricezione metà citazioni | 2-4 anni - scienze veloci, >5 anni - fondamentali |
| **FWCI** | Impatto Citazione Ponderato per Campo | 1.0 - medio campo, >1.2 - sopra media |
| **Velocità Citazione** | Velocità citazione (primi 2 anni) | Più alto = riconoscimento più rapido |
| **Premio Impatto OA** | Premio accesso aperto | +10-50% - intervallo tipico |
| **Indice Elite** | Articoli in top-10% per citazioni | >15% - indicatore eccellente |
| **Gini Autori** | Disuguaglianza pubblicazioni tra autori | 0.1-0.3 - uniforme, >0.6 - dominanza |
| **DBI** | Diversità Tematica | 0-1, più alto = più diversificato |

## 🎯 Modalità Analisi Speciale

### Cos'è?
Modalità speciale per calcolo analoghi **CiteScore** e **Impact Factor** secondo metodologie Scopus e Web of Science.

### Come funziona?
- **CiteScore**: Analizza periodo 1580-120 giorni da data corrente
- **Impact Factor**: Utilizza finestre temporali specifiche (2+2 anni)
- **Adeguamenti**: Considera solo citazioni da riviste indicizzate

### Interpretazione Risultati:
- **CiteScore > 1.0** - sopra media campo
- **Impact Factor > 3.0** - rivista alto impatto
- **Grande differenza** tra metriche regolari e adeguate indica citazioni da fonti non indicizzate

## 📋 Struttura Report Excel

### Fogli Principali:

1. **Analyzed_Articles** - dettagli articoli rivista analizzati
2. **Citing_Works** - informazioni opere citanti
3. **Work_Overlaps** - sovrapposizioni autori e affiliazioni
4. **First_Citations** - tempo fino prima citazione (escluse note editoriali)
5. **Statistics** - statistiche combinate tutti indicatori

### Fogli Analitici:

6. **Citing_Stats** - metriche citazione (H-index, accumulo citazioni)
7. **Citations_by_Year** - dinamica citazioni per anni
8. **Citation_Accumulation_Curves** - curve accumulo citazioni
9. **Citation_Network** - rete citazioni tra anni

### Fogli Partecipanti:

10. **All_Authors_Analyzed** - autori rivista (con normalizzazione nomi)
11. **All_Authors_Citing** - autori opere citanti
12. **All_Affiliations_Analyzed/Citing** - affiliazioni
13. **All_Countries_Analyzed/Citing** - distribuzione geografica
14. **All_Journals_Citing** - riviste citanti con metriche IF/CS

### Fogli Speciali:

15. **Fast_Metrics** - tutte metriche veloci in una tabella
16. **Top_Concepts** - top-10 concetti tematici
17. **Title_Keywords** - analisi parole chiave titoli
18. **Citation_Seasonality** - stagionalità citazioni
19. **Optimal_Publication_Months** - raccomandazioni tempi pubblicazione
20. **Potential_Reviewers** - revisori potenziali
21. **Special_Analysis_Metrics** - metriche modalità Analisi Speciale

## 🌍 Multilingue

### Lingue Disponibili:
- **Inglese** - lingua predefinita
- **Italiano** - traduzione completa interfaccia e terminologia

### Come Cambiare Lingua:
1. Aprire barra laterale (pannello sinistro)
2. Nella sezione "Lingua" selezionare lingua desiderata
3. Interfaccia cambia istantaneamente

## 📚 Dizionario Terminologico

### Funzionalità Apprendimento:
- **Ricerca Termini** - lista a discesa tutte metriche
- **Spiegazioni Dettagliate** - definizione, calcolo, interpretazione, esempi
- **Monitoraggio Progresso** - statistica termini studiati
- **Categorizzazione** - 7 categorie metriche per apprendimento sistematico

### Categorie Termini:
- 🔵 **Citazioni** - metriche citazione
- 🟢 **Riferimenti** - analisi riferimenti
- 🟠 **Autori** - statistiche autori
- 🟣 **Temi** - analisi tematica
- 🔴 **Rivista** - identificatori rivista
- ⚫ **Tecnico** - aspetti tecnici
- 🟤 **Database** - basi dati

## 🔮 Analisi Predittiva

### Analisi Stagionalità Citazioni:
- **Identificare mesi** con maggiore attività citazioni
- **Raccomandazioni tempi pubblicazione** considerando tempo fino prima citazione
- **Visualizzazione** distribuzione mensile citazioni

### Ricerca Revisori Potenziali:
- **Ricerca automatica** autori che citano rivista ma mai pubblicati in essa
- **Esclusione conflitti interesse** - autori senza connessioni rivista
- **Classificazione** per numero citazioni

### Analisi Parole Chiave:
- **Parole contenuto** - termini significativi titoli
- **Parole composte** - termini composti con trattino
- **Stopword scientifiche** - termini scientifici uso frequente
- **Confronto** articoli analizzati e citanti

## 💡 Consigli Utilizzo

### Per Migliori Risultati:
1. **Usare ISSN esatto** - verificare correttezza identificatore
2. **Iniziare periodi brevi** - 2-3 anni per test
3. **Attivare Analisi Speciale** per riviste Scopus/WoS
4. **Studiare dizionario** prima analisi profonda metriche
5. **Scaricare report Excel** per studio dettagliato

### Interpretazione Dati:
- **Confrontare metriche** con campo conoscenza rivista
- **Considerare età rivista** - riviste giovani hanno pattern diversi
- **Analizzare trend** - dinamica più importante valori assoluti
- **Usare multiple metriche** per valutazione completa

## ⚠️ Note Importanti

### Limitazioni Dati:
- Dipendenza qualità dati Crossref e OpenAlex
- Tempo elaborazione dipende quantità articoli e citazioni
- Alcune metriche richiedono volume minimo dati

### Raccomandazioni:
- Per riviste grandi analizzare periodi campione
- Verificare completezza dati tramite Crossref prima analisi
- Usare connessione internet stabile
- Salvare report Excel per confronti successivi

## 🆘 Supporto

### Se Problemi:
1. **Verificare connessione internet**
2. **Assicurarsi correttezza ISSN**
3. **Provare ridurre periodo analisi**
4. **Aggiornare pagina browser**

### Per Casi Complessi:
- Usare modalità Analisi Speciale per verifica dati
- Analizzare riviste con metriche note per calibrazione
- Consultare dizionario incorporato per comprensione metriche

---

**Journal Analysis Tool** fornisce strumenti professionali per editori, bibliometrici e ricercatori, permettendo analisi completa riviste scientifiche usando metodi e metriche moderne.

=============================================================================
=============================================================================
# أداة تحليل المجلات - دليل المستخدم الكامل

## 🎯 حول البرنامج

**أداة تحليل المجلات** هي أداة احترافية للتحليل الشامل للمجلات العلمية، توفر تحليلات متعمقة للاقتباسات والمقاييس واتجاهات تطور المجلات.

### 🌟 الميزات الرئيسية

- **📊 تحليل ببليومتري كامل** - إحصائيات النشر، الاقتباسات، المؤلفين
- **🚀 مقاييس سريعة** - 10+ مؤشرات رئيسية بدون أوقات تحميل طويلة
- **🎯 وضع التحليل الخاص** - حساب نظائر سايت سكور وعامل التأثير
- **🌍 واجهة ثنائية اللغة** - اللغتان العربية والإنجليزية
- **📚 قاموس مدمج** - تعلم المصطلحات العلمية مع متابعة التقدم
- **🔮 التحليلات التنبؤية** - توصيات توقيت النشر، البحث عن المحكمين
- **📈 تصورات تفاعلية** - رسوم بيانية ولوحات تحكم
- **📥 تقارير مفصلة** - ملفات إكسل تحتوي على 20+ ورقة بيانات

## 🚀 البدء السريع

### الخطوة 1: معايير التحليل الأساسية
- **رقم ISSN للمجلة**: أدخل ISSN للمجلة محل التحليل (مثال: `2411-1414`)
- **فترة التحليل**: سنوات أو نطاق (مثال: `2023-2020`)
- **وضع التحليل الخاص**: تفعيل لحساب مقاييس سايت سكور/عامل التأثير

### الخطوة 2: بدء التحليل
اضغط على زر **"بدء التحليل"** - تستغرق العملية من 5 إلى 30 دقيقة حسب حجم البيانات.

### الخطوة 3: استكشاف النتائج
- عرض النتائج في علامات التبويب بلوحة التحكم
- تحميل تقرير إكسل الكامل
- دراسة المقاييس باستخدام القاموس المدمج

## 📊 وصف المقاييس الرئيسية

### 🔬 المؤشرات الأساسية

| المقياس | الوصف | التفسير |
|---------|----------|---------------|
| **مؤشر هيرش** | مؤشر هيرش - الإنتاجية والتأثير | أعلى = أفضل. مؤشر هيرش 10 يعني 10 مقالات مع 10 اقتباسات لكل منها على الأقل |
| **إجمالي عدد المقالات** | عدد المنشورات التي تم تحليلها | حجم الإنتاج العلمي للمجلة |
| **إجمالي عدد الاقتباسات** | مجموع اقتباسات جميع المقالات | التأثير الكلي للمجلة |
| **متوسط الاقتباسات لكل مقال** | الاقتباسات/المقالات | متوسط تأثير المقالات |

### 📈 المقاييس السريعة (حساب بدون واجهة برمجة التطبيقات)

| المقياس | الوصف | القيم الطبيعية |
|---------|----------|---------------------|
| **عمر المراجع** | متوسط عمر المراجع في المقالات | 8-5 سنوات - مجلة حديثة، 10+ سنوات - كلاسيكية |
| **معدل الاقتباس الذاتي للمجلة** | معدل الاقتباس الذاتي للمجلة | 20%-10% - طبيعي، 30%+ - عزل محتمل |
| **عمر النصف للاقتباس** | الوقت للحصول على نصف الاقتباسات | 4-2 سنوات - علوم سريعة، 5+ سنوات - أساسية |
| **الأثر الموزون للاقتباس حسب المجال** | الأثر الموزون للاقتباس حسب المجال | 1.0 - متوسط المجال، 1.2+ - فوق المتوسط |
| **سرعة الاقتباس** | سرعة الاقتباس (أول سنتين) | أعلى = اعتراف أسرع |
| **علاوة تأثير الوصول المفتوح** | علاوة الوصول المفتوح | 50%+10% - النطاق المعتاد |
| **مؤشر النخبة** | مقالات في أعلى 10% حسب الاقتباسات | 15%+ - مؤشر ممتاز |
| **معامل جيني للمؤلفين** | عدم المساواة في النشر بين المؤلفين | 0.3-0.1 - موحد، 0.6+ - هيمنة |
| **مؤشر تنوع الموضوعات** | تنوع الموضوعات | 0-1، أعلى = أكثر تنوعاً |

## 🎯 وضع التحليل الخاص

### ما هو؟
وضع خاص لحساب نظائر **سايت سكور** و**عامل التأثير** وفق منهجيات سكوبس وويب أوف ساينس.

### كيف يعمل؟
- **سايت سكور**: يحلل الفترة 1580-120 يوماً من التاريخ الحالي
- **عامل التأثير**: يستخدم نوافذ زمنية محددة (2+2 سنة)
- **التعديلات**: يأخذ في الاعتبار فقط الاقتباسات من المجلات المفهرسة

### تفسير النتائج:
- **سايت سكور > 1.0** - فوق متوسط المجال
- **عامل التأثير > 3.0** - مجلة عالية التأثير
- **فرق كبير** بين المقاييس العادية والمعدلة يشير إلى اقتباسات من مصادر غير مفهرسة

## 📋 هيكل تقرير إكسل

### الأوراق الرئيسية:

1. **المقالات_المحللة** - تفاصيل مقالات المجلة التي تم تحليلها
2. **الأعمال_المقتبسة** - معلومات عن الأعمال المقتبسة
3. **التداخلات_بين_الأعمال** - تداخلات المؤلفين والانتماءات
4. **أول_اقتباسات** - الوقت حتى أول اقتباس (باستثناء الملاحظات التحريرية)
5. **الإحصائيات** - إحصائيات مجمعة لجميع المؤشرات

### الأوراق التحليلية:

6. **إحصائيات_الاقتباس** - مقاييس الاقتباس (مؤشر هيرش، تراكم الاقتباسات)
7. **الاقتباسات_حسب_السنة** - ديناميكيات الاقتباس حسب السنوات
8. **منحنيات_تراكم_الاقتباسات** - منحنيات تراكم الاقتباسات
9. **شبكة_الاقتباسات** - شبكة الاقتباسات بين السنوات

### أوراق المشاركين:

10. **جميع_المؤلفين_المحللين** - مؤلفو المجلة (مع توحيد تنسيق الأسماء)
11. **جميع_المؤلفين_المقتبسين** - مؤلفو الأعمال المقتبسة
12. **جميع_الانتماءات_المحللة/المقتبسة** - الانتماءات
13. **جميع_البلدان_المحللة/المقتبسة** - التوزيع الجغرافي
14. **جميع_المجلات_المقتبسة** - المجلات المقتبسة مع مقاييس عامل التأثير/سايت سكور

### الأوراق الخاصة:

15. **المقاييس_السريعة** - جميع المقاييس السريعة في جدول واحد
16. **أهم_المفاهيم** - أهم 10 مفاهيم موضوعية
17. **كلمات_مفتاحية_في_العناوين** - تحليل الكلمات المفتاحية في العناوين
18. **موسمية_الاقتباسات** - موسمية الاقتباسات
19. **أشهر_النشر_المثلى** - توصيات توقيت النشر
20. **محكمون_محتملون** - محكمون محتملون
21. **مقاييس_التحليل_الخاص** - مقاييس وضع التحليل الخاص

## 🌍 تعدد اللغات

### اللغات المتاحة:
- **الإنجليزية** - اللغة الافتراضية
- **العربية** - ترجمة كاملة للواجهة والمصطلحات

### كيفية تغيير اللغة:
1. افتح الشريط الجانبي (اللوحة اليسرى)
2. في قسم "اللغة" اختر اللغة المطلوبة
3. ستتغير الواجهة على الفور

## 📚 قاموس المصطلحات

### وظائف التعلم:
- **بحث المصطلحات** - قائمة منسدلة لجميع المقاييس
- **شروحات مفصلة** - تعريف، حساب، تفسير، أمثلة
- **متابعة التقدم** - إحصائيات المصطلحات التي تمت دراستها
- **التصنيف** - 7 فئات من المقاييس للدراسة المنهجية

### فئات المصطلحات:
- 🔵 **الاقتباسات** - مقاييس الاقتباس
- 🟢 **المراجع** - تحليل المراجع
- 🟠 **المؤلفون** - إحصائيات المؤلفين
- 🟣 **الموضوعات** - التحليل الموضوعي
- 🔴 **المجلة** - معرفات المجلة
- ⚫ **التقني** - الجوانب التقنية
- 🟤 **قواعد_البيانات** - قواعد البيانات

## 🔮 التحليلات التنبؤية

### تحليل موسمية الاقتباسات:
- **تحديد الأشهر** ذات أعلى نشاط اقتباس
- **توصيات توقيت النشر** مع مراعاة الوقت حتى أول اقتباس
- **التصور** التوزيع الشهري للاقتباسات

### البحث عن محكمين محتملين:
- **بحث تلقائي** عن المؤلفين الذين يقتبسون من المجلة ولكن لم ينشروا فيها أبداً
- **استبعاد تضارب المصالح** - المؤلفون بدون روابط مع المجلة
- **التصنيف** حسب عدد الاقتباسات

### تحليل الكلمات المفتاحية:
- **كلمات المحتوى** - مصطلحات مهمة في العناوين
- **كلمات مركبة** - مصطلحات مركبة بشرطة
- **كلمات توقف علمية** - مصطلحات علمية مستخدمة بشكل متكرر
- **مقارنة** المقالات المحللة والمقتبسة

## 💡 نصائح الاستخدام

### للحصول على أفضل النتائج:
1. **استخدم ISSN الدقيق** - تحقق من صحة المعرف
2. **ابدأ بفترات قصيرة** - 3-2 سنة للاختبار
3. **قم بتفعيل التحليل الخاص** لمجلات سكوبس/ويب أوف ساينس
4. **ادرس القاموس** قبل التحليل العميق للمقاييس
5. **حمّل تقرير إكسل** للدراسة التفصيلية

### تفسير البيانات:
- **قارن المقاييس** مع مجال معرفة المجلة
- **خذ في الاعتبار عمر المجلة** - المجلات الصغيرة لها أنماط مختلفة
- **حلل الاتجاهات** - الديناميكيات أكثر أهمية من القيم المطلقة
- **استخدم مقاييس متعددة** للتقييم الشامل

## ⚠️ ملاحظات مهمة

### قيود البيانات:
- الاعتماد على جودة بيانات كروسريف وأوبن أليكس
- وقت المعالجة يعتمد على عدد المقالات والاقتباسات
- بعض المقاييس تتطلب حداً أدنى من حجم البيانات

### التوصيات:
- للمجلات الكبيرة، حلل فترات عينة
- تحقق من اكتمال البيانات عبر كروسريف قبل التحليل
- استخدم اتصال إنترنت مستقر
- احفظ تقارير إكسل للمقارنة اللاحقة

## 🆘 الدعم

### في حالة حدوث مشاكل:
1. **تحقق من اتصال الإنترنت**
2. **تأكد من صحة ISSN**
3. **حاول تقصير فترة التحليل**
4. **حدث صفحة المتصفح**

### للحالات المعقدة:
- استخدم وضع التحليل الخاص للتحقق من البيانات
- حلل المجلات ذات المقاييس المعروحة للمعايرة
- ارجع إلى القاموس المدمج لفهم المقاييس

---

**أداة تحليل المجلات** توفر أدوات احترافية للمحررين، أخصائيي الببليومتريا، والباحثين، مما يمكنهم من إجراء تحليل شامل للمجلات العلمية باستخدام الأساليب والمقاييس الحديثة.

=============================================================================
=============================================================================
# 期刊分析工具 - 完整用户指南

## 🎯 关于程序

**期刊分析工具** 是一款专业的科学期刊综合分析工具，提供深入的引用分析、指标和期刊发展趋势。

### 🌟 主要功能

- **📊 完整文献计量分析** - 出版物统计、引用、作者
- **🚀 快速指标** - 10+ 个关键指标，无需长时间加载
- **🎯 特殊分析模式** - 计算类似CiteScore和影响因子的指标
- **🌍 双语界面** - 中文和英文语言
- **📚 内置词典** - 学习科学术语并跟踪进度
- **🔮 预测分析** - 出版时间推荐、审稿人搜索
- **📈 交互式可视化** - 图表和仪表板
- **📥 详细报告** - 包含20+个工作表的Excel文件

## 🚀 快速入门

### 步骤1：基本分析参数
- **期刊ISSN**：输入分析期刊的ISSN（例如：`2411-1414`）
- **分析期间**：年份或范围（例如：`2020-2023`）
- **特殊分析模式**：启用以计算CiteScore/影响因子指标

### 步骤2：开始分析
点击**"开始分析"**按钮 - 根据数据量，过程需要5到30分钟。

### 步骤3：探索结果
- 在仪表板选项卡中查看结果
- 下载完整的Excel报告
- 使用内置词典研究指标

## 📊 主要指标说明

### 🔬 基本指标

| 指标 | 描述 | 解释 |
|---------|----------|---------------|
| **H指数** | H指数 - 生产力和影响力 | 越高越好。H指数10表示有10篇文章每篇至少被引用10次 |
| **文章总数** | 分析的出版物数量 | 期刊科学产出量 |
| **总引用数** | 所有文章的总引用次数 | 期刊的整体影响力 |
| **篇均引用数** | 引用数/文章数 | 文章的平均影响力 |

### 📈 快速指标（无需API计算）

| 指标 | 描述 | 正常值 |
|---------|----------|---------------------|
| **参考文献年龄** | 文章中参考文献的平均年龄 | 5-8年 - 现代期刊，>10年 - 经典期刊 |
| **期刊自引率** | 期刊自引率 | 10-20% - 正常，>30% - 可能孤立 |
| **引用半衰期** | 获得一半引用的时间 | 2-4年 - 快速科学，>5年 - 基础科学 |
| **领域加权引用影响力** | 领域加权引用影响力 | 1.0 - 领域平均，>1.2 - 高于平均 |
| **引用速度** | 引用速度（前2年） | 越高 = 认可越快 |
| **开放获取影响力溢价** | 开放获取溢价 | +10-50% - 典型范围 |
| **精英指数** | 引用前10%的文章 | >15% - 优秀指标 |
| **作者基尼系数** | 作者间发表不平等 | 0.1-0.3 - 均匀，>0.6 - 主导 |
| **多样性指数** | 主题多样性 | 0-1，越高 = 越多样化 |

## 🎯 特殊分析模式

### 这是什么？
根据Scopus和Web of Science方法计算**CiteScore**和**影响因子**类似指标的特殊模式。

### 如何工作？
- **CiteScore**：分析当前日期前1580-120天的期间
- **影响因子**：使用特定时间窗口（2+2年）
- **调整**：仅考虑来自索引期刊的引用

### 结果解释：
- **CiteScore > 1.0** - 高于领域平均
- **影响因子 > 3.0** - 高影响力期刊
- **常规指标与调整指标之间的巨大差异**表明来自非索引来源的引用

## 📋 Excel报告结构

### 主要工作表：

1. **已分析文章** - 已分析期刊文章的详细信息
2. **引用作品** - 关于引用作品的信息
3. **作品重叠** - 作者和隶属机构的重叠
4. **首次引用** - 到首次引用的时间（不包括编辑笔记）
5. **统计** - 所有指标的合并统计

### 分析工作表：

6. **引用统计** - 引用指标（H指数，引用积累）
7. **按年引用** - 按年份的引用动态
8. **引用积累曲线** - 引用积累曲线
9. **引用网络** - 年份间的引用网络

### 参与者工作表：

10. **所有已分析作者** - 期刊作者（姓名标准化）
11. **所有引用作者** - 引用作品的作者
12. **所有已分析/引用隶属机构** - 隶属机构
13. **所有已分析/引用国家** - 地理分布
14. **所有引用期刊** - 带有IF/CS指标的引用期刊

### 特殊工作表：

15. **快速指标** - 所有快速指标在一个表中
16. **顶级概念** - 前10个主题概念
17. **标题关键词** - 标题中的关键词分析
18. **引用季节性** - 引用季节性
19. **最佳出版月份** - 出版时间推荐
20. **潜在审稿人** - 潜在审稿人
21. **特殊分析指标** - 特殊分析模式指标

## 🌍 多语言支持

### 可用语言：
- **英文** - 默认语言
- **中文** - 界面和术语的完整翻译

### 如何更改语言：
1. 打开侧边栏（左侧面板）
2. 在"语言"部分选择所需语言
3. 界面将立即切换

## 📚 术语词典

### 学习功能：
- **术语搜索** - 所有指标的下拉列表
- **详细解释** - 定义、计算、解释、示例
- **进度跟踪** - 已学习术语的统计
- **分类** - 7个指标类别用于系统学习

### 术语类别：
- 🔵 **引用** - 引用指标
- 🟢 **参考文献** - 参考文献分析
- 🟠 **作者** - 作者统计
- 🟣 **主题** - 主题分析
- 🔴 **期刊** - 期刊标识符
- ⚫ **技术** - 技术方面
- 🟤 **数据库** - 数据库

## 🔮 预测分析

### 引用季节性分析：
- **识别** 引用活动最高的月份
- **出版时间推荐** 考虑首次引用时间
- **可视化** 月度引用分布

### 潜在审稿人搜索：
- **自动搜索** 引用期刊但从未在其中发表过的作者
- **利益冲突排除** - 与期刊无联系的作者
- **按引用数排名**

### 关键词分析：
- **内容词** - 标题中的重要术语
- **复合词** - 带连字符的复合术语
- **科学停用词** - 常用科学术语
- **比较** 已分析和引用文章

## 💡 使用提示

### 为获得最佳结果：
1. **使用准确的ISSN** - 验证标识符的正确性
2. **从短期开始** - 2-3年进行测试
3. **启用特殊分析** 用于Scopus/WoS期刊
4. **在深入指标分析前研究词典**
5. **下载Excel报告** 进行详细研究

### 数据解释：
- **比较指标** 与期刊知识领域
- **考虑期刊年龄** - 年轻期刊有不同的模式
- **分析趋势** - 动态比绝对值更重要
- **使用多个指标** 进行综合评估

## ⚠️ 重要说明

### 数据限制：
- 依赖Crossref和OpenAlex的数据质量
- 处理时间取决于文章和引用数量
- 某些指标需要最低数据量

### 建议：
- 对于大型期刊，分析样本期间
- 在分析前通过Crossref检查数据完整性
- 使用稳定的互联网连接
- 保存Excel报告用于后续比较

## 🆘 支持

### 如果出现问题：
1. **检查互联网连接**
2. **确保ISSN正确**
3. **尝试缩短分析期间**
4. **刷新浏览器页面**

### 对于复杂情况：
- 使用特殊分析模式验证数据
- 分析具有已知指标的期刊进行校准
- 参考内置词典理解指标

---

**期刊分析工具** 为编辑、文献计量学家和研究人员提供专业工具，使他们能够使用现代方法和指标对科学期刊进行全面分析。

=============================================================================
=============================================================================
# ジャーナル分析ツール - 完全ユーザーガイド

## 🎯 プログラムについて

**ジャーナル分析ツール**は、科学ジャーナルの包括的分析のための専門ツールであり、引用分析、メトリクス、ジャーナルの発展傾向に関する深い分析を提供します。

### 🌟 主な機能

- **📊 完全な文献計量分析** - 出版物統計、引用、著者
- **🚀 高速メトリクス** - 10以上の主要指標を長時間の読み込みなしで
- **🎯 特別分析モード** - CiteScoreおよびインパクトファクターに類似した指標の計算
- **🌍 二言語インターフェース** - 日本語と英語
- **📚 組み込み辞書** - 進捗追跡付き科学用語学習
- **🔮 予測分析** - 出版時期の推奨、査読者検索
- **📈 インタラクティブ可視化** - グラフとダッシュボード
- **📥 詳細レポート** - 20以上のデータシートを含むExcelファイル

## 🚀 クイックスタート

### ステップ1：基本分析パラメータ
- **ジャーナルISSN**：分析対象ジャーナルのISSNを入力（例：`2411-1414`）
- **分析期間**：年度または範囲（例：`2020-2023`）
- **特別分析モード**：CiteScore/インパクトファクターメトリクス計算のために有効化

### ステップ2：分析開始
**「分析開始」**ボタンをクリック - データ量に応じて処理に5〜30分かかります。

### ステップ3：結果の探索
- ダッシュボードタブで結果を表示
- 完全なExcelレポートをダウンロード
- 組み込み辞書を使用してメトリクスを学習

## 📊 主要メトリクス説明

### 🔬 基本指標

| メトリクス | 説明 | 解釈 |
|---------|----------|---------------|
| **H指数** | ハーシュ指数 - 生産性と影響力 | 高いほど良い。H指数10は10本の論文がそれぞれ10回以上引用されたことを意味 |
| **総論文数** | 分析された出版物数 | ジャーナルの科学的アウトプット量 |
| **総被引用数** | 全論文の引用合計 | ジャーナルの全体的な影響力 |
| **論文当たり平均被引用数** | 被引用数/論文数 | 論文の平均的影響力 |

### 📈 高速メトリクス（APIなし計算）

| メトリクス | 説明 | 正常値 |
|---------|----------|---------------------|
| **参考文献年齢** | 論文内参考文献の平均年齢 | 5-8年 - 現代ジャーナル、10年以上 - 古典的ジャーナル |
| **ジャーナル自己引用率** | ジャーナル自己引用率 | 10-20% - 正常、30%超 - 孤立の可能性 |
| **被引用半減期** | 引用の半分を得るまでの時間 | 2-4年 - 速い科学、5年以上 - 基礎科学 |
| **フィールド重み付き被引用インパクト** | フィールド重み付き被引用インパクト | 1.0 - 分野平均、1.2超 - 平均以上 |
| **引用速度** | 引用速度（初めの2年間） | 高いほど認識が速い |
| **オープンアクセスインパクトプレミアム** | オープンアクセスプレミアム | +10-50% - 典型的範囲 |
| **エリート指数** | 被引用数トップ10%の論文 | 15%超 - 優れた指標 |
| **著者ジニ係数** | 著者間の出版不平等 | 0.1-0.3 - 均等、0.6超 - 支配的 |
| **多様性指数** | 主題的多様性 | 0-1、高いほど多様 |

## 🎯 特別分析モード

### 概要
ScopusおよびWeb of Scienceの方法論に基づく**CiteScore**と**インパクトファクター**の類似指標を計算する特別モード。

### 動作方法
- **CiteScore**：現在日から1580-120日前の期間を分析
- **インパクトファクター**：特定の時間枠を使用（2+2年）
- **調整**：索引化ジャーナルからの引用のみ考慮

### 結果解釈：
- **CiteScore > 1.0** - 分野平均以上
- **インパクトファクター > 3.0** - 高影響力ジャーナル
- **通常メトリクスと調整メトリクスの大きな差**は非索引ソースからの引用を示唆

## 📋 Excelレポート構造

### 主要シート：

1. **分析済み論文** - 分析されたジャーナル論文の詳細
2. **引用作品** - 引用作品に関する情報
3. **作品重複** - 著者と所属の重複
4. **初回引用** - 初回引用までの時間（編集ノートを除く）
5. **統計** - 全指標の統合統計

### 分析シート：

6. **引用統計** - 引用メトリクス（H指数、引用蓄積）
7. **年別引用** - 年別の引用動向
8. **引用蓄積曲線** - 引用蓄積曲線
9. **引用ネットワーク** - 年次間の引用ネットワーク

### 参加者シート：

10. **全分析著者** - ジャーナル著者（名前正規化済み）
11. **全引用著者** - 引用作品の著者
12. **全分析/引用所属** - 所属機関
13. **全分析/引用国** - 地理的分布
14. **全引用ジャーナル** - IF/CSメトリクス付き引用ジャーナル

### 特別シート：

15. **高速メトリクス** - 全高速メトリクスを一つの表に
16. **トップ概念** - トップ10主題概念
17. **タイトルキーワード** - タイトル内キーワード分析
18. **引用季節性** - 引用の季節性
19. **最適出版月** - 出版時期の推奨
20. **潜在査読者** - 潜在的な査読者
21. **特別分析メトリクス** - 特別分析モードのメトリクス

## 🌍 多言語対応

### 利用可能言語：
- **英語** - デフォルト言語
- **日本語** - インターフェースと用語の完全翻訳

### 言語変更方法：
1. サイドバーを開く（左パネル）
2. 「言語」セクションで希望言語を選択
3. インターフェースが即時切り替え

## 📚 用語辞書

### 学習機能：
- **用語検索** - 全メトリクスのドロップダウンリスト
- **詳細説明** - 定義、計算、解釈、例
- **進捗追跡** - 学習済み用語の統計
- **分類** - 系統的学習のための7つのメトリクスカテゴリ

### 用語カテゴリ：
- 🔵 **引用** - 引用メトリクス
- 🟢 **参考文献** - 参考文献分析
- 🟠 **著者** - 著者統計
- 🟣 **テーマ** - 主題分析
- 🔴 **ジャーナル** - ジャーナル識別子
- ⚫ **技術** - 技術的側面
- 🟤 **データベース** - データベース

## 🔮 予測分析

### 引用季節性分析：
- **最高引用活動月**の特定
- **初回引用時間**を考慮した出版時期推奨
- **月別引用分布**の可視化

### 潜在査読者検索：
- **ジャーナルを引用しているが投稿経験のない著者**の自動検索
- **利益相反排除** - ジャーナルとの関係ない著者
- **引用数によるランキング**

### キーワード分析：
- **内容語** - タイトル内の重要用語
- **複合語** - ハイフン付き複合用語
- **科学ストップワード** - 頻繁に使用される科学用語
- **分析論文と引用論文**の比較

## 💡 使用上のヒント

### 最良の結果のために：
1. **正確なISSNを使用** - 識別子の正確性を確認
2. **短期間から開始** - テストのために2-3年
3. **Scopus/WoSジャーナルには特別分析を有効化**
4. **メトリクス深部分析前に辞書を学習**
5. **詳細研究のためにExcelレポートをダウンロード**

### データ解釈：
- **メトリクスをジャーナルの知識分野**と比較
- **ジャーナルの年齢を考慮** - 若いジャーナルは異なるパターン
- **趨勢を分析** - 動向は絶対値より重要
- **総合的評価のために複数メトリクス**を使用

## ⚠️ 重要な注意点

### データ制限：
- CrossrefおよびOpenAlexのデータ品質への依存
- 処理時間は論文数と引用数に依存
- 一部メトリクスは最小データ量を必要

### 推奨事項：
- 大規模ジャーナルにはサンプル期間を分析
- 分析前にCrossrefでデータ完全性を確認
- 安定したインターネット接続を使用
- 後続比較のためにExcelレポートを保存

## 🆘 サポート

### 問題発生時：
1. **インターネット接続を確認**
2. **ISSNの正確性を確認**
3. **分析期間の短縮を試みる**
4. **ブラウザページを更新**

### 複雑な場合：
- データ検証に特別分析モードを使用
- 既知のメトリクスを持つジャーナルを分析して較正
- メトリクス理解に組み込み辞書を参照

---

**ジャーナル分析ツール**は、編集者、文献計量学者、研究者向けに専門的ツールを提供し、現代的方法とメトリクスを使用した科学ジャーナルの包括的分析を可能にします。

=============================================================================
=============================================================================