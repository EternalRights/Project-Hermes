import ast
import threading
import time

FORBIDDEN_AST_NODES = (ast.Import, ast.ImportFrom)

DANGEROUS_ATTRS = {'__globals__', '__code__', '__bases__', '__subclasses__', '__class__', '__mro__'}


def _validate_script(script_content):
    tree = ast.parse(script_content)
    for node in ast.walk(tree):
        if isinstance(node, FORBIDDEN_AST_NODES):
            raise ValueError(f"Forbidden AST node: {type(node).__name__}")
        if isinstance(node, ast.Attribute) and node.attr in DANGEROUS_ATTRS:
            raise ValueError(f"Access to dangerous attribute: {node.attr}")
    return tree


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

    def _get_safe_globals(self):
        return {
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

    def _run_script(self, script_content, context, response=None, timeout=30):
        try:
            _validate_script(script_content)
        except (SyntaxError, ValueError) as e:
            context.errors = getattr(context, "errors", [])
            context.errors.append(str(e))
            return

        local_vars = {"context": context}
        if response is not None:
            local_vars["response"] = response

        result = [None]
        error = [None]

        def target():
            try:
                exec(script_content, self._get_safe_globals(), local_vars)
            except Exception as e:
                error[0] = e

        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout=timeout)

        if thread.is_alive():
            context.errors = getattr(context, "errors", [])
            context.errors.append(f"Hook script execution timed out after {timeout}s")
        elif error[0]:
            context.errors = getattr(context, "errors", [])
            context.errors.append(str(error[0]))
