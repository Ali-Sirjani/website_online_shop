from django.template import Library

register = Library()


@register.filter
def num_fa(value):
    persian = '۰١٢٣٤٥٦٧٨٩'
    engilish = '0123456789'
    value = str(f'{value:,}')

    trans_table = str.maketrans(engilish, persian)
    translated_value = value.translate(trans_table)

    return translated_value




