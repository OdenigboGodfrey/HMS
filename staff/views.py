from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import request
from room.models import *
from .models import *
from room.models import room as hotel_room
from django.db.models import Q
from. import  base
from django.conf import settings
from HMS import settings
from django.db import IntegrityError
from django.db.models import Q
from room import base as room_base

N = 6


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
        # context['message_type'] = result['message_type']
        context.update({'message_type': result['message_type']})
    else:
        context.update({'message_type': settings.NEUTRAL})
    # dict.update({
    #     'message_type': result['message_type'],
    # })


def home_view(request):
    context = {'messages': []}
    if not basic_details(request, context):
        return redirect('staff:login')

    context['booked_rooms_count'] = base.hotel_room().get_booked_rooms(only_count=True)['booked_rooms_count']
    context['free_rooms_count'] = base.hotel_room().get(type="strict", only_count=True)['rooms_count']
    context['all_rooms_count'] = base.hotel_room().get(only_count=True)['rooms_count']
    context['reservations_count'] = base.hotel_room().get_reservations(only_count=True)['reservations_count']

    return render(request, 'staff/index.html', context)


def basic_details(request, context):
    if 'admin_id' not in request.session:
        """ if admin is not signed in, """
        return False
    """ will be used to ad basic info that will be need generally to each context"""
    context.update(
        {
            'level': settings.LEVELS,
            'auth_level': request.session['auth_level'],
            'first_dept': str(list(settings.DEPARTMENTS.keys())[0]),
            'user_type': 'staff',
            'positive': settings.POSITIVE,
            'negative': settings.NEGATIVE,
            'neutral': settings.NEUTRAL,
        })
    return True


def book(request, type):
    """
    for booking and checking user in
    """
    context = {'messages': []}
    if not basic_details(request, context):
        return redirect('staff:login')

    if type == 'now':
        if request.method == 'POST':
            result = base.hotel_room().book(request.session['admin_id'], request.POST)
            if result['status'] == settings.NEGATIVE:
                context['messages'].extend(result['messages'])

        context['password'] = base.utilities().generate_password(N)
        """ get room information """
        result = base.hotel_room().get(type="strict")
        if result['status'] != settings.NEGATIVE:
            context['rooms'] = result['rooms']

        context['messages_count'] = result['messages_count']

        """ update context based on result """
        update_context(context, result)

        return render(request, 'reception/booking.html', context)

    elif type == 'reserve':
        context['password'] = base.utilities().generate_password(N)
        if 'pb_id' in request.GET:
            context['pb'] = request.GET['pb_id']

            result = base.hotel_room().get_public_reservation_by_id({'pb_id': request.GET['pb_id']})
            if result['status'] != settings.NEGATIVE:
                context['public_booking_object'] = result['public_booking_object']

                """ get room information """
                result = base.hotel_room().get(type="strict", Post={
                    'room_type_title': context['public_booking_object'].room_type
                })

                if result['status'] != settings.NEGATIVE:
                    context['rooms'] = result['rooms']
                else:
                    context['room_type'] = context['public_booking_object'].room_type
                    context['messages'].extend(result['messages'])

            elif result['status'] == settings.NEGATIVE:
                context['messages'].extend(result['messages'])

            update_context(context, result)
        else:
            """ get room information """
            result = base.hotel_room().get(type="strict")
            if result['status'] != settings.NEGATIVE:
                context['rooms'] = result['rooms']

        if request.method == 'POST':
            result = base.hotel_room().book(request.session['admin_id'], request.POST)
            if result['status'] == settings.NEGATIVE:
                context['messages'].extend(result['messages'])

            update_context(context, result)
        return render(request, 'reception/reservation.html', context)

    elif type == 'take':
        if request.method == 'POST':
            result = base.hotel_room().take_my_reservation(request.session['admin_id'], request.POST)
            if result['status'] == settings.NEGATIVE:
                context['messages'].extend(result['messages'])
        return render(request, 'reception/take-reservation.html', context)

    elif type == 'public-reservations':
        result = base.hotel_room().public_reservations()
        if result['status'] != settings.NEGATIVE:
            context['public_booking_object'] = result['public_booking_object']
            context['count'] = result['count']
        else:
            context['messages'].extend(result['messages'])

        update_context(context, result)
        return render(request, 'hms-admin/public_reservations.html', context)
    else:
        return redirect('staff:homepage')


