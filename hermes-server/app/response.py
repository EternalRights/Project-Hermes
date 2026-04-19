def success_response(data=None, message='success', code=200):
    return {
        'code': code,
        'message': message,
        'data': data,
    }


def error_response(message='error', code=400, data=None):
    return {
        'code': code,
        'message': message,
        'data': data,
    }


def paginate_response(query, page, per_page):
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'items': pagination.items,
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages,
    }
