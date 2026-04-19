import csv
import json
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from hermes_core.parametrize.data_loader import DataLoader


def test_load_csv():
    fd, path = tempfile.mkstemp(suffix=".csv")
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "age"])
            writer.writeheader()
            writer.writerow({"name": "Alice", "age": "30"})
            writer.writerow({"name": "Bob", "age": "25"})
        result = DataLoader.load_csv(path)
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0] == {"name": "Alice", "age": "30"}
        assert result[1] == {"name": "Bob", "age": "25"}
    finally:
        os.close(fd)
        os.unlink(path)


def test_load_json_list():
    fd, path = tempfile.mkstemp(suffix=".json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump([{"key": "val1"}, {"key": "val2"}], f)
        result = DataLoader.load_json(path)
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0] == {"key": "val1"}
        assert result[1] == {"key": "val2"}
    finally:
        os.close(fd)
        os.unlink(path)


def test_load_json_single_object():
    fd, path = tempfile.mkstemp(suffix=".json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"key": "val1"}, f)
        result = DataLoader.load_json(path)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == {"key": "val1"}
    finally:
        os.close(fd)
        os.unlink(path)


def test_load_from_database():
    mock_cursor = MagicMock()
    mock_cursor.description = [("id",), ("name",)]
    mock_cursor.fetchall.return_value = [(1, "Alice"), (2, "Bob")]
    mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
    mock_cursor.__exit__ = MagicMock(return_value=False)

    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor

    with patch("hermes_core.parametrize.data_loader.pymysql.connect", return_value=mock_connection):
        config = {"host": "localhost", "user": "root", "password": "pass", "db": "test"}
        result = DataLoader.load_from_database(config, "SELECT id, name FROM users")

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] == {"id": 1, "name": "Alice"}
    assert result[1] == {"id": 2, "name": "Bob"}
    mock_connection.close.assert_called_once()