def check_in(request):
    context = {'messages': []}
    if not basic_details(request, context):
        return redirect('staff:login')

    result = base.hotel_room().get_booked_rooms()
    if result['status'] != settings.NEGATIVE:
        context['booking_object'] = result['booking_object']

    update_context(context, result)
    return render(request, 'hms-admin/checkin_list.html', context)


def check_out(request):
    context = {'messages': []}
    if not basic_details(request, context):
        return redirect('staff:login')

    if request.method == 'POST':
        try:
            """
            for checking out customers
            """
            room_object = room.objects.get(room_no=request.POST['room_no'])
            booking_object = booking.objects.filter(~Q(check_in_date=None), room=room_object, check_out_date=None).first()
            if booking_object is not None or booking_object:
                booking_object.check_out_date = datetime.now()
                booking_object.check_out_action_by = employee.objects.get(pk=request.session['admin_id'])

                booking_object.save()

                """after checking out add this room to free rooms """
                result = base.hotel_room().release_room({'room_object': room_object})
                if result['status'] == settings.NEGATIVE:
                    context['messages'].append("Failed to free up room, please contact admin. Room no: " +
                                               request.POST['room_no'] + ".")
                else:
                    context['messages'].append("Checked out " + request.POST['room_no'] + " successfully.")
                    context['message_type'] = settings.POSITIVE
            else:
                raise Exception()
        except Exception as e:
            print(e)
            context['messages'].append("Failed to checkout room " + request.POST['room_no'] + ".")
            context['message_type'] = settings.NEGATIVE

    # result = base.hotel_room().get_booked_rooms()
    # if result['status'] != settings.NEGATIVE:
    #     context['booking_object'] = result['booking_object']

    return render(request, 'reception/checkout.html', context)


def reservations(request):
    context = {'messages': []}
    if not basic_details(request, context):
        return redirect('staff:login')

    result = base.hotel_room().get_reservations()
    if result['status'] != settings.NEGATIVE:
        context['reservations'] = result['reservations']
        context['total'] = result['total']

    update_context(context, result)
    return render(request, 'hms-admin/reservation_list.html', context)


def staff_attendance(request, type):
    context = {'messages': []}

    if not basic_details(request, context):
        return redirect('staff:login')

    attendance_today_url = reverse('staff:staff-attendance'
                               ,current_app=request.resolver_match.namespace,
                               kwargs={'type': 'today'})

    if type == 'in':
        if request.method == 'POST':
            result = base.hotel_admin().attendance_signin(request.POST)
            print(result)
            if result['status'] != settings.NEGATIVE:
                return redirect(attendance_today_url)

            update_context(context, result)
        return render(request, 'staff/attendance_signin.html', context)

    elif type == "today":
        result = base.hotel_admin().get_attendance()
        if result['status'] != settings.NEGATIVE:
            """ if any messages are sent with the result append """
            if result['messages_count'] > 0:
                context['messages'].extend(result['messages'])
            context['attendance_object'] = result['attendance_object']
        else:
            context['messages'].extend(result['messages'])
        update_context(context, result)
        return render(request, 'staff/attendance.html', context)

    elif type == "out":
        if request.method == 'POST':
            result = base.hotel_admin().attendance_signout(request.POST)
            if result['status'] != settings.NEGATIVE:
                return redirect(attendance_today_url)

            update_context(context, result)

        return render(request, 'staff/attendance_signout.html', context)


def login(request):
    level = 5
    context = {'messages': [], 'auth_level': level}
    if 'admin_id' in request.session:
        return redirect('staff:homepage')

    if request.method == 'POST':
        result = base.hotel_admin().login(request.POST)
        if result['status'] != settings.NEGATIVE:
            """ 
                'val' = the numeric representation of the auth level 
                settings.LEVELS['Admin']['val']
                e.g if result['employee'].auth_level == settings.LEVELS['Admin']['val']:
             #     this is an admin if positive
                 
             """
            request.session['full_name'] = result['employee'].full_name
            request.session['email'] = result['employee'].email
            request.session['admin_id'] = result['employee'].pk
            request.session['position'] = result['employee'].position
            request.session['department'] = result['employee'].department
            request.session['auth_level'] = result['employee'].auth_level
            return redirect('staff:homepage')
        elif result['status'] == settings.NEGATIVE:
            update_context(context, result)

    return render(request, 'staff/staff-signin.html', context)


