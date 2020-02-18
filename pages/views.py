from django.shortcuts import render, redirect

from pages.base import contact
from . import base
from django.conf import settings
from HMS import settings
from staff import base as staff_base


def home_view(request):
    return render(request, "pages/index.html")


def about_view(request):
    return render(request, "pages/about.html")


def contact_view(request):
    context = {'messages': []}
    if request.method == 'POST':
        result = base.contact().contact_us(request.POST)
        print(result)
        if result['messages'] == settings.NEGATIVE:
            context['messages'].extend(result['messages'])
        else:
            context['messages'].append('Information saved.')
    context['messages_count'] = len(context['messages'])
    return render(request, "pages/contact.html")


def rooms_view(request):
    context = {}
    """ deluxe """
    result = staff_base.hotel_room().get_room_types(type='strict', only_count=True,
                                                    Post={'room_type_title': 'Deluxe'})
    if result['status'] == settings.POSITIVE:
        context['deluxe'] = result['count']

    """ Diamond"""
    result = staff_base.hotel_room().get_room_types(type='strict', only_count=True,
                                                    Post={'room_type_title': 'Diamond'})
    if result['status'] == settings.POSITIVE:
        context['diamond'] = result['count']

    # """ comfort """
    # result = staff_base.hotel_room().get_room_types(type='strict', only_count=True,
    #                                                 Post={'room_type_title': 'Comfort'})
    # if result['status'] == settings.POSITIVE:
    #     context['comfort'] = result['count']

    """ cozy """
    result = staff_base.hotel_room().get_room_types(type='strict', only_count=True,
                                                    Post={'room_type_title': 'Cozy'})
    if result['status'] == settings.POSITIVE:
        context['cozy'] = result['count']

    """ contemporary """
    result = staff_base.hotel_room().get_room_types(type='strict', only_count=True,
                                                    Post={'room_type_title': 'Contemporary'})
    if result['status'] == settings.POSITIVE:
        context['contemporary'] = result['count']

    """ twin """
    result = staff_base.hotel_room().get_room_types(type='strict', only_count=True,
                                                    Post={'room_type_title': 'Twin Delight'})
    if result['status'] == settings.POSITIVE:
        context['twin'] = result['count']

    """ Standard """
    result = staff_base.hotel_room().get_room_types(type='strict', only_count=True,
                                                    Post={'room_type_title': 'Standard'})
    if result['status'] == settings.POSITIVE:
        context['standard'] = result['count']

    """ Presidential """
    result = staff_base.hotel_room().get_room_types(type='strict', only_count=True,
                                                    Post={'room_type_title': 'Presidential'})
    if result['status'] == settings.POSITIVE:
        context['presidential'] = result['count']

    return render(request, "pages/rooms.html", context)


def p_details_view(request):
    context = {}

    """ Presidential """
    result = staff_base.hotel_room().get_room_types(type='strict', only_count=True,
                                                    Post={'room_type_title': 'Presidential'})
    if result['status'] == settings.POSITIVE:
        context['presidential'] = result['count']

    return render(request, "pages/presidential_details.html", context)


def twin_details_view(request):
    context = {}

    """ twin """
    result = staff_base.hotel_room().get_room_types(type='strict', only_count=True,
                                                    Post={'room_type_title': 'Twin Delight'})
    if result['status'] == settings.POSITIVE:
        context['twin'] = result['count']

    return render(request, "pages/twin_delight_details.html", context)


def contem_details_view(request):
    context = {}

    """ cozy """
    result = staff_base.hotel_room().get_room_types(type='strict', only_count=True,
                                                    Post={'room_type_title': 'Contemporary'})
    if result['status'] == settings.POSITIVE:
        context['contemporary'] = result['count']

    return render(request, "pages/contemporary_details.html", context)


def cozy_details_view(request):
    context = {}

    """ cozy """
    result = staff_base.hotel_room().get_room_types(type='strict', only_count=True,
                                                    Post={'room_type_title': 'Cozy'})
    if result['status'] == settings.POSITIVE:
        context['cozy'] = result['count']

    return render(request, "pages/cozy_delight_details.html", context)


def diamond_details_view(request):
    context = {}

    """ Diamond"""
    result = staff_base.hotel_room().get_room_types(type='strict', only_count=True,
                                                    Post={'room_type_title': 'Diamond'})
    if result['status'] == settings.POSITIVE:
        context['diamond'] = result['count']

    return render(request, "pages/diamond_details.html", context)


def deluxe_details_view(request):
    context = {}

    """ deluxe """
    result = staff_base.hotel_room().get_room_types(type='strict', only_count=True,
                                                    Post={'room_type_title': 'Deluxe'})
    if result['status'] == settings.POSITIVE:
        context['deluxe'] = result['count']

    return render(request, "pages/_deluxe_details.html", context)


def standard_details_view(request):
    context = {}

    """ Standard """
    result = staff_base.hotel_room().get_room_types(type='strict', only_count=True,
                                                    Post={'room_type_title': 'Standard'})
    if result['status'] == settings.POSITIVE:
        context['standard'] = result['count']

    return render(request, "pages/_standard_details.html", context)


def booking_view(request):
    context = {'messages': [], 'final_status': False}

    if 'type'in request.GET:
        context['room_type'] = request.GET['type']
        if request.method == 'POST':
            result = base.book().book(request.POST)
            if result['status'] == settings.NEGATIVE:
                context['messages'].extend(result['messages'])
            else:
                context['messages'].append('Reservation request sent. Room type: '+ result['room_type'])
                context['final_status'] = True
    else:
        return redirect('home')

    context['messages_count'] = len(context['messages'])

    return render(request, "pages/booking.html", context)
