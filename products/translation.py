from modeltranslation.translator import register, TranslationOptions

from .models import Category


@register(Category)
class CategoryTranslationOption(TranslationOptions):
    fields = ('name', 'slug')

