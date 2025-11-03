# -*- coding: utf-8 -*-
"""
Мультиязычная поддержка для Advanced Journal Analysis Tool
"""

class TranslationManager:
    def __init__(self):
        self.languages = {
            'english': 'English',
            'russian': 'Русский', 
            'german': 'Deutsch',
            'spanish': 'Español',
            'italian': 'Italiano',
            'arabic': 'العربية',
            'chinese': '中文',
            'japanese': '日本語'
        }
        
        self.translations = {
            'english': self._get_english_translations(),
            'russian': self._get_russian_translations(),
            'german': self._get_german_translations(),
            'spanish': self._get_spanish_translations(),
            'italian': self._get_italian_translations(),
            'arabic': self._get_arabic_translations(),
            'chinese': self._get_chinese_translations(),
            'japanese': self._get_japanese_translations()
        }
        
        self.current_language = 'english'
    
    def get_language_name(self, code):
        return self.languages.get(code, code)
    
    def set_language(self, language_code):
        if language_code in self.languages:
            self.current_language = language_code
        else:
            self.current_language = 'english'
    
    def get_text(self, key):
        """Получить перевод для указанного ключа"""
        try:
            return self.translations[self.current_language].get(key, self.translations['english'].get(key, key))
        except:
            return key
    
    def _get_english_translations(self):
        return {
            # Interface elements
            'app_title': 'Advanced Journal Analysis Tool',
            'analysis_parameters': 'Analysis Parameters',
            'journal_issn': 'Journal ISSN:',
            'analysis_period': 'Analysis Period:',
            'start_analysis': 'Start Analysis',
            'results': 'Results',
            'download_excel_report': 'Download Excel Report',
            'analysis_results': 'Analysis Results',
            'dictionary_of_terms': 'Dictionary of Terms',
            'select_term_to_learn': 'Select term to learn:',
            'choose_term': 'Choose term...',
            'your_progress': 'Your Progress',
            'information': 'Information',
            'analysis_capabilities': 'Analysis Capabilities',
            'note': 'Note',
            
            # Analysis capabilities
            'capability_1': '📊 H-index and citation metrics',
            'capability_2': '👥 Author and affiliation analysis', 
            'capability_3': '🌍 Geographical distribution',
            'capability_4': '🔗 Overlaps between works',
            'capability_5': '⏱️ Time to citation',
            'capability_6': '📈 Data visualization',
            'capability_7': '🚀 Fast metrics without API',
            'capability_8': '📚 Interactive dictionary of terms',
            
            # Note text
            'note_text_1': 'Analysis may take several minutes',
            'note_text_2': 'Ensure ISSN is correct',
            'note_text_3': 'For large periods, analysis time increases',
            'note_text_4': 'This program does not calculate IF and CiteScore.',
            'note_text_5': '©Chimica Techno Acta, https://chimicatechnoacta.ru / ©developed by daM',
            
            # Results section
            'journal': 'Journal',
            'period': 'Period', 
            'articles_analyzed': 'Articles analyzed',
            'detailed_statistics': 'Detailed Statistics',
            'analyzed_articles': 'Analyzed Articles',
            'citing_works': 'Citing Works',
            'comparative_analysis': 'Comparative Analysis',
            'fast_metrics': 'Fast Metrics',
            
            # Analysis status messages
            'parsing_period': '📅 Parsing period...',
            'getting_journal_name': '📖 Getting journal name...',
            'loading_articles': '📥 Loading articles from Crossref...',
            'validating_data': '🔍 Validating data...',
            'processing_articles': '🔄 Processing analyzed articles...',
            'getting_metadata': 'Getting metadata',
            'collecting_citations': '🔗 Collecting citing works...',
            'collecting_citations_progress': 'Collecting citations',
            'calculating_statistics': '📊 Calculating statistics...',
            'calculating_fast_metrics': '🚀 Calculating fast metrics...',
            'creating_report': '💾 Creating report...',
            'analysis_complete': '✅ Analysis complete!',
            
            # Success messages
            'journal_found': '📖 Journal: **{journal_name}** (ISSN: {issn})',
            'articles_found': '📄 Found analyzed articles: **{count}**',
            'unique_citing_works': '📄 Unique citing works: **{count}**',
            
            # Error messages
            'issn_required': '❌ Enter journal ISSN',
            'period_required': '❌ Enter analysis period',
            'no_articles_found': '❌ Articles not found.',
            'no_correct_years': '❌ No correct years.',
            'range_out_of_bounds': '⚠️ Range outside 1900-2100 or incorrect: {part}',
            'range_parsing_error': '⚠️ Range parsing error: {part}',
            'year_out_of_bounds': '⚠️ Year outside 1900-2100: {year}',
            'not_a_year': '⚠️ Not a year: {part}',
            'articles_skipped': '⚠️ Skipped {count} articles due to data issues',
            'loading_error': 'Loading error: {error}',
            
            # Excel report errors
            'excel_creation_error': '❌ Error creating Excel report: {error}',
            'simplified_report_created': '⚠️ Simplified report created due to memory limitations',
            'critical_excel_error': '❌ Critical error creating simplified report: {error}',
            
            # Metric labels
            'h_index': 'H-index',
            'total_articles': 'Total Articles',
            'total_citations': 'Total Citations',
            'average_citations': 'Average Citations',
            'articles_with_citations': 'Articles with Citations',
            'self_citations': 'Self-Citations',
            'international_articles': 'International Articles',
            'unique_affiliations': 'Unique Affiliations',
            'reference_age': 'Reference Age',
            'jscr': 'JSCR',
            'cited_half_life': 'Cited Half-Life',
            'fwci': 'FWCI',
            'citation_velocity': 'Citation Velocity',
            'oa_impact_premium': 'OA Impact Premium',
            'elite_index': 'Elite Index',
            'author_gini': 'Author Gini',
            
            # Tooltips and explanations
            'h_index_tooltip': 'Index showing the number of articles h that received at least h citations',
            'total_articles_tooltip': 'Total number of articles analyzed',
            'total_citations_tooltip': 'Total number of citations of all journal articles',
            'average_citations_tooltip': 'Average number of citations per article',
            'articles_with_citations_tooltip': 'Number of articles that were cited at least once',
            'self_citations_tooltip': 'References to other articles of the same journal in bibliography',
            'international_articles_tooltip': 'Percentage of articles with authors from different countries',
            'unique_affiliations_tooltip': 'Number of unique scientific organizations represented in the journal',
            
            # Dictionary terms
            'learned_term_toast': '📖 You learned the term: {term}',
            'term_understood': '✅ I understood this term!',
            'term_added_success': '🎉 Excellent! Term "{term}" added to your knowledge collection!',
            'progress_great': '🏆 Excellent result! You learned {count} terms!',
            'progress_good': '📚 Good start! Continue learning terms.',
            
            # Fast metrics details
            'reference_age_details': '**Reference Age:**',
            'reference_age_median': '- Median: {value} years',
            'reference_age_mean': '- Average: {value} years',
            'reference_age_percentile': '- 25-75 percentile: {value} years',
            'reference_age_analyzed': '- References analyzed: {value}',
            'jscr_details': '**Journal Self-Citation Rate:**',
            'jscr_self_cites': '- Self-citations: {value}',
            'jscr_total_cites': '- Total citations: {value}',
            'jscr_percentage': '- Percentage: {value}%',
            'fwci_details': '**Field-Weighted Citation Impact:**',
            'fwci_value': '- FWCI: {value}',
            'fwci_total_cites': '- Total citations: {value}',
            'fwci_expected_cites': '- Expected citations: {value}',
            'dbi_details': '**Diversity Balance Index:**',
            'dbi_value': '- DBI: {value}',
            'dbi_unique_concepts': '- Unique concepts: {value}',
            'dbi_total_mentions': '- Total mentions: {value}',
            
            # Visualization tabs
            'tab_main_metrics': '📈 Main Metrics',
            'tab_authors_organizations': '👥 Authors and Organizations', 
            'tab_geography': '🌍 Geography',
            'tab_citations': '📊 Citations',
            'tab_overlaps': '🔀 Overlaps',
            'tab_citation_timing': '⏱️ Citation Timing',
            'tab_fast_metrics': '🚀 Fast Metrics',
            
            # Analysis details
            'total_references': 'Total References',
            'single_author_articles': 'Single Author Articles',
            'international_collaboration': 'International Collaboration',
            'unique_countries': 'Unique Countries',
            'articles_10_citations': 'Articles with ≥10 citations',
            'unique_journals': 'Unique Journals',
            'unique_publishers': 'Unique Publishers',
            'average_authors_per_article': 'Average authors per article',
            'average_references_per_article': 'Average references per article',
            
            # No data messages
            'no_overlaps_found': '❌ No overlaps between analyzed and citing works found',
            'no_data_for_report': 'No data for report',
            
            # Open access premium message
            'oa_premium_positive': '📈 Positive premium indicates that open access articles are cited more frequently, confirming the value of OA publications!'
        }
    
    def _get_russian_translations(self):
        return {
            # Interface elements
            'app_title': 'Advanced Journal Analysis Tool',
            'analysis_parameters': 'Параметры анализа',
            'journal_issn': 'ISSN журнала:',
            'analysis_period': 'Период анализа:',
            'start_analysis': 'Начать анализ',
            'results': 'Результаты',
            'download_excel_report': 'Скачать Excel отчет',
            'analysis_results': 'Результаты анализа',
            'dictionary_of_terms': 'Словарь терминов',
            'select_term_to_learn': 'Выберите термин для изучения:',
            'choose_term': 'Выберите термин...',
            'your_progress': 'Ваш прогресс',
            'information': 'Информация',
            'analysis_capabilities': 'Возможности анализа',
            'note': 'Примечание',
            
            # Analysis capabilities
            'capability_1': '📊 H-index и метрики цитирования',
            'capability_2': '👥 Анализ авторов и аффилиаций', 
            'capability_3': '🌍 Географическое распределение',
            'capability_4': '🔗 Пересечения между работами',
            'capability_5': '⏱️ Время до цитирования',
            'capability_6': '📈 Визуализация данных',
            'capability_7': '🚀 Быстрые метрики без API',
            'capability_8': '📚 Интерактивный словарь терминов',
            
            # Note text
            'note_text_1': 'Анализ может занять несколько минут',
            'note_text_2': 'Убедитесь в корректности ISSN',
            'note_text_3': 'Для больших периодов время анализа увеличивается',
            'note_text_4': 'Данная программа не расчитывает IF и CiteScore.',
            'note_text_5': '©Chimica Techno Acta, https://chimicatechnoacta.ru / ©developed by daM',
            
            # Results section
            'journal': 'Журнал',
            'period': 'Период', 
            'articles_analyzed': 'Статей проанализировано',
            'detailed_statistics': 'Детальная статистика',
            'analyzed_articles': 'Анализируемые статьи',
            'citing_works': 'Цитирующие работы',
            'comparative_analysis': 'Сравнительный анализ',
            'fast_metrics': 'Быстрые метрики',
            
            # Analysis status messages
            'parsing_period': '📅 Парсинг периода...',
            'getting_journal_name': '📖 Получение названия журнала...',
            'loading_articles': '📥 Загрузка статей из Crossref...',
            'validating_data': '🔍 Валидация данных...',
            'processing_articles': '🔄 Обработка анализируемых статей...',
            'getting_metadata': 'Получение метаданных',
            'collecting_citations': '🔗 Сбор цитирующих работ...',
            'collecting_citations_progress': 'Сбор цитирований',
            'calculating_statistics': '📊 Расчет статистики...',
            'calculating_fast_metrics': '🚀 Расчет быстрых метрик...',
            'creating_report': '💾 Создание отчета...',
            'analysis_complete': '✅ Анализ завершен!',
            
            # Success messages
            'journal_found': '📖 Журнал: **{journal_name}** (ISSN: {issn})',
            'articles_found': '📄 Найдено анализируемых статей: **{count}**',
            'unique_citing_works': '📄 Уникальных цитирующих работ: **{count}**',
            
            # Error messages
            'issn_required': '❌ Введите ISSN журнала',
            'period_required': '❌ Введите период анализа',
            'no_articles_found': '❌ Статьи не найдены.',
            'no_correct_years': '❌ Нет корректных годов.',
            'range_out_of_bounds': '⚠️ Диапазон вне 1900-2100 или некорректный: {part}',
            'range_parsing_error': '⚠️ Ошибка парсинга диапазона: {part}',
            'year_out_of_bounds': '⚠️ Год вне 1900-2100: {year}',
            'not_a_year': '⚠️ Не год: {part}',
            'articles_skipped': '⚠️ Пропущено {count} статей из-за проблем с данными',
            'loading_error': 'Ошибка при загрузке: {error}',
            
            # Excel report errors
            'excel_creation_error': '❌ Ошибка при создании Excel отчета: {error}',
            'simplified_report_created': '⚠️ Создан упрощенный отчет из-за ограничений памяти',
            'critical_excel_error': '❌ Критическая ошибка при создании упрощенного отчета: {error}',
            
            # Metric labels
            'h_index': 'H-index',
            'total_articles': 'Всего статей',
            'total_citations': 'Всего цитирований',
            'average_citations': 'Среднее цитирований',
            'articles_with_citations': 'Статьи с цитированиями',
            'self_citations': 'Самоцитирования',
            'international_articles': 'Международные статьи',
            'unique_affiliations': 'Уникальных аффилиаций',
            'reference_age': 'Reference Age',
            'jscr': 'JSCR',
            'cited_half_life': 'Cited Half-Life',
            'fwci': 'FWCI',
            'citation_velocity': 'Citation Velocity',
            'oa_impact_premium': 'OA Impact Premium',
            'elite_index': 'Elite Index',
            'author_gini': 'Author Gini',
            
            # Tooltips and explanations
            'h_index_tooltip': 'Индекс, показывающий количество статей h, которые получили не менее h цитирований',
            'total_articles_tooltip': 'Общее количество проанализированных статей',
            'total_citations_tooltip': 'Общее количество цитирований всех статей журнала',
            'average_citations_tooltip': 'Среднее количество цитирований на одну статью',
            'articles_with_citations_tooltip': 'Количество статей, которые были процитированы хотя бы один раз',
            'self_citations_tooltip': 'Ссылки на другие статьи того же журнала в библиографии',
            'international_articles_tooltip': 'Процент статей с авторами из разных стран',
            'unique_affiliations_tooltip': 'Количество уникальных научных организаций, представленных в журнале',
            
            # Dictionary terms
            'learned_term_toast': '📖 Вы изучили термин: {term}',
            'term_understood': '✅ Я разобрался с этим термином!',
            'term_added_success': '🎉 Отлично! Термин "{term}" добавлен в вашу коллекцию знаний!',
            'progress_great': '🏆 Отличный результат! Вы изучили {count} терминов!',
            'progress_good': '📚 Хороший старт! Продолжайте изучать термины.',
            
            # Fast metrics details
            'reference_age_details': '**Reference Age:**',
            'reference_age_median': '- Медиана: {value} лет',
            'reference_age_mean': '- Среднее: {value} лет',
            'reference_age_percentile': '- 25-75 перцентиль: {value} лет',
            'reference_age_analyzed': '- Проанализировано ссылок: {value}',
            'jscr_details': '**Journal Self-Citation Rate:**',
            'jscr_self_cites': '- Самоцитирования: {value}',
            'jscr_total_cites': '- Всего цитирований: {value}',
            'jscr_percentage': '- Процент: {value}%',
            'fwci_details': '**Field-Weighted Citation Impact:**',
            'fwci_value': '- FWCI: {value}',
            'fwci_total_cites': '- Общие цитирования: {value}',
            'fwci_expected_cites': '- Ожидаемые цитирования: {value}',
            'dbi_details': '**Diversity Balance Index:**',
            'dbi_value': '- DBI: {value}',
            'dbi_unique_concepts': '- Уникальных концептов: {value}',
            'dbi_total_mentions': '- Всего упоминаний: {value}',
            
            # Visualization tabs
            'tab_main_metrics': '📈 Основные метрики',
            'tab_authors_organizations': '👥 Авторы и организации', 
            'tab_geography': '🌍 География',
            'tab_citations': '📊 Цитирования',
            'tab_overlaps': '🔀 Пересечения',
            'tab_citation_timing': '⏱️ Время цитирования',
            'tab_fast_metrics': '🚀 Быстрые метрики',
            
            # Analysis details
            'total_references': 'Общее количество ссылок',
            'single_author_articles': 'Статьи с одним автором',
            'international_collaboration': 'Международные статьи',
            'unique_countries': 'Уникальных стран',
            'articles_10_citations': 'Статьи с ≥10 цитированиями',
            'unique_journals': 'Уникальных журналов',
            'unique_publishers': 'Уникальных издателей',
            'average_authors_per_article': 'Среднее авторов на статью',
            'average_references_per_article': 'Среднее ссылок на статью',
            
            # No data messages
            'no_overlaps_found': '❌ Пересечения между анализируемыми и цитирующими работами не найдены',
            'no_data_for_report': 'Нет данных для отчета',
            
            # Open access premium message
            'oa_premium_positive': '📈 Положительная премия указывает на то, что статьи в открытом доступе цитируются чаще, что подтверждает ценность OA публикаций!'
        }
    
    def _get_german_translations(self):
        return {
            # Interface elements
            'app_title': 'Advanced Journal Analysis Tool',
            'analysis_parameters': 'Analyseparameter',
            'journal_issn': 'Journal ISSN:',
            'analysis_period': 'Analysezeitraum:',
            'start_analysis': 'Analyse starten',
            'results': 'Ergebnisse',
            'download_excel_report': 'Excel-Bericht herunterladen',
            'analysis_results': 'Analyseergebnisse',
            'dictionary_of_terms': 'Begriffslexikon',
            'select_term_to_learn': 'Begriff zum Lernen auswählen:',
            'choose_term': 'Begriff auswählen...',
            'your_progress': 'Ihr Fortschritt',
            'information': 'Information',
            'analysis_capabilities': 'Analysefähigkeiten',
            'note': 'Hinweis',
            
            # Analysis capabilities
            'capability_1': '📊 H-Index und Zitationsmetriken',
            'capability_2': '👥 Autoren- und Zugehörigkeitsanalyse', 
            'capability_3': '🌍 Geografische Verteilung',
            'capability_4': '🔗 Überschneidungen zwischen Arbeiten',
            'capability_5': '⏱️ Zeit bis zur Zitierung',
            'capability_6': '📈 Datenvisualisierung',
            'capability_7': '🚀 Schnelle Metriken ohne API',
            'capability_8': '📚 Interaktives Begriffslexikon',
            
            # Note text
            'note_text_1': 'Die Analyse kann mehrere Minuten dauern',
            'note_text_2': 'Stellen Sie die Korrektheit der ISSN sicher',
            'note_text_3': 'Bei großen Zeiträumen erhöht sich die Analysezeit',
            'note_text_4': 'Dieses Programm berechnet nicht IF und CiteScore.',
            'note_text_5': '©Chimica Techno Acta, https://chimicatechnoacta.ru / ©developed by daM',
            
            # Results section
            'journal': 'Journal',
            'period': 'Zeitraum', 
            'articles_analyzed': 'Artikel analysiert',
            'detailed_statistics': 'Detaillierte Statistik',
            'analyzed_articles': 'Analysierte Artikel',
            'citing_works': 'Zitierende Arbeiten',
            'comparative_analysis': 'Vergleichende Analyse',
            'fast_metrics': 'Schnelle Metriken',
            
            # Analysis status messages
            'parsing_period': '📅 Zeitraum wird analysiert...',
            'getting_journal_name': '📖 Journalname wird abgerufen...',
            'loading_articles': '📥 Artikel werden von Crossref geladen...',
            'validating_data': '🔍 Daten werden validiert...',
            'processing_articles': '🔄 Analysierte Artikel werden verarbeitet...',
            'getting_metadata': 'Metadaten werden abgerufen',
            'collecting_citations': '🔗 Zitierende Arbeiten werden gesammelt...',
            'collecting_citations_progress': 'Zitationen werden gesammelt',
            'calculating_statistics': '📊 Statistik wird berechnet...',
            'calculating_fast_metrics': '🚀 Schnelle Metriken werden berechnet...',
            'creating_report': '💾 Bericht wird erstellt...',
            'analysis_complete': '✅ Analyse abgeschlossen!',
            
            # Success messages
            'journal_found': '📖 Journal: **{journal_name}** (ISSN: {issn})',
            'articles_found': '📄 Analysierte Artikel gefunden: **{count}**',
            'unique_citing_works': '📄 Einzigartige zitierende Arbeiten: **{count}**',
            
            # Error messages
            'issn_required': '❌ Geben Sie die Journal-ISSN ein',
            'period_required': '❌ Geben Sie den Analysezeitraum ein',
            'no_articles_found': '❌ Keine Artikel gefunden.',
            'no_correct_years': '❌ Keine korrekten Jahre.',
            'range_out_of_bounds': '⚠️ Bereich außerhalb 1900-2100 oder ungültig: {part}',
            'range_parsing_error': '⚠️ Bereichsparsingfehler: {part}',
            'year_out_of_bounds': '⚠️ Jahr außerhalb 1900-2100: {year}',
            'not_a_year': '⚠️ Kein Jahr: {part}',
            'articles_skipped': '⚠️ {count} Artikel aufgrund von Datenproblemen übersprungen',
            'loading_error': 'Ladefehler: {error}',
            
            # Excel report errors
            'excel_creation_error': '❌ Fehler beim Erstellen des Excel-Berichts: {error}',
            'simplified_report_created': '⚠️ Vereinfachter Bericht aufgrund von Speicherbeschränkungen erstellt',
            'critical_excel_error': '❌ Kritischer Fehler beim Erstellen des vereinfachten Berichts: {error}',
            
            # Metric labels
            'h_index': 'H-Index',
            'total_articles': 'Gesamtartikel',
            'total_citations': 'Gesamtzitationen',
            'average_citations': 'Durchschnittliche Zitationen',
            'articles_with_citations': 'Artikel mit Zitationen',
            'self_citations': 'Selbstzitationen',
            'international_articles': 'Internationale Artikel',
            'unique_affiliations': 'Einzigartige Zugehörigkeiten',
            'reference_age': 'Referenzalter',
            'jscr': 'JSCR',
            'cited_half_life': 'Zitierte Halbwertszeit',
            'fwci': 'FWCI',
            'citation_velocity': 'Zitationsgeschwindigkeit',
            'oa_impact_premium': 'OA-Wirkungsprämie',
            'elite_index': 'Elite-Index',
            'author_gini': 'Autor-Gini',
            
            # Tooltips and explanations
            'h_index_tooltip': 'Index, der die Anzahl der Artikel h anzeigt, die mindestens h Zitationen erhalten haben',
            'total_articles_tooltip': 'Gesamtzahl der analysierten Artikel',
            'total_citations_tooltip': 'Gesamtzahl der Zitationen aller Journalartikel',
            'average_citations_tooltip': 'Durchschnittliche Anzahl von Zitationen pro Artikel',
            'articles_with_citations_tooltip': 'Anzahl der Artikel, die mindestens einmal zitiert wurden',
            'self_citations_tooltip': 'Verweise auf andere Artikel desselben Journals in der Bibliographie',
            'international_articles_tooltip': 'Prozentsatz der Artikel mit Autoren aus verschiedenen Ländern',
            'unique_affiliations_tooltip': 'Anzahl der im Journal vertretenen einzigartigen wissenschaftlichen Organisationen',
            
            # Dictionary terms
            'learned_term_toast': '📖 Sie haben den Begriff gelernt: {term}',
            'term_understood': '✅ Ich habe diesen Begriff verstanden!',
            'term_added_success': '🎉 Ausgezeichnet! Begriff "{term}" wurde zu Ihrer Wissenssammlung hinzugefügt!',
            'progress_great': '🏆 Ausgezeichnetes Ergebnis! Sie haben {count} Begriffe gelernt!',
            'progress_good': '📚 Guter Start! Lernen Sie weiter Begriffe.',
            
            # Fast metrics details
            'reference_age_details': '**Referenzalter:**',
            'reference_age_median': '- Median: {value} Jahre',
            'reference_age_mean': '- Durchschnitt: {value} Jahre',
            'reference_age_percentile': '- 25-75 Perzentil: {value} Jahre',
            'reference_age_analyzed': '- Analysierte Referenzen: {value}',
            'jscr_details': '**Journal Self-Citation Rate:**',
            'jscr_self_cites': '- Selbstzitationen: {value}',
            'jscr_total_cites': '- Gesamtzitationen: {value}',
            'jscr_percentage': '- Prozentsatz: {value}%',
            'fwci_details': '**Field-Weighted Citation Impact:**',
            'fwci_value': '- FWCI: {value}',
            'fwci_total_cites': '- Gesamtzitationen: {value}',
            'fwci_expected_cites': '- Erwartete Zitationen: {value}',
            'dbi_details': '**Diversity Balance Index:**',
            'dbi_value': '- DBI: {value}',
            'dbi_unique_concepts': '- Einzigartige Konzepte: {value}',
            'dbi_total_mentions': '- Gesamterwähnungen: {value}',
            
            # Visualization tabs
            'tab_main_metrics': '📈 Hauptmetriken',
            'tab_authors_organizations': '👥 Autoren und Organisationen', 
            'tab_geography': '🌍 Geografie',
            'tab_citations': '📊 Zitationen',
            'tab_overlaps': '🔀 Überschneidungen',
            'tab_citation_timing': '⏱️ Zitationszeit',
            'tab_fast_metrics': '🚀 Schnelle Metriken',
            
            # Analysis details
            'total_references': 'Gesamtreferenzen',
            'single_author_articles': 'Einzelautorenartikel',
            'international_collaboration': 'Internationale Zusammenarbeit',
            'unique_countries': 'Einzigartige Länder',
            'articles_10_citations': 'Artikel mit ≥10 Zitationen',
            'unique_journals': 'Einzigartige Journals',
            'unique_publishers': 'Einzigartige Verlage',
            'average_authors_per_article': 'Durchschnittliche Autoren pro Artikel',
            'average_references_per_article': 'Durchschnittliche Referenzen pro Artikel',
            
            # No data messages
            'no_overlaps_found': '❌ Keine Überschneidungen zwischen analysierten und zitierenden Arbeiten gefunden',
            'no_data_for_report': 'Keine Daten für Bericht',
            
            # Open access premium message
            'oa_premium_positive': '📈 Positive Prämie zeigt, dass Open-Access-Artikel häufiger zitiert werden, was den Wert von OA-Publikationen bestätigt!'
        }
    
    def _get_spanish_translations(self):
        return {
            # Interface elements
            'app_title': 'Advanced Journal Analysis Tool',
            'analysis_parameters': 'Parámetros de Análisis',
            'journal_issn': 'ISSN de la Revista:',
            'analysis_period': 'Período de Análisis:',
            'start_analysis': 'Iniciar Análisis',
            'results': 'Resultados',
            'download_excel_report': 'Descargar Informe Excel',
            'analysis_results': 'Resultados del Análisis',
            'dictionary_of_terms': 'Diccionario de Términos',
            'select_term_to_learn': 'Seleccione término para aprender:',
            'choose_term': 'Elija término...',
            'your_progress': 'Su Progreso',
            'information': 'Información',
            'analysis_capabilities': 'Capacidades de Análisis',
            'note': 'Nota',
            
            # Analysis capabilities
            'capability_1': '📊 H-index y métricas de citas',
            'capability_2': '👥 Análisis de autores y afiliaciones', 
            'capability_3': '🌍 Distribución geográfica',
            'capability_4': '🔗 Superposiciones entre trabajos',
            'capability_5': '⏱️ Tiempo hasta citación',
            'capability_6': '📈 Visualización de datos',
            'capability_7': '🚀 Métricas rápidas sin API',
            'capability_8': '📚 Diccionario interactivo de términos',
            
            # Note text
            'note_text_1': 'El análisis puede tomar varios minutos',
            'note_text_2': 'Asegúrese de que el ISSN sea correcto',
            'note_text_3': 'Para períodos grandes, el tiempo de análisis aumenta',
            'note_text_4': 'Este programa no calcula IF y CiteScore.',
            'note_text_5': '©Chimica Techno Acta, https://chimicatechnoacta.ru / ©developed by daM',
            
            # Results section
            'journal': 'Revista',
            'period': 'Período', 
            'articles_analyzed': 'Artículos analizados',
            'detailed_statistics': 'Estadísticas Detalladas',
            'analyzed_articles': 'Artículos Analizados',
            'citing_works': 'Trabajos que Citán',
            'comparative_analysis': 'Análisis Comparativo',
            'fast_metrics': 'Métricas Rápidas',
            
            # Analysis status messages
            'parsing_period': '📅 Analizando período...',
            'getting_journal_name': '📖 Obteniendo nombre de la revista...',
            'loading_articles': '📥 Cargando artículos de Crossref...',
            'validating_data': '🔍 Validando datos...',
            'processing_articles': '🔄 Procesando artículos analizados...',
            'getting_metadata': 'Obteniendo metadatos',
            'collecting_citations': '🔗 Recopilando trabajos que citán...',
            'collecting_citations_progress': 'Recopilando citas',
            'calculating_statistics': '📊 Calculando estadísticas...',
            'calculating_fast_metrics': '🚀 Calculando métricas rápidas...',
            'creating_report': '💾 Creando informe...',
            'analysis_complete': '✅ ¡Análisis completado!',
            
            # Success messages
            'journal_found': '📖 Revista: **{journal_name}** (ISSN: {issn})',
            'articles_found': '📄 Artículos analizados encontrados: **{count}**',
            'unique_citing_works': '📄 Trabajos que citán únicos: **{count}**',
            
            # Error messages
            'issn_required': '❌ Ingrese el ISSN de la revista',
            'period_required': '❌ Ingrese el período de análisis',
            'no_articles_found': '❌ No se encontraron artículos.',
            'no_correct_years': '❌ No hay años correctos.',
            'range_out_of_bounds': '⚠️ Rango fuera de 1900-2100 o incorrecto: {part}',
            'range_parsing_error': '⚠️ Error de análisis de rango: {part}',
            'year_out_of_bounds': '⚠️ Año fuera de 1900-2100: {year}',
            'not_a_year': '⚠️ No es un año: {part}',
            'articles_skipped': '⚠️ Se omitieron {count} artículos debido a problemas de datos',
            'loading_error': 'Error de carga: {error}',
            
            # Excel report errors
            'excel_creation_error': '❌ Error al crear informe de Excel: {error}',
            'simplified_report_created': '⚠️ Informe simplificado creado debido a limitaciones de memoria',
            'critical_excel_error': '❌ Error crítico al crear informe simplificado: {error}',
            
            # Metric labels
            'h_index': 'H-index',
            'total_articles': 'Total de Artículos',
            'total_citations': 'Total de Citas',
            'average_citations': 'Citas Promedio',
            'articles_with_citations': 'Artículos con Citas',
            'self_citations': 'Autocitas',
            'international_articles': 'Artículos Internacionales',
            'unique_affiliations': 'Afiliaciones Únicas',
            'reference_age': 'Edad de Referencia',
            'jscr': 'JSCR',
            'cited_half_life': 'Vida Media de Citación',
            'fwci': 'FWCI',
            'citation_velocity': 'Velocidad de Citación',
            'oa_impact_premium': 'Prima de Impacto OA',
            'elite_index': 'Índice de Elite',
            'author_gini': 'Gini de Autor',
            
            # Tooltips and explanations
            'h_index_tooltip': 'Índice que muestra la cantidad de artículos h que recibieron al menos h citas',
            'total_articles_tooltip': 'Número total de artículos analizados',
            'total_citations_tooltip': 'Número total de citas de todos los artículos de la revista',
            'average_citations_tooltip': 'Número promedio de citas por artículo',
            'articles_with_citations_tooltip': 'Número de artículos que fueron citados al menos una vez',
            'self_citations_tooltip': 'Referencias a otros artículos de la misma revista en la bibliografía',
            'international_articles_tooltip': 'Porcentaje de artículos con autores de diferentes países',
            'unique_affiliations_tooltip': 'Número de organizaciones científicas únicas representadas en la revista',
            
            # Dictionary terms
            'learned_term_toast': '📖 Has aprendido el término: {term}',
            'term_understood': '✅ ¡He entendido este término!',
            'term_added_success': '🎉 ¡Excelente! Término "{term}" añadido a tu colección de conocimientos!',
            'progress_great': '🏆 ¡Excelente resultado! Has aprendido {count} términos!',
            'progress_good': '📚 ¡Buen comienzo! Continúa aprendiendo términos.',
            
            # Fast metrics details
            'reference_age_details': '**Edad de Referencia:**',
            'reference_age_median': '- Mediana: {value} años',
            'reference_age_mean': '- Promedio: {value} años',
            'reference_age_percentile': '- Percentil 25-75: {value} años',
            'reference_age_analyzed': '- Referencias analizadas: {value}',
            'jscr_details': '**Tasa de Autocitación de Revista:**',
            'jscr_self_cites': '- Autocitas: {value}',
            'jscr_total_cites': '- Citas totales: {value}',
            'jscr_percentage': '- Porcentaje: {value}%',
            'fwci_details': '**Impacto de Citación Ponderado por Campo:**',
            'fwci_value': '- FWCI: {value}',
            'fwci_total_cites': '- Citas totales: {value}',
            'fwci_expected_cites': '- Citas esperadas: {value}',
            'dbi_details': '**Índice de Equilibrio de Diversidad:**',
            'dbi_value': '- DBI: {value}',
            'dbi_unique_concepts': '- Conceptos únicos: {value}',
            'dbi_total_mentions': '- Menciones totales: {value}',
            
            # Visualization tabs
            'tab_main_metrics': '📈 Métricas Principales',
            'tab_authors_organizations': '👥 Autores y Organizaciones', 
            'tab_geography': '🌍 Geografía',
            'tab_citations': '📊 Citas',
            'tab_overlaps': '🔀 Superposiciones',
            'tab_citation_timing': '⏱️ Tiempo de Citación',
            'tab_fast_metrics': '🚀 Métricas Rápidas',
            
            # Analysis details
            'total_references': 'Referencias Totales',
            'single_author_articles': 'Artículos de Autor Único',
            'international_collaboration': 'Colaboración Internacional',
            'unique_countries': 'Países Únicos',
            'articles_10_citations': 'Artículos con ≥10 citas',
            'unique_journals': 'Revistas Únicas',
            'unique_publishers': 'Editores Únicos',
            'average_authors_per_article': 'Promedio de autores por artículo',
            'average_references_per_article': 'Promedio de referencias por artículo',
            
            # No data messages
            'no_overlaps_found': '❌ No se encontraron superposiciones entre trabajos analizados y citantes',
            'no_data_for_report': 'No hay datos para el informe',
            
            # Open access premium message
            'oa_premium_positive': '📈 ¡La prima positiva indica que los artículos de acceso abierto se citan con más frecuencia, lo que confirma el valor de las publicaciones OA!'
        }
    
    def _get_italian_translations(self):
        return {
            # Interface elements
            'app_title': 'Advanced Journal Analysis Tool',
            'analysis_parameters': 'Parametri di Analisi',
            'journal_issn': 'ISSN della Rivista:',
            'analysis_period': 'Periodo di Analisi:',
            'start_analysis': 'Inizia Analisi',
            'results': 'Risultati',
            'download_excel_report': 'Scarica Report Excel',
            'analysis_results': 'Risultati Analisi',
            'dictionary_of_terms': 'Dizionario dei Termini',
            'select_term_to_learn': 'Seleziona termine da imparare:',
            'choose_term': 'Scegli termine...',
            'your_progress': 'Il Tuo Progresso',
            'information': 'Informazione',
            'analysis_capabilities': 'Capacità di Analisi',
            'note': 'Nota',
            
            # Analysis capabilities
            'capability_1': '📊 H-index e metriche di citazione',
            'capability_2': '👥 Analisi autori e affiliazioni', 
            'capability_3': '🌍 Distribuzione geografica',
            'capability_4': '🔗 Sovrapposizioni tra lavori',
            'capability_5': '⏱️ Tempo fino alla citazione',
            'capability_6': '📈 Visualizzazione dati',
            'capability_7': '🚀 Metriche veloci senza API',
            'capability_8': '📚 Dizionario interattivo dei termini',
            
            # Note text
            'note_text_1': 'L\'analisi può richiedere diversi minuti',
            'note_text_2': 'Assicurarsi che l\'ISSN sia corretto',
            'note_text_3': 'Per periodi lunghi, il tempo di analisi aumenta',
            'note_text_4': 'Questo programma non calcola IF e CiteScore.',
            'note_text_5': '©Chimica Techno Acta, https://chimicatechnoacta.ru / ©developed by daM',
            
            # Results section
            'journal': 'Rivista',
            'period': 'Periodo', 
            'articles_analyzed': 'Articoli analizzati',
            'detailed_statistics': 'Statistiche Dettagliate',
            'analyzed_articles': 'Articoli Analizzati',
            'citing_works': 'Lavori che Citano',
            'comparative_analysis': 'Analisi Comparativa',
            'fast_metrics': 'Metriche Veloci',
            
            # Analysis status messages
            'parsing_period': '📅 Analisi del periodo...',
            'getting_journal_name': '📖 Recupero nome rivista...',
            'loading_articles': '📥 Caricamento articoli da Crossref...',
            'validating_data': '🔍 Validazione dati...',
            'processing_articles': '🔄 Elaborazione articoli analizzati...',
            'getting_metadata': 'Recupero metadati',
            'collecting_citations': '🔗 Raccolta lavori che citano...',
            'collecting_citations_progress': 'Raccolta citazioni',
            'calculating_statistics': '📊 Calcolo statistiche...',
            'calculating_fast_metrics': '🚀 Calcolo metriche veloci...',
            'creating_report': '💾 Creazione report...',
            'analysis_complete': '✅ Analisi completata!',
            
            # Success messages
            'journal_found': '📖 Rivista: **{journal_name}** (ISSN: {issn})',
            'articles_found': '📄 Articoli analizzati trovati: **{count}**',
            'unique_citing_works': '📄 Lavori che citano unici: **{count}**',
            
            # Error messages
            'issn_required': '❌ Inserire l\'ISSN della rivista',
            'period_required': '❌ Inserire il periodo di analisi',
            'no_articles_found': '❌ Nessun articolo trovato.',
            'no_correct_years': '❌ Nessun anno corretto.',
            'range_out_of_bounds': '⚠️ Intervallo fuori 1900-2100 o non corretto: {part}',
            'range_parsing_error': '⚠️ Errore di analisi intervallo: {part}',
            'year_out_of_bounds': '⚠️ Anno fuori 1900-2100: {year}',
            'not_a_year': '⚠️ Non è un anno: {part}',
            'articles_skipped': '⚠️ Saltati {count} articoli per problemi dati',
            'loading_error': 'Errore di caricamento: {error}',
            
            # Excel report errors
            'excel_creation_error': '❌ Errore nella creazione report Excel: {error}',
            'simplified_report_created': '⚠️ Report semplificato creato per limiti memoria',
            'critical_excel_error': '❌ Errore critico nella creazione report semplificato: {error}',
            
            # Metric labels
            'h_index': 'H-index',
            'total_articles': 'Totale Articoli',
            'total_citations': 'Totale Citazioni',
            'average_citations': 'Citazioni Medie',
            'articles_with_citations': 'Articoli con Citazioni',
            'self_citations': 'Autocitazioni',
            'international_articles': 'Articoli Internazionali',
            'unique_affiliations': 'Affiliazioni Uniche',
            'reference_age': 'Età Riferimento',
            'jscr': 'JSCR',
            'cited_half_life': 'Emivita Citazione',
            'fwci': 'FWCI',
            'citation_velocity': 'Velocità Citazione',
            'oa_impact_premium': 'Premio Impatto OA',
            'elite_index': 'Indice Elite',
            'author_gini': 'Gini Autore',
            
            # Tooltips and explanations
            'h_index_tooltip': 'Indice che mostra il numero di articoli h che hanno ricevuto almeno h citazioni',
            'total_articles_tooltip': 'Numero totale di articoli analizzati',
            'total_citations_tooltip': 'Numero totale di citazioni di tutti gli articoli della rivista',
            'average_citations_tooltip': 'Numero medio di citazioni per articolo',
            'articles_with_citations_tooltip': 'Numero di articoli che sono stati citati almeno una volta',
            'self_citations_tooltip': 'Riferimenti ad altri articoli della stessa rivista in bibliografia',
            'international_articles_tooltip': 'Percentuale di articoli con autori di diversi paesi',
            'unique_affiliations_tooltip': 'Numero di organizzazioni scientifiche uniche rappresentate nella rivista',
            
            # Dictionary terms
            'learned_term_toast': '📖 Hai imparato il termine: {term}',
            'term_understood': '✅ Ho capito questo termine!',
            'term_added_success': '🎉 Eccellente! Termine "{term}" aggiunto alla tua collezione di conoscenze!',
            'progress_great': '🏆 Risultato eccellente! Hai imparato {count} termini!',
            'progress_good': '📚 Buon inizio! Continua a imparare termini.',
            
            # Fast metrics details
            'reference_age_details': '**Età di Riferimento:**',
            'reference_age_median': '- Mediana: {value} anni',
            'reference_age_mean': '- Media: {value} anni',
            'reference_age_percentile': '- Percentile 25-75: {value} anni',
            'reference_age_analyzed': '- Riferimenti analizzati: {value}',
            'jscr_details': '**Tasso di Autocitazione Rivista:**',
            'jscr_self_cites': '- Autocitazioni: {value}',
            'jscr_total_cites': '- Citazioni totali: {value}',
            'jscr_percentage': '- Percentuale: {value}%',
            'fwci_details': '**Impatto Citazione Ponderato per Campo:**',
            'fwci_value': '- FWCI: {value}',
            'fwci_total_cites': '- Citazioni totali: {value}',
            'fwci_expected_cites': '- Citazioni attese: {value}',
            'dbi_details': '**Indice di Bilanciamento Diversità:**',
            'dbi_value': '- DBI: {value}',
            'dbi_unique_concepts': '- Concetti unici: {value}',
            'dbi_total_mentions': '- Menzioni totali: {value}',
            
            # Visualization tabs
            'tab_main_metrics': '📈 Metriche Principali',
            'tab_authors_organizations': '👥 Autori e Organizzazioni', 
            'tab_geography': '🌍 Geografia',
            'tab_citations': '📊 Citazioni',
            'tab_overlaps': '🔀 Sovrapposizioni',
            'tab_citation_timing': '⏱️ Tempo Citazione',
            'tab_fast_metrics': '🚀 Metriche Veloci',
            
            # Analysis details
            'total_references': 'Riferimenti Totali',
            'single_author_articles': 'Articoli Autore Singolo',
            'international_collaboration': 'Collaborazione Internazionale',
            'unique_countries': 'Paesi Unici',
            'articles_10_citations': 'Articoli con ≥10 citazioni',
            'unique_journals': 'Riviste Uniche',
            'unique_publishers': 'Editori Unici',
            'average_authors_per_article': 'Media autori per articolo',
            'average_references_per_article': 'Media riferimenti per articolo',
            
            # No data messages
            'no_overlaps_found': '❌ Nessuna sovrapposizione trovata tra lavori analizzati e citanti',
            'no_data_for_report': 'Nessun dato per il report',
            
            # Open access premium message
            'oa_premium_positive': '📈 Il premio positivo indica che gli articoli ad accesso aperto vengono citati più frequentemente, confermando il valore delle pubblicazioni OA!'
        }
    
    def _get_arabic_translations(self):
        return {
            # Basic interface elements - Arabic translations will be added
            'app_title': 'Advanced Journal Analysis Tool',
            'analysis_parameters': 'معلمات التحليل',
            'journal_issn': 'رقم ISSN للمجلة:',
            'start_analysis': 'بدء التحليل',
            # ... other Arabic translations would go here
        }
    
    def _get_chinese_translations(self):
        return {
            # Basic interface elements - Chinese translations will be added  
            'app_title': 'Advanced Journal Analysis Tool',
            'analysis_parameters': '分析参数',
            'journal_issn': '期刊 ISSN:',
            'start_analysis': '开始分析',
            # ... other Chinese translations would go here
        }
    
    def _get_japanese_translations(self):
        return {
            # Basic interface elements - Japanese translations will be added
            'app_title': 'Advanced Journal Analysis Tool', 
            'analysis_parameters': '分析パラメータ',
            'journal_issn': 'ジャーナル ISSN:',
            'start_analysis': '分析開始',
            # ... other Japanese translations would go here
        }

# Global translation manager instance
translation_manager = TranslationManager()