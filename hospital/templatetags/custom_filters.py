from django import template

register = template.Library()


@register.filter
def get(dictionary, key):
    """获取字典中的值"""
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def attr(obj, attribute):
    """获取对象的属性"""
    if obj is None:
        return None
    return getattr(obj, attribute, None)
