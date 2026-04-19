import csv
import json

import pymysql


class DataLoader:

    @staticmethod
    def load_csv(file_path: str) -> list[dict]:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [row for row in reader]

    @staticmethod
    def load_json(file_path: str) -> list[dict]:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return [data]

    @staticmethod
    def load_from_database(connection_config: dict, query: str) -> list[dict]:
        connection = pymysql.connect(**connection_config)
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
        finally:
            connection.close()
