from django.core.paginator import Paginator
from django.conf import settings


def paginator(request, post):
    paginator = Paginator(post, settings.NUMBER_OBJECTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
