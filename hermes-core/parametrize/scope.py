class VariableScope:

    SCOPE_STEP = "step"
    SCOPE_CASE = "case"
    SCOPE_ENVIRONMENT = "environment"
    SCOPE_GLOBAL = "global"

    _PRIORITY = [SCOPE_STEP, SCOPE_CASE, SCOPE_ENVIRONMENT, SCOPE_GLOBAL]

    def __init__(self):
        self._scopes: dict[str, dict] = {
            self.SCOPE_STEP: {},
            self.SCOPE_CASE: {},
            self.SCOPE_ENVIRONMENT: {},
            self.SCOPE_GLOBAL: {},
        }

    def set_global(self, key: str, value):
        self._scopes[self.SCOPE_GLOBAL][key] = value

    def set_environment(self, key: str, value):
        self._scopes[self.SCOPE_ENVIRONMENT][key] = value

    def set_case(self, key: str, value):
        self._scopes[self.SCOPE_CASE][key] = value

    def set_step(self, key: str, value):
        self._scopes[self.SCOPE_STEP][key] = value

    def get(self, key: str):
        for scope_type in self._PRIORITY:
            if key in self._scopes[scope_type]:
                return self._scopes[scope_type][key]
        raise KeyError(f"Variable '{key}' not found in any scope")

    def merge(self) -> dict:
        merged = {}
        for scope_type in reversed(self._PRIORITY):
            merged.update(self._scopes[scope_type])
        return merged

    def clear_scope(self, scope_type: str):
        if scope_type in self._scopes:
            self._scopes[scope_type] = {}
