import math
from collections import defaultdict

import API
from scipy.stats import norm
class DiagnosticCalculator:
    """
    Класс для расчета диагностических показателей на основе метрик пациента.
    Выполняет расчет Z-оценок, процентилей, интегральных индексов и диагностических выводов.
    """

    def __init__(self):
        # self.patient_id = patient_id
        self._z_scores_cache = {}  # Кэш Z-оценок по metric_id
        self._deltas_cache = {}
        self._percentiles_cache = {}  # Кэш процентилей по metric_id
        self._idx_cache = {}  # Кэш интегральных индексов по disease_id

    def calculate_all(self, metrics_values, patient_id):
        """
        Основной метод расчета всех диагностических показателей.
        """
        # Получаем необходимые данные из API
        reference_data = self._fetch_reference_data(patient_id)
        weights = self._fetch_weights(metrics_values)
        thresholds = self._fetch_thresholds(weights)

        # Объединяем данные метрик со справочными данными
        metric_data = self._merge_metric_with_reference(metrics_values, reference_data)

        # Рассчитываем Z-оценки и процентили
        percentile_results = self._calculate_z_scores_and_percentiles(metric_data)

        # Рассчитываем интегральные индексы
        Idxs = self._calculate_integral_indexes(weights, percentile_results)

        # Формируем диагностические выводы
        conclusions = self._form_diagnostic_conclusions(Idxs, thresholds)

        # Получаем названия метрик и заболеваний
        enriched_results = self._enrich_results_with_names(percentile_results, conclusions)

        return enriched_results

    def _fetch_reference_data(self, patient_id):
        """Получение справочных данных (p50, s) для пациента"""
        return API.get_row_data("reference_data", patient_id)["info"]

    def _fetch_weights(self, metrics_values):
        """Получение весов метрик для заболеваний"""
        metric_ids = [item['metric_id'] for item in metrics_values]
        return API.get_row_data("weights", metric_ids)["info"]

    def _fetch_thresholds(self, weights):
        """Получение пороговых значений для заболеваний"""
        disease_ids = list(set(item['disease_id'] for item in weights))  # Убираем дубликаты
        return API.get_row_data("thresholds", disease_ids)["info"]

    def _merge_metric_with_reference(self, metrics_values, reference_data):
        """
        Объединение данных метрик со справочными данными.

        Args:
            metrics_values: Список значений метрик пациента
            reference_data: Справочные данные (p50, s)

        Returns:
            list: Объединенные данные
        """
        # Создаем словарь для быстрого поиска справочных данных по metric_id
        ref_dict = {ref['metric_id']: ref for ref in reference_data}
        merged_data = []

        for metric in metrics_values:
            metric_id = metric['metric_id']
            if metric_id in ref_dict:
                merged_item = {
                    **metric,
                    **ref_dict[metric_id]
                }
                merged_data.append(merged_item)

        return merged_data

    def _calculate_z_scores_and_percentiles(self, metric_data):
        """
        Расчет Z-оценок и процентилей для каждой метрики.

        Args:
            metric_data: Объединенные данные метрик

        Returns:
            list: Результаты с процентилями и Z-оценками
        """
        percentile_results = []

        for data in metric_data:
            try:
                # Извлекаем значения
                N = float(data['metric'])
                p50 = float(data['p50'])
                p5 = float(data['p5'])
                p95 = float(data['p95'])
                s = float(data['s'])
                metric_id = data['metric_id']

                # Расчет Z-оценки
                Z = (N - p50) / s
                deltas = {
                    "d-": max(0.0, Z*(-1)),
                    "d+": max(0.0, Z)
                }
                # Кэшируем Z-оценку
                self._z_scores_cache[metric_id] = deltas
                # self._deltas_cache[metric_id] = deltas

                # Расчет процентиля
                #P = norm.cdf(Z) * 100
                P =self._calculate_normality_percentile(N, p5, p50, p95)

                # Кэшируем процентиль
                self._percentiles_cache[metric_id] = P

                percentile_results.append({
                    "P": P,
                    "metric_id": metric_id,
                    "Z": Z,  # Сохраняем Z для возможного дальнейшего использования,
                    "deltas": deltas
                })

            except (ValueError, ZeroDivisionError) as e:
                print(f"Ошибка расчета для метрики {data.get('name', 'unknown')}: {e}")
                continue

        return percentile_results

    def _calculate_normality_percentile(self, value, p5, p50, p95):
        """
        Расчет процентиля нормальности (0-100%).

        Где:
        - 100% = идеальное значение (p50)
        - 50% = на границе нормы (p5 или p95)
        - <50% = отклонение за пределы нормы

        Args:
            value: Значение метрики пациента
            p5: 5-й перцентиль
            p50: 50-й перцентиль (медиана)
            p95: 95-й перцентиль

        Returns:
            float: Процентиль нормальности (0-100)
        """
        # Если значение ниже p5 (ниже нормы)
        if value <= p5:
            # Линейная интерполяция от 0 до 50%
            # Предполагаем, что минимальное возможное значение = 0
            min_val = 0
            if p5 > 0:
                return 50 * (value / p5)
            else:
                return 0

        # Если значение между p5 и p50
        elif value <= p50:
            # Линейная интерполяция от 50% до 100%
            return 50 + 50 * ((value - p5) / (p50 - p5))

        # Если значение между p50 и p95
        elif value <= p95:
            # Линейная интерполяция от 100% до 50%
            return 100 - 50 * ((value - p50) / (p95 - p50))

        # Если значение выше p95 (выше нормы)
        else:
            # Линейная экстраполяция за пределы нормы
            # Предполагаем, что максимальное значение = 2 * p95
            max_val = 2 * p95
            if max_val > p95:
                return 50 * (p95 / value)
            else:
                return 0
    def _calculate_integral_indexes(self, weights, percentile_results):
        """
        Расчет интегральных индексов (Idx) для заболеваний.

        Args:
            weights: Веса метрик для заболеваний
            percentile_results: Результаты с процентилями

        Returns:
            list: Интегральные индексы по заболеваниям
        """
        # Создаем словарь для быстрого доступа к Z-оценкам
        z_dict = {item['metric_id']: item['deltas'] for item in percentile_results}

        grouped_weights = defaultdict(list)
        for item in weights:
            grouped_weights[item['disease_id']].append(item)

        # Convert to regular dict if needed
        grouped_weights = dict(grouped_weights)

        grouped_by_disease = defaultdict(list)
        for item in weights:
            grouped_by_disease[item['disease_id']].append(item)

        # Now loop through each disease group
        idxs_dict = {}
        for disease_id, metrics in grouped_by_disease.items():
            if disease_id == 1:  # Check if this is disease 1
                # Do something with this disease
                print(f"Processing disease {disease_id}")

            # Loop through all metrics for this disease
            for weight in metrics:

                metric_id = weight['metric_id']
                w = float(weight['w'])
                w_l = float(weight['w_l'])
                dp = z_dict[metric_id]['d+']
                dm = z_dict[metric_id]['d-']
                if disease_id not in idxs_dict:
                    idxs_dict[disease_id] = 0
                contribution = w * dp + w_l * dm
                idxs_dict[disease_id] += contribution

        Idxs = [{"disease_id": disease_id, "Idx": idx}
                for disease_id, idx in idxs_dict.items()]
        # Calculate denominator once
        sum_exp = sum(math.exp(item['Idx']) for item in Idxs)

        # Calculate probabilities
        probabilities = [
            {
                'disease_id': item['disease_id'],
                'Idx': item['Idx'],
                'probability': round(math.exp(item['Idx']) / sum_exp * 100, 2)
            }
            for item in Idxs
        ]

        # Кэшируем результаты
        for idx_item in probabilities:
            self._idx_cache[idx_item['disease_id']] = idx_item['Idx']
        return probabilities

    def _form_diagnostic_conclusions(self, Idxs, thresholds):
        """
        Формирование диагностических выводов на основе пороговых значений.

        Args:
            Idxs: Интегральные индексы
            thresholds: Пороговые значения

        Returns:
            list: Диагностические выводы
        """
        # Группируем пороги по disease_id для быстрого поиска
        thresholds_by_disease = self._group_thresholds_by_disease(thresholds)

        conclusions = []
        for idx_item in Idxs:
            disease_id = idx_item['disease_id']
            idx_value = idx_item['Idx']

            # # Пропускаем, если нет порогов для этого заболевания
            # if disease_id not in thresholds_by_disease:
            #     continue
            # Проверяем каждый порог для заболевания
            if disease_id != 2:
                for threshold in thresholds_by_disease[disease_id]:
                    tmin = threshold['Tmin']
                    tmax = threshold['Tmax']
                    matches_tmin = tmin is None or idx_value >= tmin
                    matches_tmax = tmax is None or idx_value < tmax
                    if matches_tmin and matches_tmax:
                        conclusions.append({
                            'disease_id': disease_id,
                            'C': threshold['C'],
                            'C_id': threshold['C_id'],
                            'idx': idx_value,
                            'probability': idx_item['probability']
                        })
            else:
                conclusions.append({
                    'disease_id': disease_id,
                    'C': "-",
                    'C_id': 1,
                    'idx': idx_value,
                    'probability': idx_item['probability']
                })
                break  # Первый подходящий порог
        return conclusions

    def _group_thresholds_by_disease(self, thresholds):
        """Группировка пороговых значений по disease_id"""
        thresholds_by_disease = {}

        for t in thresholds:
            disease_id = t['disease_id']

            if disease_id not in thresholds_by_disease:
                thresholds_by_disease[disease_id] = []

            # Конвертируем значения в float
            tmin = float(t['Tmin']) if t['Tmin'] is not None else None
            tmax = float(t['Tmax']) if t['Tmax'] is not None else None

            thresholds_by_disease[disease_id].append({
                'Tmin': tmin,
                'Tmax': tmax,
                'C': t['C'],
                'C_id': t['severity_id'],
            })

        return thresholds_by_disease

    def _enrich_results_with_names(self, percentile_results, conclusions):
        """
        Обогащение результатов названиями метрик и заболеваний.

        Args:
            percentile_results: Результаты с процентилями
            conclusions: Диагностические выводы

        Returns:
            tuple: Обогащенные результаты
        """
        # Получаем ID для запросов
        disease_ids = [item['disease_id'] for item in conclusions]
        metric_ids = [item['metric_id'] for item in percentile_results]

        # Получаем данные из API
        diseases = API.get_row_data("diseases_by_ids", disease_ids)["info"]
        metrics = API.get_row_data("metrics_by_ids", metric_ids)["info"]

        # Объединяем с названиями
        enriched_percentiles = self._merge_with_metrics(percentile_results, metrics)
        enriched_conclusions = self._merge_with_diseases(conclusions, diseases)
        return enriched_percentiles, enriched_conclusions

    def _merge_with_metrics(self, percentile_results, metrics):
        """Объединение процентилей с названиями метрик"""
        metrics_dict = {metric['metric_id']: metric for metric in metrics}
        enriched = []

        for item in percentile_results:
            metric_id = item['metric_id']
            if metric_id in metrics_dict:
                enriched_item = {
                    **item,
                    **metrics_dict[metric_id]
                }
                enriched.append(enriched_item)

        return enriched

    def _merge_with_diseases(self, conclusions, diseases):
        """Объединение выводов с названиями заболеваний"""
        diseases_dict = {disease['disease_id']: disease for disease in diseases}
        enriched = []

        for item in conclusions:
            disease_id = item['disease_id']
            if disease_id in diseases_dict:
                enriched_item = {
                    **item,
                    **diseases_dict[disease_id]
                }
                enriched.append(enriched_item)

        return enriched