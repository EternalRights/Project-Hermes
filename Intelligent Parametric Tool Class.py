import csv
import json
import sqlite3
import re
from typing import Dict, List, Any


class SmartParameterizer:
    def __init__(self):
        self.data_sources = {}

    def load_csv_data(self, file_path: str, name: str):
        """加载CSV数据源"""
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        self.data_sources[name] = data

    def load_json_data(self, file_path: str, name: str):
        """加载JSON数据源"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.data_sources[name] = data

    def extract_from_response(self, response: Dict[str, Any], path: str) -> Any:
        """从响应中提取数据"""
        # 支持JSONPath语法
        keys = path.split('.')
        current = response
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and key.isdigit():
                current = current[int(key)]
            else:
                return None
        return current

    def replace_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """替换模板中的变量"""
        pattern = r'\{\{(\w+)\}\}'

        def replace_var(match):
            var_name = match.group(1)
            return str(variables.get(var_name, match.group(0)))

        return re.sub(pattern, replace_var, template)

    def get_data_by_index(self, source_name: str, index: int) -> Dict[str, Any]:
        """按索引获取数据"""
        if source_name in self.data_sources:
            data = self.data_sources[source_name]
            if isinstance(data, list) and 0 <= index < len(data):
                return data[index]
        return {}