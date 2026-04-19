import re
import ast

from .functions import FUNCTIONS

_PATTERN = re.compile(r"\{\{(.+?)\}\}")


class TemplateRenderer:

    def render(self, template: str, variables: dict) -> str:
        def _replace(match: re.Match) -> str:
            expr = match.group(1).strip()
            if "(" in expr and expr.endswith(")"):
                return str(self._call_function(expr))
            if expr in variables:
                return str(variables[expr])
            return match.group(0)

        return _PATTERN.sub(_replace, template)

    def render_dict(self, data: dict, variables: dict) -> dict:
        result = {}
        for key, value in data.items():
            rendered_key = self.render(key, variables)
            if isinstance(value, str):
                result[rendered_key] = self.render(value, variables)
            elif isinstance(value, dict):
                result[rendered_key] = self.render_dict(value, variables)
            elif isinstance(value, list):
                result[rendered_key] = self._render_list(value, variables)
            else:
                result[rendered_key] = value
        return result

    def _render_list(self, data: list, variables: dict) -> list:
        result = []
        for item in data:
            if isinstance(item, str):
                result.append(self.render(item, variables))
            elif isinstance(item, dict):
                result.append(self.render_dict(item, variables))
            elif isinstance(item, list):
                result.append(self._render_list(item, variables))
            else:
                result.append(item)
        return result

    @staticmethod
    def _call_function(expr: str):
        func_name_end = expr.index("(")
        func_name = expr[:func_name_end].strip()
        args_str = expr[func_name_end + 1 : -1].strip()

        if func_name not in FUNCTIONS:
            raise ValueError(f"Unknown function: {func_name}")

        args = []
        kwargs = {}
        if args_str:
            parsed = ast.parse(f"f({args_str})", mode="eval")
            for elt in parsed.body.args:
                args.append(ast.literal_eval(elt))
            for kw in parsed.body.keywords:
                kwargs[kw.arg] = ast.literal_eval(kw.value)

        return FUNCTIONS[func_name](*args, **kwargs)
