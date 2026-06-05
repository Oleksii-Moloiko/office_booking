import logging
from django_ratelimit.exceptions import Ratelimited
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('bookings')


def custom_exception_handler(exc, context):
    """
    Уніфікований формат помилок:
    {
        "error": "Короткий опис",
        "code": "машино-читаємий код",
        "details": {...}  # опціонально
    }
    """
    # django-ratelimit raises Ratelimited — DRF does not know about it,
    # so exception_handler returns None. We handle it explicitly here.
    if isinstance(exc, Ratelimited):
        logger.warning(
            'Rate limit exceeded',
            extra={
                'path': context['request'].path,
                'method': context['request'].method,
            }
        )
        return Response(
            {
                'error': 'Забагато запитів. Спробуйте пізніше.',
                'code': 'too_many_requests',
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'error': _get_error_message(response),
            'code': _get_error_code(response.status_code),
        }

        # Додаємо деталі якщо є (наприклад, помилки валідації полів)
        if isinstance(response.data, dict):
            details = {
                k: v for k, v in response.data.items()
                if k not in ('detail', 'non_field_errors')
            }
            if details:
                error_data['details'] = details

        # Логуємо серверні помилки
        if response.status_code >= 500:
            logger.error(
                'Server error',
                extra={
                    'status_code': response.status_code,
                    'path': context['request'].path,
                    'error': str(exc),
                }
            )

        response.data = error_data

    return response


def _get_error_message(response) -> str:
    data = response.data
    if isinstance(data, dict):
        if 'detail' in data:
            return str(data['detail'])
        if 'non_field_errors' in data:
            errors = data['non_field_errors']
            return str(errors[0]) if errors else 'Помилка валідації'
        # Перша помилка поля
        for key, value in data.items():
            if isinstance(value, list) and value:
                return f"{key}: {value[0]}"
    if isinstance(data, list) and data:
        return str(data[0])
    return 'Виникла помилка'


def _get_error_code(status_code: int) -> str:
    codes = {
        400: 'bad_request',
        401: 'unauthorized',
        403: 'forbidden',
        404: 'not_found',
        405: 'method_not_allowed',
        409: 'conflict',
        429: 'too_many_requests',
        500: 'server_error',
    }
    return codes.get(status_code, 'error')