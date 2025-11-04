# -*- coding: utf-8 -*-
"""
Мультиязычная поддержка для Advanced Journal Analysis Tool
"""

class TranslationManager:
    def __init__(self):
        self.languages = {
            'english': 'English 🇺🇸',
            'russian': 'Русский 🇷🇺', 
            'german': 'Deutsch 🇩🇪',
            'spanish': 'Español 🇪🇸',
            'italian': 'Italiano 🇮🇹',
            'arabic': 'العربية 🇸🇦',
            'chinese': '中文 🇨🇳',
            'japanese': '日本語 🇯🇵'
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
            'loading_articles': 'Loading data from',
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
            'oa_premium_positive': '📈 Positive premium indicates that open access articles are cited more frequently, confirming the value of OA publications!',
            
            # Additional terms needed
            'language_selection': 'Language Selection',
            'select_language': 'Select language:',
            'analysis_starting': 'Starting analysis...',
            'loaded_articles': 'Loaded {count} articles...',
            'articles_loaded': 'Loaded {count} articles',
            'and': 'and',
            'analysis_may_take_time': 'Analysis may take a long time in case of large number of analyzed articles or citations.',
            'reduce_period_recommended': 'For "quick" statistics, it is recommended to reduce the analysis period...',
            'journal_not_found': 'Journal not found',
            'failed_create_full_report': 'Failed to create full report',
            'try_reduce_data_or_period': 'Try to reduce the amount of analyzed data or analysis period',
            
            # H-index explanation
            'what_is_h_index': 'What is H-index and how to interpret it?',
            
            # Author Gini
            'author_gini_meaning': 'Author Gini Index - what does it mean?',
            'current_value': 'Current value',
            'interpretation': 'Interpretation',
            
            # International collaboration
            'about_international_collaboration': 'About international collaboration',
            'definition': 'Definition',
            'significance_for_science': 'Significance for science',
            'high_international_articles_indicator': 'High percentage of international articles indicates global significance of the journal and broad international recognition.',
            
            # JSCR levels
            'jscr_explanation': 'Journal Self-Citation Rate (JSCR)',
            'low_self_citations_excellent': 'Low level of self-citations - excellent!',
            'moderate_self_citations_normal': 'Moderate level of self-citations - normal',
            'elevated_self_citations_attention': 'Elevated level of self-citations - requires attention',
            'high_self_citations_problems': 'High level of self-citations - may indicate problems',
            
            # Citation timing
            'cited_half_life_explanation': 'Cited Half-Life - citation half-life period',
            'years': 'years',
            
            # First citation details
            'first_citation_details': 'First Citation Details',
            'min_days_to_citation': 'Min days to citation',
            'max_days_to_citation': 'Max days to citation',
            'average_days': 'Average days',
            'median_days': 'Median days',
            
            # Overlaps
            'total_overlaps': 'Total Overlaps',
            'articles_with_overlaps': 'Articles with overlaps',
            'average_overlaps_per_article': 'Average overlaps per article',
            'overlap_count_distribution': 'Overlap count distribution',
            'overlap_count': 'Overlap count',
            'frequency': 'Frequency',
            'overlap_details': 'Overlap details',
            
            # Fast metrics additional
            'citation_velocity_details': '**Citation Velocity:**',
            'average_citations_per_year': 'Average citations per year',
            'articles_with_data': 'Articles with data',
            'oa_impact_premium_details': '**OA Impact Premium:**',
            'premium': 'Premium',
            'oa_articles': 'OA articles',
            'non_oa_articles': 'Non-OA articles',
            
            # Concepts and DBI
            'top_5_thematic_concepts': 'Top-5 Thematic Concepts',
            'top_thematic_concepts': 'Top thematic concepts',
            'concept': 'Concept',
            'mentions': 'Mentions',
            'diversity_balance_index': 'Diversity Balance Index (DBI)',
            'current_dbi_value': 'Current DBI value',
            
            # More tooltips
            'more_about_reference_age': 'More about Reference Age',
            'what_does_it_mean': 'What does this mean?',
            'example': 'Example',
            'open_access_premium': 'Open Access Premium',
            
            # Progress and learning
            'learned_terms': 'Learned terms',
            'analysis_starting': 'Starting analysis...'
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
            'loading_articles': 'Загрузка данных из',
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
            'oa_premium_positive': '📈 Положительная премия указывает на то, что статьи в открытом доступе цитируются чаще, что подтверждает ценность OA публикаций!',
            
            # Additional terms needed
            'language_selection': 'Выбор языка',
            'select_language': 'Выберите язык:',
            'analysis_starting': 'Запуск анализа...',
            'loaded_articles': 'Загружено {count} статей...',
            'articles_loaded': 'Загружено {count} статей',
            'and': 'и',
            'analysis_may_take_time': 'Анализ может занять длительное время в случае большого числа анализируемых статей или цитирований.',
            'reduce_period_recommended': 'Для получения "быстрой" статистики рекомендуется уменьшить период анализа...',
            'journal_not_found': 'Журнал не найден',
            'failed_create_full_report': 'Не удалось создать полный отчет',
            'try_reduce_data_or_period': 'Попробуйте уменьшить объем анализируемых данных или период анализа',
            
            # H-index explanation
            'what_is_h_index': 'Что такое H-index и как его интерпретировать?',
            
            # Author Gini
            'author_gini_meaning': 'Индекс Джини авторов - что это значит?',
            'current_value': 'Текущее значение',
            'interpretation': 'Интерпретация',
            
            # International collaboration
            'about_international_collaboration': 'О международном сотрудничестве',
            'definition': 'Определение',
            'significance_for_science': 'Значение для науки',
            'high_international_articles_indicator': 'Высокий процент международных статей указывает на глобальную значимость журнала и широкое международное признание.',
            
            # JSCR levels
            'jscr_explanation': 'Journal Self-Citation Rate (JSCR)',
            'low_self_citations_excellent': 'Низкий уровень самоцитирований - отлично!',
            'moderate_self_citations_normal': 'Умеренный уровень самоцитирований - нормально',
            'elevated_self_citations_attention': 'Повышенный уровень самоцитирований - требует внимания',
            'high_self_citations_problems': 'Высокий уровень самоцитирований - может указывать на проблемы',
            
            # Citation timing
            'cited_half_life_explanation': 'Cited Half-Life - период полуцитирования',
            'years': 'лет',
            
            # First citation details
            'first_citation_details': 'Детали первых цитирований',
            'min_days_to_citation': 'Мин. дней до цитирования',
            'max_days_to_citation': 'Макс. дней до цитирования',
            'average_days': 'Среднее дней',
            'median_days': 'Медиана дней',
            
            # Overlaps
            'total_overlaps': 'Всего пересечений',
            'articles_with_overlaps': 'Статей с пересечениями',
            'average_overlaps_per_article': 'Среднее пересечений на статью',
            'overlap_count_distribution': 'Распределение пересечений по количеству',
            'overlap_count': 'Количество пересечений',
            'frequency': 'Частота',
            'overlap_details': 'Детали пересечений',
            
            # Fast metrics additional
            'citation_velocity_details': '**Citation Velocity:**',
            'average_citations_per_year': 'Среднее цитирований/год',
            'articles_with_data': 'Статьи с данными',
            'oa_impact_premium_details': '**OA Impact Premium:**',
            'premium': 'Премия',
            'oa_articles': 'OA статей',
            'non_oa_articles': 'Не-OA статей',
            
            # Concepts and DBI
            'top_5_thematic_concepts': 'Топ-5 тематических концептов',
            'top_thematic_concepts': 'Топ тематических концептов',
            'concept': 'Концепт',
            'mentions': 'Упоминаний',
            'diversity_balance_index': 'Diversity Balance Index (DBI)',
            'current_dbi_value': 'Текущее значение DBI',
            
            # More tooltips
            'more_about_reference_age': 'Подробнее о Reference Age',
            'what_does_it_mean': 'Что это значит?',
            'example': 'Пример',
            'open_access_premium': 'Премия открытого доступа',
            
            # Progress and learning
            'learned_terms': 'Изучено терминов',
            'analysis_starting': 'Запуск анализа...'
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
            'loading_articles': 'Daten werden von',
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
            'oa_premium_positive': '📈 Positive Prämie zeigt, dass Open-Access-Artikel häufiger zitiert werden, was den Wert von OA-Publikationen bestätigt!',
            
            # Additional terms needed
            'language_selection': 'Sprachauswahl',
            'select_language': 'Sprache auswählen:',
            'analysis_starting': 'Analyse wird gestartet...',
            'loaded_articles': '{count} Artikel geladen...',
            'articles_loaded': '{count} Artikel geladen',
            'and': 'und',
            'analysis_may_take_time': 'Die Analyse kann bei einer großen Anzahl analysierter Artikel oder Zitationen lange dauern.',
            'reduce_period_recommended': 'Für "schnelle" Statistiken wird empfohlen, den Analysezeitraum zu verkürzen...',
            'journal_not_found': 'Journal nicht gefunden',
            'failed_create_full_report': 'Erstellung des vollständigen Berichts fehlgeschlagen',
            'try_reduce_data_or_period': 'Versuchen Sie, die Menge der analysierten Daten oder den Analysezeitraum zu reduzieren',
            
            # H-index explanation
            'what_is_h_index': 'Was ist der H-Index und wie wird er interpretiert?',
            
            # Author Gini
            'author_gini_meaning': 'Autor-Gini-Index - was bedeutet das?',
            'current_value': 'Aktueller Wert',
            'interpretation': 'Interpretation',
            
            # International collaboration
            'about_international_collaboration': 'Über internationale Zusammenarbeit',
            'definition': 'Definition',
            'significance_for_science': 'Bedeutung für die Wissenschaft',
            'high_international_articles_indicator': 'Ein hoher Prozentsatz internationaler Artikel weist auf die globale Bedeutung der Zeitschrift und breite internationale Anerkennung hin.',
            
            # JSCR levels
            'jscr_explanation': 'Journal Self-Citation Rate (JSCR)',
            'low_self_citations_excellent': 'Geringe Selbstzitationen - ausgezeichnet!',
            'moderate_self_citations_normal': 'Mäßige Selbstzitationen - normal',
            'elevated_self_citations_attention': 'Erhöhte Selbstzitationen - erfordert Aufmerksamkeit',
            'high_self_citations_problems': 'Hohe Selbstzitationen - kann auf Probleme hinweisen',
            
            # Citation timing
            'cited_half_life_explanation': 'Cited Half-Life - Zitationshalbwertszeit',
            'years': 'Jahre',
            
            # First citation details
            'first_citation_details': 'Erste Zitationsdetails',
            'min_days_to_citation': 'Min. Tage bis Zitation',
            'max_days_to_citation': 'Max. Tage bis Zitation',
            'average_days': 'Durchschnitt Tage',
            'median_days': 'Median Tage',
            
            # Overlaps
            'total_overlaps': 'Gesamtüberschneidungen',
            'articles_with_overlaps': 'Artikel mit Überschneidungen',
            'average_overlaps_per_article': 'Durchschnittliche Überschneidungen pro Artikel',
            'overlap_count_distribution': 'Verteilung der Überschneidungen nach Anzahl',
            'overlap_count': 'Anzahl der Überschneidungen',
            'frequency': 'Häufigkeit',
            'overlap_details': 'Überschneidungsdetails',
            
            # Fast metrics additional
            'citation_velocity_details': '**Zitationsgeschwindigkeit:**',
            'average_citations_per_year': 'Durchschnittliche Zitationen pro Jahr',
            'articles_with_data': 'Artikel mit Daten',
            'oa_impact_premium_details': '**OA-Wirkungsprämie:**',
            'premium': 'Prämie',
            'oa_articles': 'OA-Artikel',
            'non_oa_articles': 'Nicht-OA-Artikel',
            
            # Concepts and DBI
            'top_5_thematic_concepts': 'Top-5 thematische Konzepte',
            'top_thematic_concepts': 'Top thematische Konzepte',
            'concept': 'Konzept',
            'mentions': 'Erwähnungen',
            'diversity_balance_index': 'Diversity Balance Index (DBI)',
            'current_dbi_value': 'Aktueller DBI-Wert',
            
            # More tooltips
            'more_about_reference_age': 'Mehr über Referenzalter',
            'what_does_it_mean': 'Was bedeutet das?',
            'example': 'Beispiel',
            'open_access_premium': 'Open-Access-Prämie',
            
            # Progress and learning
            'learned_terms': 'Gelernte Begriffe',
            'analysis_starting': 'Analyse wird gestartet...'
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
            'loading_articles': 'Cargando datos de',
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
            'oa_premium_positive': '📈 ¡La prima positiva indica que los artículos de acceso abierto se citan con más frecuencia, lo que confirma el valor de las publicaciones OA!',
            
            # Additional terms needed
            'language_selection': 'Selección de Idioma',
            'select_language': 'Seleccione idioma:',
            'analysis_starting': 'Iniciando análisis...',
            'loaded_articles': 'Cargados {count} artículos...',
            'articles_loaded': 'Cargados {count} artículos',
            'and': 'y',
            'analysis_may_take_time': 'El análisis puede tomar mucho tiempo en caso de una gran cantidad de artículos analizados o citas.',
            'reduce_period_recommended': 'Para estadísticas "rápidas", se recomienda reducir el período de análisis...',
            'journal_not_found': 'Revista no encontrada',
            'failed_create_full_report': 'No se pudo crear el informe completo',
            'try_reduce_data_or_period': 'Intente reducir la cantidad de datos analizados o el período de análisis',
            
            # H-index explanation
            'what_is_h_index': '¿Qué es el H-index y cómo interpretarlo?',
            
            # Author Gini
            'author_gini_meaning': 'Índice Gini de Autor - ¿qué significa?',
            'current_value': 'Valor actual',
            'interpretation': 'Interpretación',
            
            # International collaboration
            'about_international_collaboration': 'Sobre la colaboración internacional',
            'definition': 'Definición',
            'significance_for_science': 'Significado para la ciencia',
            'high_international_articles_indicator': 'Un alto porcentaje de artículos internacionales indica la importancia global de la revista y un amplio reconocimiento internacional.',
            
            # JSCR levels
            'jscr_explanation': 'Tasa de Autocitación de Revista (JSCR)',
            'low_self_citations_excellent': 'Bajo nivel de autocitas - ¡excelente!',
            'moderate_self_citations_normal': 'Nivel moderado de autocitas - normal',
            'elevated_self_citations_attention': 'Nivel elevado de autocitas - requiere atención',
            'high_self_citations_problems': 'Alto nivel de autocitas - puede indicar problemas',
            
            # Citation timing
            'cited_half_life_explanation': 'Vida Media de Citación - período de semicitación',
            'years': 'años',
            
            # First citation details
            'first_citation_details': 'Detalles de Primeras Citas',
            'min_days_to_citation': 'Mín. días hasta citación',
            'max_days_to_citation': 'Máx. días hasta citación',
            'average_days': 'Promedio días',
            'median_days': 'Mediana días',
            
            # Overlaps
            'total_overlaps': 'Superposiciones Totales',
            'articles_with_overlaps': 'Artículos con superposiciones',
            'average_overlaps_per_article': 'Superposiciones promedio por artículo',
            'overlap_count_distribution': 'Distribución de superposiciones por cantidad',
            'overlap_count': 'Cantidad de superposiciones',
            'frequency': 'Frecuencia',
            'overlap_details': 'Detalles de superposiciones',
            
            # Fast metrics additional
            'citation_velocity_details': '**Velocidad de Citación:**',
            'average_citations_per_year': 'Citas promedio por año',
            'articles_with_data': 'Artículos con datos',
            'oa_impact_premium_details': '**Prima de Impacto OA:**',
            'premium': 'Prima',
            'oa_articles': 'Artículos OA',
            'non_oa_articles': 'Artículos no OA',
            
            # Concepts and DBI
            'top_5_thematic_concepts': 'Top-5 Conceptos Temáticos',
            'top_thematic_concepts': 'Top conceptos temáticos',
            'concept': 'Concepto',
            'mentions': 'Menciones',
            'diversity_balance_index': 'Índice de Equilibrio de Diversidad (DBI)',
            'current_dbi_value': 'Valor DBI actual',
            
            # More tooltips
            'more_about_reference_age': 'Más sobre Edad de Referencia',
            'what_does_it_mean': '¿Qué significa esto?',
            'example': 'Ejemplo',
            'open_access_premium': 'Prima de Acceso Abierto',
            
            # Progress and learning
            'learned_terms': 'Términos aprendidos',
            'analysis_starting': 'Iniciando análisis...'
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
            'loading_articles': 'Caricamento dati da',
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
            'oa_premium_positive': '📈 Il premio positivo indica che gli articoli ad accesso aperto vengono citati più frequentemente, confermando il valore delle pubblicazioni OA!',
            
            # Additional terms needed
            'language_selection': 'Selezione Lingua',
            'select_language': 'Seleziona lingua:',
            'analysis_starting': 'Avvio analisi...',
            'loaded_articles': 'Caricati {count} articoli...',
            'articles_loaded': 'Caricati {count} articoli',
            'and': 'e',
            'analysis_may_take_time': 'L\'analisi può richiedere molto tempo in caso di un gran numero di articoli analizzati o citazioni.',
            'reduce_period_recommended': 'Per statistiche "veloci", si consiglia di ridurre il periodo di analisi...',
            'journal_not_found': 'Rivista non trovata',
            'failed_create_full_report': 'Creazione report completo fallita',
            'try_reduce_data_or_period': 'Prova a ridurre la quantità di dati analizzati o il periodo di analisi',
            
            # H-index explanation
            'what_is_h_index': 'Cos\'è l\'H-index e come interpretarlo?',
            
            # Author Gini
            'author_gini_meaning': 'Indice Gini Autore - cosa significa?',
            'current_value': 'Valore attuale',
            'interpretation': 'Interpretazione',
            
            # International collaboration
            'about_international_collaboration': 'Sulla collaborazione internazionale',
            'definition': 'Definizione',
            'significance_for_science': 'Significato per la scienza',
            'high_international_articles_indicator': 'Un\'alta percentuale di articoli internazionali indica l\'importanza globale della rivista e un ampio riconoscimento internazionale.',
            
            # JSCR levels
            'jscr_explanation': 'Tasso di Autocitazione Rivista (JSCR)',
            'low_self_citations_excellent': 'Basso livello di autocitazioni - eccellente!',
            'moderate_self_citations_normal': 'Livello moderato di autocitazioni - normale',
            'elevated_self_citations_attention': 'Livello elevato di autocitazioni - richiede attenzione',
            'high_self_citations_problems': 'Alto livello di autocitazioni - può indicare problemi',
            
            # Citation timing
            'cited_half_life_explanation': 'Emivita Citazione - periodo di semicitazione',
            'years': 'anni',
            
            # First citation details
            'first_citation_details': 'Dettagli Prime Citazioni',
            'min_days_to_citation': 'Min. giorni fino citazione',
            'max_days_to_citation': 'Max. giorni fino citazione',
            'average_days': 'Media giorni',
            'median_days': 'Mediana giorni',
            
            # Overlaps
            'total_overlaps': 'Sovrapposizioni Totali',
            'articles_with_overlaps': 'Articoli con sovrapposizioni',
            'average_overlaps_per_article': 'Sovrapposizioni medie per articolo',
            'overlap_count_distribution': 'Distribuzione sovrapposizioni per quantità',
            'overlap_count': 'Quantità di sovrapposizioni',
            'frequency': 'Frequenza',
            'overlap_details': 'Dettagli sovrapposizioni',
            
            # Fast metrics additional
            'citation_velocity_details': '**Velocità di Citazione:**',
            'average_citations_per_year': 'Citazioni medie per anno',
            'articles_with_data': 'Articoli con dati',
            'oa_impact_premium_details': '**Premio Impatto OA:**',
            'premium': 'Premio',
            'oa_articles': 'Articoli OA',
            'non_oa_articles': 'Articoli non OA',
            
            # Concepts and DBI
            'top_5_thematic_concepts': 'Top-5 Concetti Tematici',
            'top_thematic_concepts': 'Top concetti tematici',
            'concept': 'Concetto',
            'mentions': 'Menzioni',
            'diversity_balance_index': 'Indice di Bilanciamento Diversità (DBI)',
            'current_dbi_value': 'Valore DBI attuale',
            
            # More tooltips
            'more_about_reference_age': 'Più sull\'Età di Riferimento',
            'what_does_it_mean': 'Cosa significa?',
            'example': 'Esempio',
            'open_access_premium': 'Premio Accesso Aperto',
            
            # Progress and learning
            'learned_terms': 'Termini imparati',
            'analysis_starting': 'Avvio analisi...'
        }
    
    def _get_arabic_translations(self):
        return {
            # Interface elements
            'app_title': 'Advanced Journal Analysis Tool',
            'analysis_parameters': 'معلمات التحليل',
            'journal_issn': 'رقم ISSN للمجلة:',
            'analysis_period': 'فترة التحليل:',
            'start_analysis': 'بدء التحليل',
            'results': 'النتائج',
            'download_excel_report': 'تحميل تقرير Excel',
            'analysis_results': 'نتائج التحليل',
            'dictionary_of_terms': 'قاموس المصطلحات',
            'select_term_to_learn': 'اختر مصطلح للتعلم:',
            'choose_term': 'اختر مصطلح...',
            'your_progress': 'تقدمك',
            'information': 'معلومات',
            'analysis_capabilities': 'قدرات التحليل',
            'note': 'ملاحظة',
            
            # Analysis capabilities
            'capability_1': '📊 مؤشر H ومقاييس الاقتباس',
            'capability_2': '👥 تحليل المؤلفين والانتماءات', 
            'capability_3': '🌍 التوزيع الجغرافي',
            'capability_4': '🔗 التداخلات بين الأعمال',
            'capability_5': '⏱️ الوقت حتى الاقتباس',
            'capability_6': '📈 تصور البيانات',
            'capability_7': '🚀 مقاييس سريعة بدون API',
            'capability_8': '📚 قاموس مصطلحات تفاعلي',
            
            # Note text
            'note_text_1': 'قد يستغرق التحليل عدة دقائق',
            'note_text_2': 'تأكد من صحة ISSN',
            'note_text_3': 'للفترات الكبيرة، يزيد وقت التحليل',
            'note_text_4': 'هذا البرنامج لا يحسب IF وCiteScore.',
            'note_text_5': '©Chimica Techno Acta, https://chimicatechnoacta.ru / ©developed by daM',
            
            # Results section
            'journal': 'المجلة',
            'period': 'الفترة', 
            'articles_analyzed': 'المقالات التي تم تحليلها',
            'detailed_statistics': 'إحصائيات مفصلة',
            'analyzed_articles': 'المقالات المحللة',
            'citing_works': 'الأعمال التي تستشهد',
            'comparative_analysis': 'التحليل المقارن',
            'fast_metrics': 'المقاييس السريعة',
            
            # Analysis status messages
            'parsing_period': '📅 تحليل الفترة...',
            'getting_journal_name': '📖 جاري الحصول على اسم المجلة...',
            'loading_articles': 'جاري تحميل المقالات من Crossref...',
            'validating_data': '🔍 التحقق من صحة البيانات...',
            'processing_articles': '🔄 معالجة المقالات المحللة...',
            'getting_metadata': 'جاري الحصول على البيانات الوصفية',
            'collecting_citations': '🔗 جمع الأعمال التي تستشهد...',
            'collecting_citations_progress': 'جمع الاقتباسات',
            'calculating_statistics': '📊 حساب الإحصائيات...',
            'calculating_fast_metrics': '🚀 حساب المقاييس السريعة...',
            'creating_report': '💾 إنشاء التقرير...',
            'analysis_complete': '✅ اكتمل التحليل!',
            
            # Success messages
            'journal_found': '📖 المجلة: **{journal_name}** (ISSN: {issn})',
            'articles_found': '📄 تم العثور على المقالات المحللة: **{count}**',
            'unique_citing_works': '📄 الأعمال الفريدة التي تستشهد: **{count}**',
            
            # Error messages
            'issn_required': '❌ أدخل ISSN المجلة',
            'period_required': '❌ أدخل فترة التحليل',
            'no_articles_found': '❌ لم يتم العثور على مقالات.',
            'no_correct_years': '❌ لا توجد سنوات صحيحة.',
            'range_out_of_bounds': '⚠️ النطاق خارج 1900-2100 أو غير صحيح: {part}',
            'range_parsing_error': '⚠️ خطأ في تحليل النطاق: {part}',
            'year_out_of_bounds': '⚠️ السنة خارج 1900-2100: {year}',
            'not_a_year': '⚠️ ليست سنة: {part}',
            'articles_skipped': '⚠️ تم تخطي {count} مقال بسبب مشاكل البيانات',
            'loading_error': 'خطأ في التحميل: {error}',
            
            # Excel report errors
            'excel_creation_error': '❌ خطأ في إنشاء تقرير Excel: {error}',
            'simplified_report_created': '⚠️ تم إنشاء تقرير مبسط بسبب قيود الذاكرة',
            'critical_excel_error': '❌ خطأ حرج في إنشاء التقرير المبسط: {error}',
            
            # Metric labels
            'h_index': 'مؤشر H',
            'total_articles': 'إجمالي المقالات',
            'total_citations': 'إجمالي الاقتباسات',
            'average_citations': 'متوسط الاقتباسات',
            'articles_with_citations': 'المقالات ذات الاقتباسات',
            'self_citations': 'الاقتباسات الذاتية',
            'international_articles': 'المقالات الدولية',
            'unique_affiliations': 'الانتماءات الفريدة',
            'reference_age': 'عمر المرجع',
            'jscr': 'JSCR',
            'cited_half_life': 'نصف عمر الاقتباس',
            'fwci': 'FWCI',
            'citation_velocity': 'سرعة الاقتباس',
            'oa_impact_premium': 'علاوة تأثير OA',
            'elite_index': 'مؤشر النخبة',
            'author_gini': 'جيني المؤلف',
            
            # Tooltips and explanations
            'h_index_tooltip': 'مؤشر يوضح عدد المقالات h التي تلقت على الأقل h اقتباس',
            'total_articles_tooltip': 'إجمالي عدد المقالات التي تم تحليلها',
            'total_citations_tooltip': 'إجمالي عدد اقتباسات جميع مقالات المجلة',
            'average_citations_tooltip': 'متوسط عدد الاقتباسات لكل مقال',
            'articles_with_citations_tooltip': 'عدد المقالات التي تم اقتباسها مرة واحدة على الأقل',
            'self_citations_tooltip': 'المراجع لمقالات أخرى من نفس المجلة في الفهرس',
            'international_articles_tooltip': 'نسبة المقالات بمؤلفين من دول مختلفة',
            'unique_affiliations_tooltip': 'عدد المنظمات العلمية الفريدة الممثلة في المجلة',
            
            # Dictionary terms
            'learned_term_toast': '📖 لقد تعلمت المصطلح: {term}',
            'term_understood': '✅ لقد فهمت هذا المصطلح!',
            'term_added_success': '🎉 ممتاز! تمت إضافة المصطلح "{term}" إلى مجموعة معرفتك!',
            'progress_great': '🏆 نتيجة ممتازة! لقد تعلمت {count} مصطلحات!',
            'progress_good': '📚 بداية جيدة! استمر في تعلم المصطلحات.',
            
            # Fast metrics details
            'reference_age_details': '**عمر المرجع:**',
            'reference_age_median': '- الوسيط: {value} سنة',
            'reference_age_mean': '- المتوسط: {value} سنة',
            'reference_age_percentile': '- النسبة المئوية 25-75: {value} سنة',
            'reference_age_analyzed': '- المراجع التي تم تحليلها: {value}',
            'jscr_details': '**معدل الاقتباس الذاتي للمجلة:**',
            'jscr_self_cites': '- الاقتباسات الذاتية: {value}',
            'jscr_total_cites': '- إجمالي الاقتباسات: {value}',
            'jscr_percentage': '- النسبة المئوية: {value}%',
            'fwci_details': '**تأثير الاقتباس المرجح حسب المجال:**',
            'fwci_value': '- FWCI: {value}',
            'fwci_total_cites': '- إجمالي الاقتباسات: {value}',
            'fwci_expected_cites': '- الاقتباسات المتوقعة: {value}',
            'dbi_details': '**مؤشر توازن التنوع:**',
            'dbi_value': '- DBI: {value}',
            'dbi_unique_concepts': '- المفاهيم الفريدة: {value}',
            'dbi_total_mentions': '- إجمالي الذكر: {value}',
            
            # Visualization tabs
            'tab_main_metrics': '📈 المقاييس الرئيسية',
            'tab_authors_organizations': '👥 المؤلفون والمنظمات', 
            'tab_geography': '🌍 الجغرافيا',
            'tab_citations': '📊 الاقتباسات',
            'tab_overlaps': '🔀 التداخلات',
            'tab_citation_timing': '⏱️ توقيت الاقتباس',
            'tab_fast_metrics': '🚀 المقاييس السريعة',
            
            # Analysis details
            'total_references': 'إجمالي المراجع',
            'single_author_articles': 'مقالات المؤلف الواحد',
            'international_collaboration': 'التعاون الدولي',
            'unique_countries': 'الدول الفريدة',
            'articles_10_citations': 'المقالات ذات ≥10 اقتباسات',
            'unique_journals': 'المجلات الفريدة',
            'unique_publishers': 'الناشرون الفريدون',
            'average_authors_per_article': 'متوسط المؤلفين لكل مقال',
            'average_references_per_article': 'متوسط المراجع لكل مقال',
            
            # No data messages
            'no_overlaps_found': '❌ لم يتم العثور على تداخلات بين الأعمال المحللة والمستشهدة',
            'no_data_for_report': 'لا توجد بيانات للتقرير',
            
            # Open access premium message
            'oa_premium_positive': '📈 تشير العلاوة الإيجابية إلى أن مقالات الوصول المفتوح يتم اقتباسها بشكل متكرر، مما يؤكد قيمة منشورات OA!',
            
            # Additional terms needed
            'language_selection': 'اختيار اللغة',
            'select_language': 'اختر اللغة:',
            'analysis_starting': 'بدء التحليل...',
            'loaded_articles': 'تم تحميل {count} مقال...',
            'articles_loaded': 'تم تحميل {count} مقال',
            'and': 'و',
            'analysis_may_take_time': 'قد يستغرق التحليل وقتًا طويلاً في حالة وجود عدد كبير من المقالات المحللة أو الاقتباسات.',
            'reduce_period_recommended': 'للحصول على إحصائيات "سريعة"، يوصى بتقليل فترة التحليل...',
            'journal_not_found': 'المجلة غير موجودة',
            'failed_create_full_report': 'فشل في إنشاء التقرير الكامل',
            'try_reduce_data_or_period': 'حاول تقليل كمية البيانات التي تم تحليلها أو فترة التحليل',
            
            # H-index explanation
            'what_is_h_index': 'ما هو مؤشر H وكيفية تفسيره؟',
            
            # Author Gini
            'author_gini_meaning': 'مؤشر جيني المؤلف - ماذا يعني؟',
            'current_value': 'القيمة الحالية',
            'interpretation': 'التفسير',
            
            # International collaboration
            'about_international_collaboration': 'حول التعاون الدولي',
            'definition': 'التعريف',
            'significance_for_science': 'الأهمية للعلوم',
            'high_international_articles_indicator': 'تشير النسبة المئوية العالية للمقالات الدولية إلى الأهمية العالمية للمجلة والاعتراف الدولي الواسع.',
            
            # JSCR levels
            'jscr_explanation': 'معدل الاقتباس الذاتي للمجلة (JSCR)',
            'low_self_citations_excellent': 'مستوى منخفض من الاقتباسات الذاتية - ممتاز!',
            'moderate_self_citations_normal': 'مستوى معتدل من الاقتباسات الذاتية - طبيعي',
            'elevated_self_citations_attention': 'مستوى مرتفع من الاقتباسات الذاتية - يتطلب اهتمامًا',
            'high_self_citations_problems': 'مستوى عالٍ من الاقتباسات الذاتية - قد يشير إلى مشاكل',
            
            # Citation timing
            'cited_half_life_explanation': 'نصف عمر الاقتباس - فترة نصف الاقتباس',
            'years': 'سنوات',
            
            # First citation details
            'first_citation_details': 'تفاصيل الاقتباسات الأولى',
            'min_days_to_citation': 'الحد الأدنى للأيام حتى الاقتباس',
            'max_days_to_citation': 'الحد الأقصى للأيام حتى الاقتباس',
            'average_days': 'متوسط الأيام',
            'median_days': 'وسيط الأيام',
            
            # Overlaps
            'total_overlaps': 'إجمالي التداخلات',
            'articles_with_overlaps': 'المقالات ذات التداخلات',
            'average_overlaps_per_article': 'متوسط التداخلات لكل مقال',
            'overlap_count_distribution': 'توزيع عدد التداخلات',
            'overlap_count': 'عدد التداخلات',
            'frequency': 'التكرار',
            'overlap_details': 'تفاصيل التداخلات',
            
            # Fast metrics additional
            'citation_velocity_details': '**سرعة الاقتباس:**',
            'average_citations_per_year': 'متوسط الاقتباسات سنويًا',
            'articles_with_data': 'المقالات ذات البيانات',
            'oa_impact_premium_details': '**علاوة تأثير OA:**',
            'premium': 'العلاوة',
            'oa_articles': 'مقالات OA',
            'non_oa_articles': 'مقالات غير OA',
            
            # Concepts and DBI
            'top_5_thematic_concepts': 'أفضل 5 مفاهيم موضوعية',
            'top_thematic_concepts': 'أفضل المفاهيم الموضوعية',
            'concept': 'المفهوم',
            'mentions': 'الذكر',
            'diversity_balance_index': 'مؤشر توازن التنوع (DBI)',
            'current_dbi_value': 'قيمة DBI الحالية',
            
            # More tooltips
            'more_about_reference_age': 'المزيد عن عمر المرجع',
            'what_does_it_mean': 'ماذا يعني هذا؟',
            'example': 'مثال',
            'open_access_premium': 'علاوة الوصول المفتوح',
            
            # Progress and learning
            'learned_terms': 'المصطلحات التي تم تعلمها',
            'analysis_starting': 'بدء التحليل...'
        }
    
    def _get_chinese_translations(self):
        return {
            # Interface elements
            'app_title': 'Advanced Journal Analysis Tool',
            'analysis_parameters': '分析参数',
            'journal_issn': '期刊 ISSN:',
            'analysis_period': '分析期间:',
            'start_analysis': '开始分析',
            'results': '结果',
            'download_excel_report': '下载 Excel 报告',
            'analysis_results': '分析结果',
            'dictionary_of_terms': '术语词典',
            'select_term_to_learn': '选择要学习的术语:',
            'choose_term': '选择术语...',
            'your_progress': '您的进度',
            'information': '信息',
            'analysis_capabilities': '分析能力',
            'note': '注意',
            
            # Analysis capabilities
            'capability_1': '📊 H指数和引文指标',
            'capability_2': '👥 作者和隶属关系分析', 
            'capability_3': '🌍 地理分布',
            'capability_4': '🔗 工作之间的重叠',
            'capability_5': '⏱️ 引用时间',
            'capability_6': '📈 数据可视化',
            'capability_7': '🚀 无需API的快速指标',
            'capability_8': '📚 交互式术语词典',
            
            # Note text
            'note_text_1': '分析可能需要几分钟',
            'note_text_2': '确保ISSN正确',
            'note_text_3': '对于大时间段，分析时间会增加',
            'note_text_4': '此程序不计算IF和CiteScore。',
            'note_text_5': '©Chimica Techno Acta, https://chimicatechnoacta.ru / ©developed by daM',
            
            # Results section
            'journal': '期刊',
            'period': '期间', 
            'articles_analyzed': '已分析文章',
            'detailed_statistics': '详细统计',
            'analyzed_articles': '已分析文章',
            'citing_works': '引用作品',
            'comparative_analysis': '比较分析',
            'fast_metrics': '快速指标',
            
            # Analysis status messages
            'parsing_period': '📅 解析期间...',
            'getting_journal_name': '📖 获取期刊名称...',
            'loading_articles': '从Crossref加载文章...',
            'validating_data': '🔍 验证数据...',
            'processing_articles': '🔄 处理已分析文章...',
            'getting_metadata': '获取元数据',
            'collecting_citations': '🔗 收集引用作品...',
            'collecting_citations_progress': '收集引用',
            'calculating_statistics': '📊 计算统计...',
            'calculating_fast_metrics': '🚀 计算快速指标...',
            'creating_report': '💾 创建报告...',
            'analysis_complete': '✅ 分析完成!',
            
            # Success messages
            'journal_found': '📖 期刊: **{journal_name}** (ISSN: {issn})',
            'articles_found': '📄 找到已分析文章: **{count}**',
            'unique_citing_works': '📄 独特引用作品: **{count}**',
            
            # Error messages
            'issn_required': '❌ 输入期刊ISSN',
            'period_required': '❌ 输入分析期间',
            'no_articles_found': '❌ 未找到文章。',
            'no_correct_years': '❌ 没有正确的年份。',
            'range_out_of_bounds': '⚠️ 范围超出1900-2100或不正确: {part}',
            'range_parsing_error': '⚠️ 范围解析错误: {part}',
            'year_out_of_bounds': '⚠️ 年份超出1900-2100: {year}',
            'not_a_year': '⚠️ 不是年份: {part}',
            'articles_skipped': '⚠️ 由于数据问题跳过了 {count} 篇文章',
            'loading_error': '加载错误: {error}',
            
            # Excel report errors
            'excel_creation_error': '❌ 创建Excel报告错误: {error}',
            'simplified_report_created': '⚠️ 由于内存限制创建了简化报告',
            'critical_excel_error': '❌ 创建简化报告时出现严重错误: {error}',
            
            # Metric labels
            'h_index': 'H指数',
            'total_articles': '总文章数',
            'total_citations': '总引用数',
            'average_citations': '平均引用数',
            'articles_with_citations': '有引用的文章',
            'self_citations': '自引',
            'international_articles': '国际文章',
            'unique_affiliations': '独特隶属关系',
            'reference_age': '参考文献年龄',
            'jscr': 'JSCR',
            'cited_half_life': '引用半衰期',
            'fwci': 'FWCI',
            'citation_velocity': '引用速度',
            'oa_impact_premium': 'OA影响溢价',
            'elite_index': '精英指数',
            'author_gini': '作者基尼系数',
            
            # Tooltips and explanations
            'h_index_tooltip': '显示至少有h次引用的h篇文章数量的指数',
            'total_articles_tooltip': '已分析文章总数',
            'total_citations_tooltip': '期刊所有文章的总引用数',
            'average_citations_tooltip': '每篇文章的平均引用数',
            'articles_with_citations_tooltip': '至少被引用一次的文章数量',
            'self_citations_tooltip': '参考文献中引用同一期刊其他文章',
            'international_articles_tooltip': '来自不同国家作者的文章百分比',
            'unique_affiliations_tooltip': '期刊中代表的独特科学组织数量',
            
            # Dictionary terms
            'learned_term_toast': '📖 您学习了术语: {term}',
            'term_understood': '✅ 我理解了这个术语!',
            'term_added_success': '🎉 优秀! 术语"{term}"已添加到您的知识收藏中!',
            'progress_great': '🏆 优秀结果! 您学习了 {count} 个术语!',
            'progress_good': '📚 良好的开始! 继续学习术语。',
            
            # Fast metrics details
            'reference_age_details': '**参考文献年龄:**',
            'reference_age_median': '- 中位数: {value} 年',
            'reference_age_mean': '- 平均值: {value} 年',
            'reference_age_percentile': '- 25-75百分位: {value} 年',
            'reference_age_analyzed': '- 已分析参考文献: {value}',
            'jscr_details': '**期刊自引率:**',
            'jscr_self_cites': '- 自引: {value}',
            'jscr_total_cites': '- 总引用: {value}',
            'jscr_percentage': '- 百分比: {value}%',
            'fwci_details': '**领域加权引用影响:**',
            'fwci_value': '- FWCI: {value}',
            'fwci_total_cites': '- 总引用: {value}',
            'fwci_expected_cites': '- 预期引用: {value}',
            'dbi_details': '**多样性平衡指数:**',
            'dbi_value': '- DBI: {value}',
            'dbi_unique_concepts': '- 独特概念: {value}',
            'dbi_total_mentions': '- 总提及: {value}',
            
            # Visualization tabs
            'tab_main_metrics': '📈 主要指标',
            'tab_authors_organizations': '👥 作者和组织', 
            'tab_geography': '🌍 地理',
            'tab_citations': '📊 引用',
            'tab_overlaps': '🔀 重叠',
            'tab_citation_timing': '⏱️ 引用时间',
            'tab_fast_metrics': '🚀 快速指标',
            
            # Analysis details
            'total_references': '总参考文献',
            'single_author_articles': '单作者文章',
            'international_collaboration': '国际合作',
            'unique_countries': '独特国家',
            'articles_10_citations': '有≥10次引用的文章',
            'unique_journals': '独特期刊',
            'unique_publishers': '独特出版商',
            'average_authors_per_article': '每篇文章平均作者数',
            'average_references_per_article': '每篇文章平均参考文献数',
            
            # No data messages
            'no_overlaps_found': '❌ 未找到已分析作品和引用作品之间的重叠',
            'no_data_for_report': '没有报告数据',
            
            # Open access premium message
            'oa_premium_positive': '📈 正溢价表明开放获取文章被更频繁地引用，证实了OA出版物的价值!',
            
            # Additional terms needed
            'language_selection': '语言选择',
            'select_language': '选择语言:',
            'analysis_starting': '开始分析...',
            'loaded_articles': '已加载 {count} 篇文章...',
            'articles_loaded': '已加载 {count} 篇文章',
            'and': '和',
            'analysis_may_take_time': '在分析大量文章或引用的情况下，分析可能需要很长时间。',
            'reduce_period_recommended': '对于"快速"统计，建议减少分析期间...',
            'journal_not_found': '未找到期刊',
            'failed_create_full_report': '创建完整报告失败',
            'try_reduce_data_or_period': '尝试减少分析数据量或分析期间',
            
            # H-index explanation
            'what_is_h_index': '什么是H指数以及如何解释它？',
            
            # Author Gini
            'author_gini_meaning': '作者基尼系数 - 这意味着什么？',
            'current_value': '当前值',
            'interpretation': '解释',
            
            # International collaboration
            'about_international_collaboration': '关于国际合作',
            'definition': '定义',
            'significance_for_science': '对科学的意义',
            'high_international_articles_indicator': '高比例的国际文章表明期刊的全球重要性和广泛的国际认可。',
            
            # JSCR levels
            'jscr_explanation': '期刊自引率 (JSCR)',
            'low_self_citations_excellent': '低自引水平 - 优秀!',
            'moderate_self_citations_normal': '中等自引水平 - 正常',
            'elevated_self_citations_attention': '较高的自引水平 - 需要注意',
            'high_self_citations_problems': '高自引水平 - 可能表明问题',
            
            # Citation timing
            'cited_half_life_explanation': '引用半衰期 - 半引用期',
            'years': '年',
            
            # First citation details
            'first_citation_details': '首次引用详情',
            'min_days_to_citation': '最小引用天数',
            'max_days_to_citation': '最大引用天数',
            'average_days': '平均天数',
            'median_days': '中位数天数',
            
            # Overlaps
            'total_overlaps': '总重叠数',
            'articles_with_overlaps': '有重叠的文章',
            'average_overlaps_per_article': '每篇文章平均重叠数',
            'overlap_count_distribution': '重叠数量分布',
            'overlap_count': '重叠数量',
            'frequency': '频率',
            'overlap_details': '重叠详情',
            
            # Fast metrics additional
            'citation_velocity_details': '**引用速度:**',
            'average_citations_per_year': '年平均引用数',
            'articles_with_data': '有数据的文章',
            'oa_impact_premium_details': '**OA影响溢价:**',
            'premium': '溢价',
            'oa_articles': 'OA文章',
            'non_oa_articles': '非OA文章',
            
            # Concepts and DBI
            'top_5_thematic_concepts': '前5个主题概念',
            'top_thematic_concepts': '热门主题概念',
            'concept': '概念',
            'mentions': '提及',
            'diversity_balance_index': '多样性平衡指数 (DBI)',
            'current_dbi_value': '当前DBI值',
            
            # More tooltips
            'more_about_reference_age': '更多关于参考文献年龄',
            'what_does_it_mean': '这意味着什么？',
            'example': '示例',
            'open_access_premium': '开放获取溢价',
            
            # Progress and learning
            'learned_terms': '已学习术语',
            'analysis_starting': '开始分析...'
        }
    
    def _get_japanese_translations(self):
        return {
            # Interface elements
            'app_title': 'Advanced Journal Analysis Tool',
            'analysis_parameters': '分析パラメータ',
            'journal_issn': 'ジャーナル ISSN:',
            'analysis_period': '分析期間:',
            'start_analysis': '分析開始',
            'results': '結果',
            'download_excel_report': 'Excelレポートをダウンロード',
            'analysis_results': '分析結果',
            'dictionary_of_terms': '用語辞典',
            'select_term_to_learn': '学習する用語を選択:',
            'choose_term': '用語を選択...',
            'your_progress': 'あなたの進捗',
            'information': '情報',
            'analysis_capabilities': '分析機能',
            'note': '注意',
            
            # Analysis capabilities
            'capability_1': '📊 H指数と被引用指標',
            'capability_2': '👥 著者と所属の分析', 
            'capability_3': '🌍 地理的分布',
            'capability_4': '🔗 作品間の重複',
            'capability_5': '⏱️ 引用までの時間',
            'capability_6': '📈 データ可視化',
            'capability_7': '🚀 API不要の高速指標',
            'capability_8': '📚 インタラクティブ用語辞典',
            
            # Note text
            'note_text_1': '分析には数分かかる場合があります',
            'note_text_2': 'ISSNが正しいことを確認してください',
            'note_text_3': '期間が長い場合、分析時間が増加します',
            'note_text_4': 'このプログラムはIFとCiteScoreを計算しません。',
            'note_text_5': '©Chimica Techno Acta, https://chimicatechnoacta.ru / ©developed by daM',
            
            # Results section
            'journal': 'ジャーナル',
            'period': '期間', 
            'articles_analyzed': '分析された記事',
            'detailed_statistics': '詳細統計',
            'analyzed_articles': '分析された記事',
            'citing_works': '引用作品',
            'comparative_analysis': '比較分析',
            'fast_metrics': '高速指標',
            
            # Analysis status messages
            'parsing_period': '📅 期間の解析...',
            'getting_journal_name': '📖 ジャーナル名の取得...',
            'loading_articles': 'Crossrefから記事を読み込み中...',
            'validating_data': '🔍 データの検証...',
            'processing_articles': '🔄 分析記事の処理...',
            'getting_metadata': 'メタデータの取得',
            'collecting_citations': '🔗 引用作品の収集...',
            'collecting_citations_progress': '引用の収集',
            'calculating_statistics': '📊 統計の計算...',
            'calculating_fast_metrics': '🚀 高速指標の計算...',
            'creating_report': '💾 レポートの作成...',
            'analysis_complete': '✅ 分析完了!',
            
            # Success messages
            'journal_found': '📖 ジャーナル: **{journal_name}** (ISSN: {issn})',
            'articles_found': '📄 分析された記事が見つかりました: **{count}**',
            'unique_citing_works': '📄 ユニークな引用作品: **{count}**',
            
            # Error messages
            'issn_required': '❌ ジャーナルISSNを入力してください',
            'period_required': '❌ 分析期間を入力してください',
            'no_articles_found': '❌ 記事が見つかりませんでした。',
            'no_correct_years': '❌ 正しい年がありません。',
            'range_out_of_bounds': '⚠️ 1900-2100の範囲外または不正: {part}',
            'range_parsing_error': '⚠️ 範囲解析エラー: {part}',
            'year_out_of_bounds': '⚠️ 1900-2100の範囲外の年: {year}',
            'not_a_year': '⚠️ 年ではありません: {part}',
            'articles_skipped': '⚠️ データの問題で {count} 記事をスキップしました',
            'loading_error': '読み込みエラー: {error}',
            
            # Excel report errors
            'excel_creation_error': '❌ Excelレポート作成エラー: {error}',
            'simplified_report_created': '⚠️ メモリ制限のため簡略化レポートを作成',
            'critical_excel_error': '❌ 簡略化レポート作成中の重大なエラー: {error}',
            
            # Metric labels
            'h_index': 'H指数',
            'total_articles': '総記事数',
            'total_citations': '総被引用数',
            'average_citations': '平均被引用数',
            'articles_with_citations': '引用のある記事',
            'self_citations': '自己引用',
            'international_articles': '国際記事',
            'unique_affiliations': 'ユニーク所属',
            'reference_age': '参考文献年齢',
            'jscr': 'JSCR',
            'cited_half_life': '被引用半減期',
            'fwci': 'FWCI',
            'citation_velocity': '引用速度',
            'oa_impact_premium': 'OA影響プレミアム',
            'elite_index': 'エリート指数',
            'author_gini': '著者ジニ係数',
            
            # Tooltips and explanations
            'h_index_tooltip': '少なくともh回引用されたh本の論文数を示す指数',
            'total_articles_tooltip': '分析された記事の総数',
            'total_citations_tooltip': 'ジャーナル全記事の総被引用数',
            'average_citations_tooltip': '1記事あたりの平均被引用数',
            'articles_with_citations_tooltip': '少なくとも1回引用された記事数',
            'self_citations_tooltip': '参考文献内の同じジャーナルの他の論文への参照',
            'international_articles_tooltip': '異なる国の著者による記事の割合',
            'unique_affiliations_tooltip': 'ジャーナルに代表されるユニークな科学組織の数',
            
            # Dictionary terms
            'learned_term_toast': '📖 用語を学習しました: {term}',
            'term_understood': '✅ この用語を理解しました!',
            'term_added_success': '🎉 優秀! 用語"{term}"が知識コレクションに追加されました!',
            'progress_great': '🏆 優秀な結果! {count} 個の用語を学習しました!',
            'progress_good': '📚 良いスタート! 引き続き用語を学習してください。',
            
            # Fast metrics details
            'reference_age_details': '**参考文献年齢:**',
            'reference_age_median': '- 中央値: {value} 年',
            'reference_age_mean': '- 平均: {value} 年',
            'reference_age_percentile': '- 25-75パーセンタイル: {value} 年',
            'reference_age_analyzed': '- 分析された参考文献: {value}',
            'jscr_details': '**ジャーナル自己引用率:**',
            'jscr_self_cites': '- 自己引用: {value}',
            'jscr_total_cites': '- 総引用: {value}',
            'jscr_percentage': '- 割合: {value}%',
            'fwci_details': '**分野加重被引用影響:**',
            'fwci_value': '- FWCI: {value}',
            'fwci_total_cites': '- 総引用: {value}',
            'fwci_expected_cites': '- 期待引用: {value}',
            'dbi_details': '**多様性バランス指数:**',
            'dbi_value': '- DBI: {value}',
            'dbi_unique_concepts': '- ユニーク概念: {value}',
            'dbi_total_mentions': '- 総言及: {value}',
            
            # Visualization tabs
            'tab_main_metrics': '📈 主要指標',
            'tab_authors_organizations': '👥 著者と組織', 
            'tab_geography': '🌍 地理',
            'tab_citations': '📊 引用',
            'tab_overlaps': '🔀 重複',
            'tab_citation_timing': '⏱️ 引用タイミング',
            'tab_fast_metrics': '🚀 高速指標',
            
            # Analysis details
            'total_references': '総参考文献',
            'single_author_articles': '単独著者記事',
            'international_collaboration': '国際協力',
            'unique_countries': 'ユニーク国',
            'articles_10_citations': '被引用数≥10の記事',
            'unique_journals': 'ユニークジャーナル',
            'unique_publishers': 'ユニーク出版社',
            'average_authors_per_article': '1記事あたりの平均著者数',
            'average_references_per_article': '1記事あたりの平均参考文献数',
            
            # No data messages
            'no_overlaps_found': '❌ 分析作品と引用作品の間に重複は見つかりませんでした',
            'no_data_for_report': 'レポートデータなし',
            
            # Open access premium message
            'oa_premium_positive': '📈 正のプレミアムは、オープンアクセス記事がより頻繁に引用されていることを示し、OA出版物の価値を確認します!',
            
            # Additional terms needed
            'language_selection': '言語選択',
            'select_language': '言語を選択:',
            'analysis_starting': '分析を開始...',
            'loaded_articles': '{count} 記事を読み込みました...',
            'articles_loaded': '{count} 記事を読み込みました',
            'and': 'と',
            'analysis_may_take_time': '分析対象の記事数や引用数が多い場合、分析に時間がかかる可能性があります。',
            'reduce_period_recommended': '「高速」統計を得るには、分析期間を短縮することをお勧めします...',
            'journal_not_found': 'ジャーナルが見つかりません',
            'failed_create_full_report': '完全なレポートの作成に失敗しました',
            'try_reduce_data_or_period': '分析データ量または分析期間を減らしてみてください',
            
            # H-index explanation
            'what_is_h_index': 'H指数とは何か、どのように解釈するか？',
            
            # Author Gini
            'author_gini_meaning': '著者ジニ係数 - これは何を意味しますか？',
            'current_value': '現在の値',
            'interpretation': '解釈',
            
            # International collaboration
            'about_international_collaboration': '国際協力について',
            'definition': '定義',
            'significance_for_science': '科学への重要性',
            'high_international_articles_indicator': '国際記事の割合が高いことは、ジャーナルの世界的な重要性と広範な国際的認知を示しています。',
            
            # JSCR levels
            'jscr_explanation': 'ジャーナル自己引用率 (JSCR)',
            'low_self_citations_excellent': '低い自己引用レベル - 優秀!',
            'moderate_self_citations_normal': '適度な自己引用レベル - 正常',
            'elevated_self_citations_attention': '高い自己引用レベル - 注意が必要',
            'high_self_citations_problems': '高い自己引用レベル - 問題を示す可能性あり',
            
            # Citation timing
            'cited_half_life_explanation': '被引用半減期 - 半引用期間',
            'years': '年',
            
            # First citation details
            'first_citation_details': '最初の引用詳細',
            'min_days_to_citation': '最小引用日数',
            'max_days_to_citation': '最大引用日数',
            'average_days': '平均日数',
            'median_days': '中央値日数',
            
            # Overlaps
            'total_overlaps': '総重複数',
            'articles_with_overlaps': '重複のある記事',
            'average_overlaps_per_article': '1記事あたりの平均重複数',
            'overlap_count_distribution': '重複数の分布',
            'overlap_count': '重複数',
            'frequency': '頻度',
            'overlap_details': '重複詳細',
            
            # Fast metrics additional
            'citation_velocity_details': '**引用速度:**',
            'average_citations_per_year': '年平均引用数',
            'articles_with_data': 'データのある記事',
            'oa_impact_premium_details': '**OA影響プレミアム:**',
            'premium': 'プレミアム',
            'oa_articles': 'OA記事',
            'non_oa_articles': '非OA記事',
            
            # Concepts and DBI
            'top_5_thematic_concepts': 'トップ5テーマ概念',
            'top_thematic_concepts': 'トップテーマ概念',
            'concept': '概念',
            'mentions': '言及',
            'diversity_balance_index': '多様性バランス指数 (DBI)',
            'current_dbi_value': '現在のDBI値',
            
            # More tooltips
            'more_about_reference_age': '参考文献年齢について詳しく',
            'what_does_it_mean': 'これは何を意味しますか？',
            'example': '例',
            'open_access_premium': 'オープンアクセスプレミアム',
            
            # Progress and learning
            'learned_terms': '学習した用語',
            'analysis_starting': '分析を開始...'
        }

# Global translation manager instance
translation_manager = TranslationManager()