def logout(request):
    if 'admin_id' in request.session:
        del request.session['full_name']
        del request.session['email']
        del request.session['admin_id']
        del request.session['auth_level']

    return redirect('staff:login')


def expenses(request, type):
    context = {'messages': []}

    if not basic_details(request, context):
        return redirect('staff:login')

    if type == "add":
        if request.method == 'POST':
            result = base.hotel_management().add_expense(request.session['admin_id'], request.POST)
            if result['status'] == settings.NEGATIVE:
                context['messages'].extend(result['messages'])
            update_context(context, result)
        return render(request, 'hms-admin/add_expenses.html', context)

    elif type == "today":
        result = base.hotel_management().get_expense()
        if result['status'] == settings.NEGATIVE:
            context['messages'].extend(result['messages'])
        else:
            context['expense_object'] = result['expense_object']
            context['expense_total'] = result['total']

        return render(request, 'hms-admin/admin_expenses.html', context)


def inventory(request, type):
    context = {'messages': []}

    if not basic_details(request, context):
        return redirect('staff:login')

    if type == 'add':
        if request.method == 'POST':
            """ adds new inventory """
            result = base.hotel_inventory().add(request.session['admin_id'], request.POST)
            if not result['status']:
                context['messages'].extend(result['messages'])
            context['messages_count'] = result['messages_count']

            update_context(context, result)
        return render(request, 'hms-admin/add_inventory.html', context)
    elif type == 'view':
        result = base.hotel_inventory().get_inventory()
        if result['status'] != settings.NEGATIVE:
            context['inventory_object'] = result['inventory_object']

        update_context(context, result)
        return render(request, 'hms-admin/inventory.html', context)


def create(request, type):
    context = {'messages': []}

    if not basic_details(request, context):
        return redirect('staff:login')

    if type == 'room':
        if request.method == 'POST':
            result = base.hotel_room().add(request.session['admin_id'], request.POST)
            if result['status'] == settings.NEGATIVE:
                context['messages'].extend(result['messages'])
                context['messages_count'] = result['messages_count']

        result = base.hotel_room().get_room_types()
        if result['status'] != settings.NEGATIVE:
            context['room_types'] = result['room_types']

        update_context(context, result)
        return render(request, 'hms-admin/add_room.html', context)

    elif type == 'staff':
        if request.method == 'POST':
            result = base.hotel_admin().create_staff(request.session['admin_id'], request.POST)
            if result['status'] == settings.NEGATIVE:
                context['messages'].extend(result['messages'])

            update_context(context, result)

        context['departments'] = settings.DEPARTMENTS
        context['positions'] = settings.POSITIONS

        return render(request, 'hms-admin/add_staff.html', context)

    elif type == 'room_type':
        if request.method == 'POST':
            result = base.hotel_room().set_room_types(request.session['admin_id'], request.POST)
            if result['status'] == settings.NEGATIVE:
                context['messages'].extend(result['messages'])

        update_context(context, result)
        return render(request, "hms-admin/room_type.html", context)

    else:
        return redirect('staff:homepage')


def order(request, type):
    context = {'messages': []}

    if not basic_details(request, context):
        return redirect('staff:login')
    if type == 'add':
        if request.method == 'POST':
            result = base.hotel_room().booking_order(request.session['admin_id'],
                                                     request.POST)
            if result['status'] == settings.NEGATIVE:
                context['messages'].extend(result['messages'])

        result = base.hotel_room().get_booked_rooms()
        if result['status'] != settings.NEGATIVE:
            context['booking'] = result['booking_object']

        result = base.hotel_inventory().get_inventory()
        if result['status'] != settings.NEGATIVE:
            context['inventory_object'] = result['inventory_object']

        update_context(context, result)
        return render(request, "hms-admin/place_order.html", context)
    elif type == 'view':
        result = base.hotel_management().get_revenue(type='all')
        print(result)
        if result['status'] != settings.NEGATIVE:
            context['revenue_object'] = result['revenue_object']
            context['revenue_total'] = result['total']

        update_context(context, result)
        return render(request, "hms-admin/admin_revenues.html", context)
    else:
        return redirect('staff:homepage')


def room_management(request, type):
    context = {'messages': []}

    if not basic_details(request, context):
        return redirect('staff:login')

    if type == 'view':
        if 'strict' in request.GET:
            result = base.hotel_room().get(type="strict")
        else:
            result = base.hotel_room().get()

        if result['status'] != settings.NEGATIVE:
            context['rooms'] = result['rooms']
        else:
            context['messages'].extend(result['messages'])

        update_context(context, result)
        return render(request, 'hms-admin/room_management.html', context)


