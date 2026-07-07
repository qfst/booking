import logging

from fastapi.exceptions import RequestValidationError

from app.api.shared.errors import Error, LocationType, ValidationError
from app.core.messages import Message


logger = logging.getLogger(__name__)

_MESSAGES: dict[str, str] = {
    'missing': Message.MISSING_FIELD,
    'string_type': Message.STRING_INVALID,
}


class ErrorMapper:
    """Преобразователь стандартных ошибок валидации FastAPI/Pydantic в единый формат."""

    @staticmethod
    def map(validation_error: RequestValidationError) -> Error:
        """Преобразует сырой список ошибок Pydantic в структурированный объект ответа.

        :param validation_error: Исключение валидации запроса от FastApi.
        :return: Стандартизированный объект ошибки с детализацией по полям.
        """
        logger.debug(
            f'Провал валидации входящего запроса. '
            f'Обнаружено ошибок: {len(validation_error.errors())}'
        )
        parsed_errors: list[ValidationError] = []
        seen_fields: set[str] = set()

        for error in validation_error.errors():
            loc = error.get('loc', [])
            if not loc:
                continue
            loc_type = str(loc[0]) if len(loc) > 0 else LocationType.BODY
            raw_field_name = loc[1]

            if loc_type == LocationType.HEADER:
                display_field = '-'.join(
                    word.capitalize() for word in raw_field_name.split('_')
                )
            else:
                display_field = raw_field_name

            if display_field in seen_fields:
                continue

            msg = error.get('msg', '')
            err_type = error.get('type', '')

            clean_message = _MESSAGES.get(err_type)
            if clean_message is None:
                logger.warning(
                    f'Обнаружен незадокументированный тип ошибки валидации:'
                    f' err_type={err_type}. Будет использовано стандартное сообщение '
                    f'Pydantic: {msg}'
                )
                clean_message = msg

            logger.debug(
                f'Обработка ошибки валидации: field={display_field}, type={err_type}, '
                f'loc_type={loc_type}'
            )
            parsed_errors.append(
                ValidationError(
                    field=display_field,
                    detail=clean_message,
                    location_type=LocationType(loc_type),
                )
            )
            seen_fields.add(display_field)

        return Error(message=Message.VALIDATION_ERROR, errors=parsed_errors)
