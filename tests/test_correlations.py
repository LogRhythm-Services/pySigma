import pytest
from sigma.correlations import (
    SigmaCorrelationCondition,
    SigmaCorrelationConditionOperator,
    SigmaCorrelationRule,
    SigmaCorrelationType,
    SigmaRuleReference,
)
from sigma.exceptions import (
    SigmaCorrelationConditionError,
    SigmaCorrelationRuleError,
    SigmaCorrelationTypeError,
    SigmaTimespanError,
)


def test_correlation_valid_1():
    rule = SigmaCorrelationRule.from_dict(
        {
            "title": "Valid correlation",
            "correlation": {
                "type": "event_count",
                "rules": "failed_login",
                "group-by": "user",
                "timespan": "10m",
                "condition": {"gte": 10},
            },
        }
    )
    assert isinstance(rule, SigmaCorrelationRule)
    assert rule.title == "Valid correlation"
    assert rule.type == SigmaCorrelationType.EVENT_COUNT
    assert rule.rules == [SigmaRuleReference("failed_login")]
    assert rule.group_by == ["user"]
    assert rule.timespan == 600
    assert rule.condition == SigmaCorrelationCondition(
        op=SigmaCorrelationConditionOperator.GTE, count=10
    )
    assert rule.ordered == False


def test_correlation_valid_2():
    rule = SigmaCorrelationRule.from_dict(
        {
            "title": "Valid correlation",
            "correlation": {
                "type": "temporal",
                "rules": ["event_a", "event_b"],
                "group-by": ["source", "user"],
                "timespan": "1h",
                "ordered": True,
            },
        }
    )
    assert isinstance(rule, SigmaCorrelationRule)
    assert rule.title == "Valid correlation"
    assert rule.type == SigmaCorrelationType.TEMPORAL
    assert rule.rules == [SigmaRuleReference("event_a"), SigmaRuleReference("event_b")]
    assert rule.group_by == ["source", "user"]
    assert rule.timespan == 3600
    assert rule.condition == None
    assert rule.ordered == True


def test_correlation_valid_1_from_yaml():
    rule = SigmaCorrelationRule.from_yaml(
        """
title: Valid correlation
correlation:
    type: event_count
    rules: failed_login
    group-by: user
    timespan: 10m
    condition:
        gte: 10
"""
    )
    assert isinstance(rule, SigmaCorrelationRule)
    assert rule.title == "Valid correlation"
    assert rule.type == SigmaCorrelationType.EVENT_COUNT
    assert rule.rules == [SigmaRuleReference("failed_login")]
    assert rule.group_by == ["user"]
    assert rule.timespan == 600
    assert rule.condition == SigmaCorrelationCondition(
        op=SigmaCorrelationConditionOperator.GTE, count=10
    )
    assert rule.ordered == False


def test_correlation_valid_2_from_yaml():
    rule = SigmaCorrelationRule.from_yaml(
        """
title: Valid correlation
correlation:
    type: temporal
    rules:
        - event_a
        - event_b
    group-by:
        - source
        - user
    timespan: 1h
    ordered: true
"""
    )
    assert isinstance(rule, SigmaCorrelationRule)
    assert rule.title == "Valid correlation"
    assert rule.type == SigmaCorrelationType.TEMPORAL
    assert rule.rules == [SigmaRuleReference("event_a"), SigmaRuleReference("event_b")]
    assert rule.group_by == ["source", "user"]
    assert rule.timespan == 3600
    assert rule.condition == None
    assert rule.ordered == True


def test_correlation_wrong_type():
    with pytest.raises(
        SigmaCorrelationTypeError, match="'test' is no valid Sigma correlation type"
    ):
        SigmaCorrelationRule.from_dict(
            {
                "name": "Invalid correlation type",
                "correlation": {
                    "type": "test",
                    "rules": "failed_login",
                    "group-by": ["user"],
                    "timespan": "10m",
                    "condition": {"gte": 10},
                },
            }
        )


def test_correlation_without_type():
    with pytest.raises(SigmaCorrelationTypeError, match="Sigma correlation rule without type"):
        SigmaCorrelationRule.from_dict(
            {
                "name": "Invalid correlation type",
                "correlation": {
                    "rules": "failed_login",
                    "group-by": ["user"],
                    "timespan": "10m",
                    "condition": {"gte": 10},
                },
            }
        )