def salary(request, type):
    context = {'messages': []}

    if not basic_details(request, context):
        return redirect('staff:login')

    if type == 'add':
        if request.method == 'POST':
            result = base.hotel_management().add_salary(request.session['admin_id'], request.POST)
            if result['status'] == settings.NEGATIVE:
                context['messages'].extend(result['messages'])
            else:
                context['messages'].append('Action Successful.')
            context['message_type'] = result['status']

        result = base.hotel_admin().get_staff()
        if result['status'] != settings.NEGATIVE:
            context['employee_objects'] = result['employee_objects']

        context['departments'] = settings.DEPARTMENTS

        # update_context(context, result)
        return render(request, 'hms-admin/add_salaries.html', context)
    elif type == 'view':
        result = base.hotel_management().get_salary_payment()

        if result['status'] != settings.NEGATIVE:
            context['salary_object'] = result['salary_object']

        update_context(context, result)
        return render(request, 'hms-admin/admin_salaries.html', context)
    else:
        return redirect('staff:homepage')


def revenue(request, type):
    context = {'messages': []}

    if not basic_details(request, context):
        return redirect('staff:login')

    if type == 'view':
        result = base.hotel_management().get_revenue()
        if result['status'] != settings.NEGATIVE:
            context['revenue_object'] = result['revenue_object']
            context['revenue_total'] = result['total']
        else:
            context['messages'].extend(result['messages'])

        update_context(context, result)
        return render(request, 'hms-admin/admin_revenues.html', context)
    else:
        return redirect('staff:homepage')


def chat(request, type):
    context = {'messages': [], 'base_page': 'staff/base.html'}

    if not basic_details(request, context):
        return redirect('staff:login')

    if type == 'list':
        result = room_base.chat().list({'employee': request.session['admin_id'], 'user_type': context['user_type']})
        if result['status'] != settings.NEGATIVE:
            context['chat_list'] = result['chat_list']

        update_context(context, result)
        return render(request, 'hms-admin/chat_list.html', context)
    elif type == 'fetch':
        if 'room_no' in request.GET:
            context['admin_id'] = request.session['admin_id']
            context['room_no'] = request.GET['room_no']
            result = room_base.chat().get_messages({'room_no': request.GET['room_no'], 'user_type': context['user_type']})
            if result['status'] != settings.NEGATIVE:
                context['chat_messages'] = result['chat_messages']

            context['url'] = reverse('staff:chat'
                                     , current_app=request.resolver_match.namespace,
                                     kwargs={'type': 'send'}) + "?room_no=" + request.GET['room_no']

            update_context(context, result)
            return render(request, 'room/message.html', context)
        return redirect('staff:homepage')
    elif type == "send":
        if request.method == 'POST':
            if 'room_no' in request.GET:
                result = room_base.chat().send(request.POST)
                if result['status'] == settings.NEGATIVE:
                    context['messages'].extend(result['messages'])
                chat_list_url = reverse('staff:chat'
                                        , current_app=request.resolver_match.namespace,
                                        kwargs={'type': 'fetch'}) + "?room_no=" + request.GET['room_no']
                return redirect(chat_list_url)
        return redirect('staff:homepage')


def pcu(request):
    context = {'messages': []}

    if not basic_details(request, context):
        return redirect('staff:login')

    if 'pcu_id' in request.GET:
        result = base.hotel_admin().mark_public_contact_data(request.GET['pcu_id'])
        if result['status'] != settings.NEGATIVE:
            context['messages'].extend(result['messages'])

    result = base.hotel_admin().get_public_contact_data()
    if result['status'] != settings.NEGATIVE:
        context['public_contact_object'] = result['public_contact_object']

    update_context(context, result)
    return render(request, 'hms-admin/pcu.html', context)


def sm(request, type):
    context = {'messages': []}

    if not basic_details(request, context):
        return redirect('staff:login')

    if type == 'view':
        result = base.hotel_admin().get_staff()
        print(result)
        if result['status'] != settings.NEGATIVE:
            context['employee_objects'] = result['employee_objects']
        update_context(context, result)

        return render(request, 'hms-admin/staff_management.html', context)
    else:
        return redirect('staff:homepage')

