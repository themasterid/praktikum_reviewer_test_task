# Можно лучше, если импортировать typing,
# это поможет нам разобраться с типами данных.
import datetime as dt


class Record:
    # date='' не лучший выбор, с typing мы можем принять
    # либо текущую дату, либо None, давай попробуем сделать это
    # через аннотацию типов.
    # Так же для amount и comment.
    # В будущем это пригодится. И так по всему коду, повторно делать аннотацию
    # переменных не нужно, достаточно это сделать один раз.
    def __init__(self, amount, comment, date=''):
        self.amount = amount
        # Тут можно лучше, избавится от NOT немного изменив логику.
        self.date = (
            dt.datetime.strptime(date, '%d.%m.%Y').date()
            if date
            else dt.datetime.now().date()
        )
        # Желательно держать переменные в одном месте,
        # не раскидывая их по телу класса.
        self.comment = comment


# Говорят программисты делают докстринги,
# мелочь, а другому программисту сразу становится понятно, о чем класс.
class Calculator:
    def __init__(self, limit):
        self.limit = limit
        # Отличное решение использовать [] вместо list()!
        self.records = []

    # метод ничего не возвращает, намек на typing
    def add_record(self, record):
        self.records.append(record)

    def get_today_stats(self):
        today_stats = 0
        # Желательно вынести dt.datetime.now().date() в отдельную переменную,
        # что бы не запрашивать каждый раз текущую дату.
        # Если работа скрипта затянется или скрипт отработает,
        # на стыке смены дат можно получить не то значение.
        for Record in self.records:
            if Record.date == dt.datetime.now().date():
                today_stats = today_stats + Record.amount
        # Тут можно попробовать лучше, проитерироваться по всем записям
        # records и выбрать даты на "сегодня", и сравнить их с текущей,
        # если равны выдать сумму применив метод sum например return sum(выборка по датам).
        # Давай попробуем сделать все это через list comprehension.
        # Это избавит нас от лишней переменной today_stats
        # https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
        return today_stats

    def get_week_stats(self):
        # Отличное решение вынести дату в отдельную переменную!
        # Что бы все было более очевидно, попробуем использовать
        # timedelta в выборке недельного диапазона.
        today = dt.datetime.now().date()
        return sum(
            record.amount
            for record in self.records
            if ((today - record.date).days < 7 and (today - record.date).days >= 0)
        )


class CaloriesCalculator(Calculator):
    # Комментарий к одному методу класса лучше вынести в докстринг
    def get_calories_remained(self):  # Получает остаток калорий на сегодня
        # Однобуквенные переменные непонятны, лучше давать осмысленные имена
        # переменным, например limit_today
        x = self.limit - self.get_today_stats()
        if x > 0:
            # f-строка без вывода значений переменных не имеет никакого смысла
            # Давай попробуем сделать все так:
            # ('текст'
            # f'текст {var} текст')
            # это смотрится более читаемо.
            return f'Сегодня можно съесть что-нибудь' \
                   f' ещё, но с общей калорийностью не более {x} кКал'
        # Если у нас есть, return, и он по условию не сработает,
        # нужен ли нам этот лишний else? Давай проверим без него :)
        else:
            # Давай подумаем, однострочный возврат, что тут лишнее?
            return('Хватит есть!')


class CashCalculator(Calculator):
    # Отличное решение вынести курс валют в константы!
    # Но без рубля тут грустно, надо подумать как его вернуть :)
    # float можно указать так, 60.0 Python не запрещает.
    USD_RATE = float(60)  # Курс доллар США.
    EURO_RATE = float(70)  # Курс Евро.

    # не обязательно передавать в метод константы класса
    # USD_RATE, EURO_RATE, достаточно обратится к ним по self
    def get_today_cash_remained(self, currency,
                                USD_RATE=USD_RATE, EURO_RATE=EURO_RATE):
        currency_type = currency
        cash_remained = self.limit - self.get_today_stats()
        
        # Можно избавится от условий, применив словарь,
        # и уже через словарь проверять валюту.
        # например if currency not in my_dict:
        #               return 'текст'
        if currency == 'usd':
            cash_remained /= USD_RATE
            currency_type = 'USD'
        elif currency_type == 'eur':
            cash_remained /= EURO_RATE
            currency_type = 'Euro'
        elif currency_type == 'rub':
            cash_remained == 1.00
            currency_type = 'руб'
        # Тут тоже можно поменять логику условий
        # избавится от лишних elif, особенно в случае долга.
        # поможет в этом нам техника guard block
        # https://medium.com/@scadge/if-statements-design-guard-clauses-might-be-all-you-need-67219a1a981a
        if cash_remained > 0:
            # тут лаконичнее выглядит такая конструкция
            # f'На сегодня осталось {кеш_сегодня} {валюта}'
            # округление можно вынести в константы
            return (
                f'На сегодня осталось {round(cash_remained, 2)} '
                f'{currency_type}'
            )
        # тут можно вынести отдельным условием, дабы не считать лишнее если у нас
        # лимит на сегодня равен 0
        elif cash_remained == 0:
            return 'Денег нет, держись'
        # Лишнее условие, можно обойтись без него, совсем без условия
        # достаточно вернуть данные, проверь, это интересно.
        elif cash_remained < 0:
            # Перегружена строка, лучше использовать f-строку
            # в которую просто вставим подготовленные данные.
            return 'Денег нет, держись:' \
                   ' твой долг - {0:.2f} {1}'.format(-cash_remained,
                                                     currency_type)

    # Лучше сделать отдельным метод в классе Calculator, где посчитаем
    # лимит минус статистика за сегодня
    def get_week_stats(self):
        super().get_week_stats()
