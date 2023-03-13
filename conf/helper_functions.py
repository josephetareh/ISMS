from django.core.paginator import Paginator


def paginator_helper(request, django_object, records_per_page):
    paginator = Paginator(django_object, records_per_page)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)
    return page_object
