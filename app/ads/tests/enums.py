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


AD_TITLE_EXAMPLES = ['Монета', 'Часы', 'Бюст', 'Шкатулка']
AD_DESC_KEYWORD_EXAMPLES = ['кобальт', 'винтаж', 'редкая', 'целая']
AD_CATEGORY_EXAMPLES = ['Нумизматика', 'Мебель', 'Скульптура']
AD_CONDITION_EXAMPLES = ['Новое', 'Как новое', 'Отличное', 'Хорошее', 'Приемлемое']
