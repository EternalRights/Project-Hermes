import html


def html_escape(s):
    return html.escape(str(s), quote=True)
