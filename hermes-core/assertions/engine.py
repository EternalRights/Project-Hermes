import re

from jsonschema import validate, ValidationError


class AssertionResult:

    def __init__(self, passed, assertion_type, expected, actual, message=""):
        self.passed = passed
        self.assertion_type = assertion_type
        self.expected = expected
        self.actual = actual
        self.message = message

    def __repr__(self):
        status = "PASS" if self.passed else "FAIL"
        return f"AssertionResult({status}, {self.assertion_type}, expected={self.expected}, actual={self.actual})"


def _compare(actual, expected, comparison):
    ops = {
        "eq": lambda a, e: a == e,
        "neq": lambda a, e: a != e,
        "gt": lambda a, e: a > e,
        "gte": lambda a, e: a >= e,
        "lt": lambda a, e: a < e,
        "lte": lambda a, e: a <= e,
        "contains": lambda a, e: e in a,
        "not_contains": lambda a, e: e not in a,
        "starts_with": lambda a, e: str(a).startswith(str(e)),
        "ends_with": lambda a, e: str(a).endswith(str(e)),
    }
    op = ops.get(comparison)
    if op is None:
        return False, f"Unsupported comparison: {comparison}"
    try:
        result = op(actual, expected)
        return result, "" if result else f"{actual} {comparison} {expected} failed"
    except TypeError as e:
        return False, str(e)


class AssertionEngine:

    def assert_status_code(self, actual, expected):
        passed = actual == expected
        return AssertionResult(
            passed=passed,
            assertion_type="status_code",
            expected=expected,
            actual=actual,
            message="" if passed else f"Expected status {expected}, got {actual}",
        )

    def assert_json_path(self, response, json_path, expected, comparison="eq"):
        from jsonpath_ng import parse
        try:
            data = response.json()
            expr = parse(json_path)
            matches = expr.find(data)
            if not matches:
                return AssertionResult(
                    passed=False,
                    assertion_type="json_path",
                    expected=expected,
                    actual=None,
                    message=f"JSONPath '{json_path}' found no matches",
                )
            actual = matches[0].value
            passed, msg = _compare(actual, expected, comparison)
            return AssertionResult(
                passed=passed,
                assertion_type="json_path",
                expected=expected,
                actual=actual,
                message=msg,
            )
        except Exception as e:
            return AssertionResult(
                passed=False,
                assertion_type="json_path",
                expected=expected,
                actual=None,
                message=str(e),
            )

    def assert_regex(self, text, pattern, expected_match=True):
        try:
            match = re.search(pattern, text)
            found = match is not None
            passed = found == expected_match
            return AssertionResult(
                passed=passed,
                assertion_type="regex",
                expected=expected_match,
                actual=found,
                message="" if passed else f"Regex '{pattern}' match={found}, expected={expected_match}",
            )
        except re.error as e:
            return AssertionResult(
                passed=False,
                assertion_type="regex",
                expected=expected_match,
                actual=None,
                message=str(e),
            )

    def assert_response_time(self, elapsed_ms, max_ms):
        passed = elapsed_ms <= max_ms
        return AssertionResult(
            passed=passed,
            assertion_type="response_time",
            expected=f"<={max_ms}ms",
            actual=f"{elapsed_ms}ms",
            message="" if passed else f"Response time {elapsed_ms}ms exceeded {max_ms}ms",
        )

    def assert_schema(self, json_data, schema):
        try:
            validate(instance=json_data, schema=schema)
            return AssertionResult(
                passed=True,
                assertion_type="schema",
                expected="valid",
                actual="valid",
                message="",
            )
        except ValidationError as e:
            return AssertionResult(
                passed=False,
                assertion_type="schema",
                expected="valid",
                actual="invalid",
                message=e.message,
            )

    def run_assertions(self, response, assertions_config):
        results = []
        for cfg in assertions_config:
            atype = cfg.get("type")
            if atype == "status_code":
                results.append(self.assert_status_code(response.status_code, cfg["expected"]))
            elif atype == "json_path":
                results.append(self.assert_json_path(
                    response, cfg["path"], cfg["expected"], cfg.get("comparison", "eq")
                ))
            elif atype == "regex":
                results.append(self.assert_regex(
                    response.text, cfg["pattern"], cfg.get("expected_match", True)
                ))
            elif atype == "response_time":
                results.append(self.assert_response_time(response.elapsed, cfg["max_ms"]))
            elif atype == "schema":
                results.append(self.assert_schema(response.json(), cfg["schema"]))
            else:
                results.append(AssertionResult(
                    passed=False,
                    assertion_type=atype,
                    expected=None,
                    actual=None,
                    message=f"Unknown assertion type: {atype}",
                ))
        return results
