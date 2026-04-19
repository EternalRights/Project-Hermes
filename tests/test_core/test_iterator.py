import pytest

from hermes_core.parametrize.iterator import ParameterIterator


def test_sequential_multiple_sources():
    source_a = [{"x": 1}, {"x": 2}]
    source_b = [{"y": 3}, {"y": 4}]
    it = ParameterIterator([source_a, source_b], ParameterIterator.STRATEGY_SEQUENTIAL)
    result = list(it.iterate())
    assert result == [{"x": 1}, {"x": 2}, {"y": 3}, {"y": 4}]


def test_random_all_rows_yielded():
    source_a = [{"a": 1}, {"a": 2}]
    source_b = [{"b": 3}, {"b": 4}]
    it = ParameterIterator([source_a, source_b], ParameterIterator.STRATEGY_RANDOM)
    result = list(it.iterate())
    assert len(result) == 4
    values = sorted([list(r.values())[0] for r in result])
    assert values == [1, 2, 3, 4]


def test_cartesian_all_combinations():
    source_a = [{"x": 1}, {"x": 2}]
    source_b = [{"y": "a"}, {"y": "b"}]
    it = ParameterIterator([source_a, source_b], ParameterIterator.STRATEGY_CARTESIAN)
    result = list(it.iterate())
    assert len(result) == 4
    assert {"x": 1, "y": "a"} in result
    assert {"x": 1, "y": "b"} in result
    assert {"x": 2, "y": "a"} in result
    assert {"x": 2, "y": "b"} in result


def test_cartesian_single_source():
    source = [{"x": 1}, {"x": 2}]
    it = ParameterIterator([source], ParameterIterator.STRATEGY_CARTESIAN)
    result = list(it.iterate())
    assert result == [{"x": 1}, {"x": 2}]


def test_cartesian_empty_sources():
    it = ParameterIterator([], ParameterIterator.STRATEGY_CARTESIAN)
    result = list(it.iterate())
    assert result == []


def test_unknown_strategy():
    it = ParameterIterator([], "unknown")
    with pytest.raises(ValueError, match="Unknown strategy"):
        list(it.iterate())


def test_sequential_empty_sources():
    it = ParameterIterator([], ParameterIterator.STRATEGY_SEQUENTIAL)
    result = list(it.iterate())
    assert result == []
