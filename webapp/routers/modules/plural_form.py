from num2words import num2words


class PluralForm:
    """Склонение числительных"""

    def __init__():
        pass

    @staticmethod
    async def _plural_form(number: str, forms: tuple[str, str, str]) -> str:
        number = str(number)

        last_two = int(number[-2:]) if len(number) > 1 else int(number)
        last_one = int(number[-1])

        if 11 <= last_two <= 14:
            return forms[0]
        if last_one == 1:
            return forms[1]
        if 2 <= last_one <= 4:
            return forms[2]
        return forms[0]

    @classmethod
    async def rub(cls, number: str) -> str:
        return await cls._plural_form(number, ("рублей", "рубль", "рубля"))

    @classmethod
    async def kop(cls, number: str) -> str:
        return await cls._plural_form(number, ("копеек", "копейка", "копейки"))

    @classmethod
    async def sum_propis(cls, total_sum: str) -> str:
        sum_user = total_sum.replace(" ", "")
        parts = sum_user.split(".")
        sum_user_rub = parts[0]
        sum_user_kop = parts[1]

        sum_rub_str = await cls.rub(sum_user_rub)
        sum_kop_str = await cls.kop(sum_user_kop)

        sum_propis_rus = num2words(sum_user_rub, lang="ru")
        sum_rub = (sum_propis_rus + " " + sum_rub_str).capitalize()
        sum_kop = (str(sum_user_kop) + " " + sum_kop_str).capitalize()
        return sum_rub + " " + sum_kop