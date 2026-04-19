import time


class HookExecutor:

    def execute_pre_hooks(self, hooks_config, context):
        if not hooks_config:
            return context
        for hook in hooks_config:
            htype = hook.get("type")
            if htype == "script":
                self._run_script(hook["content"], context)
            elif htype == "wait":
                duration = hook.get("duration", 1)
                time.sleep(duration)
        return context

    def execute_post_hooks(self, hooks_config, context, response):
        if not hooks_config:
            return context
        for hook in hooks_config:
            htype = hook.get("type")
            if htype == "script":
                self._run_script(hook["content"], context, response=response)
            elif htype == "wait":
                duration = hook.get("duration", 1)
                time.sleep(duration)
        return context

    def _run_script(self, script_content, context, response=None):
        safe_globals = {
            "__builtins__": {
                "int": int,
                "float": float,
                "str": str,
                "bool": bool,
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "set": set,
                "len": len,
                "range": range,
                "print": print,
                "isinstance": isinstance,
                "type": type,
                "abs": abs,
                "min": min,
                "max": max,
                "sum": sum,
                "sorted": sorted,
                "reversed": reversed,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
                "round": round,
                "hasattr": hasattr,
                "getattr": getattr,
                "setattr": setattr,
            },
            "time": time,
        }
        local_vars = {"context": context}
        if response is not None:
            local_vars["response"] = response
        try:
            exec(script_content, safe_globals, local_vars)
        except Exception as e:
            context.errors = getattr(context, "errors", [])
            context.errors.append(str(e))
