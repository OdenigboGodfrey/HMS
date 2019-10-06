from django.shortcuts import render, redirect
from django.http import request
from .models import *
from . import base
import hashlib
from django.db.models import Q
from django.conf import settings
from HMS import settings
from django.urls import reverse

app_name = 'room'
PASSWORD_SALT = '$.2@7!29^Bc;a)f2:144f6$@_)5196b01.%6.FdD04dA0%'


def hash(content):
    return hashlib.md5(
        PASSWORD_SALT.encode() + (hashlib.sha1(content.encode()).hexdigest()).encode()).hexdigest()


def is_slice_in_list(new_array, old_array):
    """ used to check if new array is in old array"""
    len_s = len(new_array) #  so we don't recompute length of new on every iteration
    return any(new_array == old_array[i:len_s+i] for i in range(len(old_array) - len_s+1))


def update_context(context, result):
    """
    function is used to update the context with general details from the result variable
    :param dict: view context
    :param result: the returned value from model action
    :return:
    """
    if not is_slice_in_list(result['messages'], context['messages']):
        context['messages'].extend(result['messages'])
    if 'messages_count' in result:
        context['messages_count'] = result['messages_count']
    else:
        context['messages_count'] = len(result['messages'])
    if 'message_type' in result:
        context.update({
            'message_type': result['message_type'],
        })
    else:
        context.update({
            'message_type': settings.NEUTRAL,
        })


def basic_details(request, context):
    if 'booking_id' not in request.session:
        """ if admin is not signed in, """
        return False
    """ will be used to ad basic info that will be need by each context"""
    context.update({'room_no': request.session['room_no'], 'booking': request.session['booking_id'], 'user_type': 'room'})
    return True


def room_index_view(request):
    context = {'messages': []}
    if not basic_details(request, context):

        return redirect('room:login')
    result = base.room_base().get_booking_info({'booking_id': request.session['booking_id']})

    if result['status'] != settings.NEGATIVE:
        context['booking_object'] = result['booking_object']

    update_context(context, result)
    return render(request, "room/index.html", context)


def login(request):
    context = {'messages': []}

    action = False

    # if request.method == 'GET':
    #     if 'login' in request.GET:
    #         result = base.room_base().login(request.GET)
    #         action = True
    if request.method == 'POST':
        result = base.room_base().login(request.POST)
        action = True

    if action:
        if result['status'] == settings.NEGATIVE:
            update_context(context, result)

        elif result['status'] != settings.NEGATIVE:
            request.session['booking_id'] = result['booking_object'].pk
            request.session['room_no'] = result['booking_object'].room.room_no
            request.session['full_name'] = result['booking_object'].user.full_name
            request.session['check_in_date'] = str(result['booking_object'].check_in_date)
            return redirect('room:room')

        else:
            context['messages'].append("An error occurred.")
    return render(request, 'room/signin.html',  context)


def logout(request):
    if 'booking_id' in request.session:
        del request.session['booking_id']
        del request.session['room_no']
        del request.session['full_name']
        del request.session['check_in_date']

    return redirect('room:room')


def room_chat(request, type):
    context = {'messages': [], 'base_page': 'room/base.html'}
    if not basic_details(request, context):

        return redirect('room:login')

    if type == "send":
        action = False
        # if request.method == 'GET':
        #     result = base.chat().send(request.GET)
        #     action = True
        if request.method == 'POST':
            result = base.chat().send(request.POST)
            action = True

        if action:
            if result['status'] == settings.NEGATIVE:
                context['messages'].extend(result['messages'])
        room_url = reverse('room:chat',
                           current_app=request.resolver_match.namespace,
                           kwargs={'type': 'fetch'})
        return redirect(room_url)
    elif type == "fetch":
        result = base.chat().get_messages({'booking': request.session['booking_id'], 'user_type': context['user_type']})

        if result['status'] == settings.NEGATIVE:
             context['messages'].extend(result['messages'])
        else:
            context['chat_messages'] = result['chat_messages']
        context['booking'] = int(request.session['booking_id'])
        context['url'] = reverse('room:chat'
                               ,current_app=request.resolver_match.namespace,
                               kwargs={'type': 'send'})
        return render(request, "room/message.html", context)

