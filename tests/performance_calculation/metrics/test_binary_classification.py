#  Author:   Niels Nuyttens  <niels@nannyml.com>
#
#  License: Apache Software License 2.0

"""Unit tests for performance metrics."""
from typing import Tuple

import pandas as pd
import pytest

from nannyml import PerformanceCalculator
from nannyml._typing import ProblemType
from nannyml.datasets import load_synthetic_binary_classification_dataset
from nannyml.performance_calculation.metrics.base import MetricFactory
from nannyml.performance_calculation.metrics.binary_classification import (
    BinaryClassificationAccuracy,
    BinaryClassificationAUROC,
    BinaryClassificationF1,
    BinaryClassificationPrecision,
    BinaryClassificationRecall,
    BinaryClassificationSpecificity,
)


@pytest.fixture(scope='module')
def binary_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:  # noqa: D103
    ref_df, ana_df, tgt_df = load_synthetic_binary_classification_dataset()
    ref_df['y_pred'] = ref_df['y_pred_proba'].map(lambda p: p >= 0.8).astype(int)
    ana_df['y_pred'] = ana_df['y_pred_proba'].map(lambda p: p >= 0.8).astype(int)

    return ref_df, ana_df, tgt_df


@pytest.fixture(scope='module')
def performance_calculator() -> PerformanceCalculator:
    return PerformanceCalculator(
        timestamp_column_name='timestamp',
        y_pred_proba='y_pred_proba',
        y_pred='y_pred',
        y_true='work_home_actual',
        metrics=['roc_auc', 'f1', 'precision', 'recall', 'specificity', 'accuracy'],
        problem_type='classification_binary',
    )


@pytest.fixture(scope='module')
def realized_performance_metrics(performance_calculator, binary_data) -> pd.DataFrame:
    performance_calculator.fit(binary_data[0])
    results = performance_calculator.calculate(binary_data[1].merge(binary_data[2], on='identifier')).filter(
        period='analysis'
    )
    return results.data


@pytest.fixture(scope='module')
def no_timestamp_metrics(binary_data):
    calc = PerformanceCalculator(
        y_pred_proba='y_pred_proba',
        y_pred='y_pred',
        y_true='work_home_actual',
        metrics=['roc_auc', 'f1', 'precision', 'recall', 'specificity', 'accuracy'],
        problem_type='classification_binary',
    ).fit(binary_data[0])
    results = calc.calculate(binary_data[1].merge(binary_data[2], on='identifier')).filter(period='analysis')
    return results.data


@pytest.mark.parametrize(
    'key,problem_type,metric',
    [
        ('roc_auc', ProblemType.CLASSIFICATION_BINARY, BinaryClassificationAUROC),
        ('f1', ProblemType.CLASSIFICATION_BINARY, BinaryClassificationF1),
        ('precision', ProblemType.CLASSIFICATION_BINARY, BinaryClassificationPrecision),
        ('recall', ProblemType.CLASSIFICATION_BINARY, BinaryClassificationRecall),
        ('specificity', ProblemType.CLASSIFICATION_BINARY, BinaryClassificationSpecificity),
        ('accuracy', ProblemType.CLASSIFICATION_BINARY, BinaryClassificationAccuracy),
    ],
)
def test_metric_factory_returns_correct_metric_given_key_and_problem_type(key, problem_type, metric):  # noqa: D103
    calc = PerformanceCalculator(
        timestamp_column_name='timestamp',
        y_pred_proba='y_pred_proba',
        y_pred='y_pred',
        y_true='y_true',
        metrics=['roc_auc', 'f1'],
        problem_type='classification_binary',
    )
    sut = MetricFactory.create(
        key, problem_type, y_true=calc.y_true, y_pred=calc.y_pred, y_pred_proba=calc.y_pred_proba
    )
    assert sut == metric(y_true=calc.y_true, y_pred=calc.y_pred, y_pred_proba=calc.y_pred_proba)


@pytest.mark.parametrize(
    'metric, expected',
    [
        ('roc_auc', [0.97096, 0.97025, 0.97628, 0.96772, 0.96989, 0.96005, 0.95853, 0.95904, 0.96309, 0.95756]),
        ('f1', [0.92186, 0.92124, 0.92678, 0.91684, 0.92356, 0.87424, 0.87672, 0.86806, 0.883, 0.86775]),
        ('precision', [0.96729, 0.96607, 0.96858, 0.96819, 0.9661, 0.94932, 0.95777, 0.95012, 0.95718, 0.94271]),
        ('recall', [0.88051, 0.88039, 0.88843, 0.87067, 0.8846, 0.81017, 0.80832, 0.79904, 0.8195, 0.80383]),
        ('specificity', [0.9681, 0.9701, 0.97277, 0.9718, 0.96864, 0.95685, 0.96364, 0.95795, 0.96386, 0.94879]),
        ('accuracy', [0.9228, 0.926, 0.9318, 0.9216, 0.9264, 0.8836, 0.8852, 0.8784, 0.8922, 0.8746]),
    ],
)
def test_metric_values_are_calculated_correctly(realized_performance_metrics, metric, expected):
    metric_values = realized_performance_metrics.loc[:, (metric, 'value')]
    assert (round(metric_values, 5) == expected).all()


@pytest.mark.parametrize(
    'metric, expected',
    [
        ('roc_auc', [0.97096, 0.97025, 0.97628, 0.96772, 0.96989, 0.96005, 0.95853, 0.95904, 0.96309, 0.95756]),
        ('f1', [0.92186, 0.92124, 0.92678, 0.91684, 0.92356, 0.87424, 0.87672, 0.86806, 0.883, 0.86775]),
        ('precision', [0.96729, 0.96607, 0.96858, 0.96819, 0.9661, 0.94932, 0.95777, 0.95012, 0.95718, 0.94271]),
        ('recall', [0.88051, 0.88039, 0.88843, 0.87067, 0.8846, 0.81017, 0.80832, 0.79904, 0.8195, 0.80383]),
        ('specificity', [0.9681, 0.9701, 0.97277, 0.9718, 0.96864, 0.95685, 0.96364, 0.95795, 0.96386, 0.94879]),
        ('accuracy', [0.9228, 0.926, 0.9318, 0.9216, 0.9264, 0.8836, 0.8852, 0.8784, 0.8922, 0.8746]),
    ],
)
def test_metric_values_without_timestamp_are_calculated_correctly(no_timestamp_metrics, metric, expected):
    metric_values = no_timestamp_metrics.loc[:, (metric, 'value')]
    assert (round(metric_values, 5) == expected).all()
