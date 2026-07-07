from enum import StrEnum

from pydantic import BaseModel, Field


class LocationType(StrEnum):
    """Тип расположения ошибочного поля в запросе."""

    HEADER = 'header'
    BODY = 'body'
    PATH = 'path'
    QUERY = 'query'


class ValidationError(BaseModel):
    """Детализированная информация об ошибке конкретного поля."""

    field: str = Field(description='Имя поля, в котором допущена ошибка')
    detail: str = Field(description='Текст ошибки валидации для поля')
    location_type: LocationType = Field(
        description='Где именно в запросе находится поле',
    )


class Error(BaseModel):
    """Стандартный формат ответа сервера при возникновении ошибок."""

    message: str = Field(description='Общее описание ошибки или глобальное сообщение')
    errors: list[ValidationError] | None = Field(
        default=None,
        description='Список детальных ошибок валидации полей',
    )

    model_config = {
        'json_schema_extra': {
            'examples': [
                {
                    'message': 'Ошибка валидации данных',
                    'errors': [
                        {
                            'field': 'some_path',
                            'detail': 'Путь не найден',
                            'location_type': 'path',
                        },
                        {
                            'field': 'some_header',
                            'detail': 'Заголовок не найден',
                            'location_type': 'header',
                        },
                        {
                            'field': 'some_body_field',
                            'detail': 'Поле не найдено',
                            'location_type': 'body',
                        },
                    ],
                }
            ]
        }
    }
