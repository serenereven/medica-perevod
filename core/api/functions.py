from django.db.models import Func, CharField


class ExtractLeadingText(Func):
    """
    Извлекает текстовую часть строки до первого числа.
    Использует возможности PostgreSQL для работы с регулярными выражениями.
    """

    function = "SUBSTRING"
    template = "%(function)s(%(expressions)s FROM '^[^0-9]*')"
    output_field = CharField()


class ExtractFirstNumber(Func):
    """
    Извлекает первую последовательность цифр из строки.
    """

    function = "SUBSTRING"
    template = "%(function)s(%(expressions)s FROM '[0-9]+')"
    output_field = CharField()