def test_correlation_invalid_rule_reference():
    with pytest.raises(
        SigmaCorrelationRuleError, match="Rule reference must be plain string or list."
    ):
        SigmaCorrelationRule.from_dict(
            {
                "name": "Invalid rule reference",
                "correlation": {
                    "type": "event_count",
                    "rules": {"test": "test"},
                    "group-by": ["user"],
                    "timespan": "10m",
                    "condition": {"gte": 10},
                },
            }
        )


def test_correlation_without_rule_reference():
    with pytest.raises(
        SigmaCorrelationRuleError, match="Sigma correlation rule without rule references"
    ):
        SigmaCorrelationRule.from_dict(
            {
                "name": "Invalid rule reference",
                "correlation": {
                    "type": "event_count",
                    "group-by": ["user"],
                    "timespan": "10m",
                    "condition": {"gte": 10},
                },
            }
        )


def test_correlation_invalid_group_by():
    with pytest.raises(
        SigmaCorrelationRuleError,
        match="Sigma correlation group-by definition must be string or list",
    ):
        SigmaCorrelationRule.from_dict(
            {
                "name": "Invalid group-by",
                "correlation": {
                    "type": "event_count",
                    "rules": "failed_login",
                    "group-by": {"test": "test"},
                    "timespan": "10m",
                    "condition": {"gte": 10},
                },
            }
        )


def test_correlation_invalid_timespan():
    with pytest.raises(SigmaTimespanError, match="Timespan '10' is invalid."):
        SigmaCorrelationRule.from_dict(
            {
                "name": "Invalid time span",
                "correlation": {
                    "type": "event_count",
                    "rules": "failed_login",
                    "group-by": ["user"],
                    "timespan": "10",
                    "condition": {"gte": 10},
                },
            }
        )


def test_correlation_invalid_ordered():
    with pytest.raises(
        SigmaCorrelationRuleError, match="Sigma correlation ordered definition must be boolean"
    ):
        SigmaCorrelationRule.from_dict(
            {
                "name": "Invalid ordered",
                "correlation": {
                    "type": "event_count",
                    "rules": "failed_login",
                    "group-by": ["user"],
                    "timespan": "10m",
                    "ordered": "test",
                    "condition": {"gte": 10},
                },
            }
        )


def test_correlation_invalid_condition():
    with pytest.raises(
        SigmaCorrelationRuleError, match="Sigma correlation condition definition must be a dict"
    ):
        SigmaCorrelationRule.from_dict(
            {
                "name": "Invalid condition",
                "correlation": {
                    "type": "event_count",
                    "rules": "failed_login",
                    "group-by": ["user"],
                    "timespan": "10m",
                    "condition": "test",
                },
            }
        )


def test_correlation_without_condition():
    with pytest.raises(SigmaCorrelationRuleError, match="Sigma correlation rule without condition"):
        SigmaCorrelationRule.from_dict(
            {
                "name": "Invalid condition",
                "correlation": {
                    "type": "event_count",
                    "rules": "failed_login",
                    "group-by": ["user"],
                    "timespan": "10m",
                },
            }
        )


def test_correlation_condition():
    cond = SigmaCorrelationCondition.from_dict({"gte": 10})
    assert isinstance(cond, SigmaCorrelationCondition)
    assert cond.op == SigmaCorrelationConditionOperator.GTE
    assert cond.count == 10


def test_correlation_condition_multiple_items():
    with pytest.raises(
        SigmaCorrelationConditionError,
        match="Sigma correlation condition must have exactly one item",
    ):
        SigmaCorrelationCondition.from_dict({"gte": 10, "lte": 20})


def test_correlation_condition_invalid_operator():
    with pytest.raises(
        SigmaCorrelationConditionError,
        match="Sigma correlation condition operator 'test' is invalid",
    ):
        SigmaCorrelationCondition.from_dict({"test": 10})


def test_correlation_condition_invalid_count():
    with pytest.raises(
        SigmaCorrelationConditionError,
        match="'test' is no valid Sigma correlation condition count",
    ):
        SigmaCorrelationCondition.from_dict({"gte": "test"})
