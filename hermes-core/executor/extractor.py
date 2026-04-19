import re

from jsonpath_ng import parse


class VariableExtractor:

    def extract_by_json_path(self, response, json_path, variable_name):
        try:
            data = response.json()
            expr = parse(json_path)
            matches = expr.find(data)
            if matches:
                return {variable_name: matches[0].value}
            return {}
        except Exception:
            return {}

    def extract_by_regex(self, response, pattern, variable_name, group=0):
        try:
            text = response.text
            match = re.search(pattern, text)
            if match:
                return {variable_name: match.group(group)}
            return {}
        except Exception:
            return {}

    def extract_variables(self, response, extract_config):
        result = {}
        for cfg in extract_config:
            source = cfg.get("source", "body")
            etype = cfg.get("type")
            variable_name = cfg.get("variable")
            if not variable_name:
                continue
            if etype == "json_path":
                result.update(self.extract_by_json_path(response, cfg["path"], variable_name))
            elif etype == "regex":
                result.update(self.extract_by_regex(response, cfg["pattern"], variable_name, cfg.get("group", 0)))
        return result
