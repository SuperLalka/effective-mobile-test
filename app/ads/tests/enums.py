import enum


class AdvertsItemConditions(str, enum.Enum):
    new = 'Новое'
    almost_new = 'Как новое'
    excellent = 'Отличное'
    good = 'Хорошее'
    acceptable = 'Приемлемое'

    @classmethod
    def values(cls):
        return [i.value for i in cls]
