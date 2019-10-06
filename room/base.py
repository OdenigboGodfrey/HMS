from datetime import date

from HMS import settings
from .models import *
from django.db.models import Q
import hashlib
from django.conf import settings
from django.shortcuts import get_object_or_404
from staff.models import employee, department, position, admin_conversation
from django.db.models import Count
import staff.base as staff_base


PASSWORD_SALT = '$.2@7!29^Bc;a)f2:144f6$@_)5196b01.%6.FdD04dA0%'


class chat:
    def get_admin_with_least_conversation(self, Post):
        """

        :post_requirements: [**admins]
        :param type:  all='get all rooms', strict='get only free rooms'
        :param only_count: only Return the number of rooms
        :return:
        """
        data = utilities().init_data()
        try:
            admin_conversation_object = admin_conversation.objects.filter(employee__active=1).order_by('-conversations')
            if admin_conversation_object is not None and len(admin_conversation_object) > 0:
                if 'admins' in Post:
                    for admin in admin_conversation_object:
                        if admin.employee.pk in Post['admins']:
                            """ 
                                if current admin is in list of admins admins 
                                currently on shift send message to that admin 
                            """
                            data['admin_object'] = admin
                            break
                    if 'admin_object' not in data:
                        """ if failed, select most active admin and send message to."""
                        data['admin_object'] = admin_conversation_object.last()
                else:
                    raise Exception()
        except Exception as e:
            data = utilities().error(data, error=e)

        return utilities().return_data(data)

    def get_an_admin(self):
        data = utilities().init_data()
        admins = []
        try:
            """ get the attendance for today """
            result = staff_base.hotel_admin().get_attendance()
            if result['status'] != settings.NEGATIVE:
                for staff in result['attendance_object']:
                    if staff.employee.auth_level == settings.LEVELS['front_desk'] and staff.check_out is None:
                        """ only append admins who are at work """
                        admins.append(staff.employee.pk)
            if len(admins) > 0:
                result = self.get_admin_with_least_conversation({'admins': admins})
            else:
                result = self.get_admin_with_least_conversation({'admins': []})

            if result['status'] != settings.NEGATIVE:
                data['admin_object'] = result['admin_object']
                result = staff_base.hotel_room().conversation_counter({'employee_id': data['admin_object'].pk})
            #     do sth with result
            else:
                data['messages'].extend(result['messages'])
        except Exception as e:
            data = utilities().error(data, error=e)

        return utilities().return_data(data)

    def send(self, Post):
        """
        function used to send chat messages
        :post_requirements: [room_no, booking, user_type('staff','room')]
        :param Post: dictionary containing the needing data 
        :return: dictionary 
        """
        data = utilities().init_data()
        try:
            """ 
                check if convo has already started, if yes get previous admin
                unless current message was sent by an admin
            """

            employee_object = None
            try:
                if 'employee' in Post:
                    employee_object = employee.objects.get(pk=Post['employee'])

                if 'user_type' in Post and Post['user_type'] == "staff":
                    """
                        if user is staff, staff only get to see room no, use room_no to get booking_id
                    """
                    booking_object = booking.objects.filter(room__room_no=Post['room_no'], check_out_date=None).first()
                else:
                    booking_object = booking.objects.get(pk=Post['booking'])

                message_object = message.objects.filter(
                    booking=booking_object).order_by('-id').first()
                if message_object is not None and employee_object is not None:
                    employee_object = message_object.employee
                    print('end')
                else:
                    raise Exception()
            except Exception as e:
                print(e, '1')
                result = self.get_an_admin()
                print(result)
                if result['status'] != settings.NEGATIVE:
                    employee_object = result['admin_object'].employee
                elif result['status'] == settings.NEGATIVE or employee_object is None:
                    raise Exception()

            room_object = room.objects.get(room_no=Post['room_no'])

            message_object = message()
            message_object.message = Post['message']
            message_object.employee = employee_object
            message_object.booking = booking_object
            message_object.room = room_object

            print(message_object.booking)
            print(message_object.employee)

            if Post['user_type'] == "staff":
                """
                    sent_by, where e:employee and b:booking
                """
                message_object.sent_by = 'e_' + str(message_object.employee.pk)
            elif Post['user_type'] == "room":
                message_object.sent_by = 'b_' + str(message_object.booking.pk)
            else:
                raise Exception()
            message_object.status = 0  # not seen
            
            message_object.save()

        except Exception as e:
            print(e, '2')
            data = utilities().error(data, "Failed to send message.", e)
            
        return utilities().return_data(data)
    
    def get_messages(self, Post, new_to_old=True, type="all"):
        """

        :post_requirements: [(booking(booking_id) || **room), **user_type]
        :param Post: 
        :param new_to_old: sorting order
        :param type: dictionary
        :return: 
        """
        data = utilities().init_data(post_extras={'chat_messages': [], 'chat_count': 0})
        try:
            if 'user_type' in Post and Post['user_type'] == "staff":
                """
                    if user is staff, staff only get to see room no, use room_no to get booking_id
                """
                booking_object = booking.objects.filter(room__room_no=Post['room_no'], check_out_date=None).first()
                if booking_object is not None:
                    Post['booking'] = booking_object.pk
                else:
                    raise Exception()

            if new_to_old:
                message_objects = message.objects.filter(booking=Post['booking']).order_by(
                    '-id')
            else:
                message_objects = message.objects.filter(booking=Post['booking']).order_by(
                    'id')

            print(message_objects)

            if message_objects is not None and len(message_objects) > 0:
                for message_object in message_objects:
                    subcontent = {
                        'message': message_object,
                        'time': utilities().get_validated_time(message_object.created_at),
                        'sent_by': message_object.sent_by
                        }

                    sent_by = str(message_object.sent_by)
                    if Post['user_type'] == "room" and sent_by[0] == 'b':
                        subcontent['sent_by'] = int(str(message_object.sent_by)[2::])
                    elif Post['user_type'] == "staff" and sent_by[0] == 'e':
                        if int(sent_by[2::]) == message_object.employee.pk:
                            """
                                if message is sent by this admin, set the snt_by value to be admin's id
                            """
                            subcontent['sent_by'] = int(str(message_object.sent_by)[2::])
                    data['chat_messages'].append(subcontent)
                    if type == "single":
                        break
                data['chat_count'] = len(message_objects)
            else:
                raise Exception()
        except Exception as e:
            print(e)
            data = utilities().error(data, "Failed to get messages.", e)

        return utilities().return_data(data)

    def get_recent(self, Post, type='all'):
        """
        function gets the most recent messages from the last_chat_id(pk) sent with the param 'Post'
        :post_requirements: [last_chat_id, booking]
        :param Post: dictionary
        :param type: message type('all', 'single')
        :return: dictionary
        """
        data = utilities().init_data(post_extras={'chat_messages': [], 'chat_count': 0})

        try:
            message_objects = message.objects.filter(~Q(pk__range=(1, int(Post['last_chat_id']))),
                                                     booking=Post['booking']).order_by('-id')

            if message_objects is not None and len(message_objects) > 0:
                for message_object in message_objects:
                    subcontent = {'message': message_object}
                    data['chat_messages'].append(subcontent)
                    if type == "single":
                        break
                data['chat_count'] = len(message_objects)
            else:
                raise Exception()
        except Exception as e:
            data = utilities().error(data, "Failed to get messages.", e)
        return utilities().return_data(data)

    def list(self, Post):
        """
        function gets the list of all other users this current user has messaged
        :post_requirements: [user_type('room', 'staff'), employee]
        :param Post: dictionary
        :return: dictionary containing chat_messages
        """
        data = utilities().init_data(post_extras={'chat_list': [], 'chat_count': 0})

        try:

            if Post['user_type'] == 'room':
                chat_list_object = message.objects.filter(booking=Post['booking']).values(
                    'employee', 'booking').annotate(count=Count('employee'))
            if Post['user_type'] == 'staff':
                chat_list_object = message.objects.filter(employee=Post['employee']).\
                    values('room__room_no').annotate(count=Count('room__room_no'))

            if chat_list_object is not None:
                for child in chat_list_object:
                    if child['room__room_no'] not in data['chat_list']:
                        data['chat_list'].append(child['room__room_no'])
            else:
                raise Exception()
        except Exception as e:
            data = utilities().error(data, "Failed to get message list.", e)

        print(data)
        return utilities().return_data(data)


class room_base:
    def login(self, Post):
        """
        :post_requirements: [room_no, password]
        :param Post:
        :return:
        """
        data = utilities().init_data()
        try:
            booking_object = booking.objects.filter(room__room_no=Post['room_no'],
                                                    check_out_date=None).first()
            if booking_object is not None and booking_object:

                if booking_object.password == utilities().hash(Post['password']):
                    data['booking_object'] = booking_object
                else:
                    raise Exception('Incorrect password.')
            else:
                raise Exception('Invalid login info.')
        except Exception as e:

            data = utilities().error(data, str(e))

        return utilities().return_data(data)

    def get_booking_info(self, Post):
        """
        :post_requirements: [booking_id]
        :param Post:
        :return:
        """
        data = utilities().init_data()

        try:
            data['booking_object'] = booking.objects.get(pk=Post['booking_id'])
        except:
            data = utilities().error(data, str(e))

        return utilities().return_data(data)


class utilities:
    def hash(self, content):
        return hashlib.md5(
            PASSWORD_SALT.encode() + (hashlib.sha1(content.encode()).hexdigest()).encode()).hexdigest()

    def init_data(self, post_extras={}):
        dict = {'messages': [], 'status': settings.NEUTRAL}

        if len(post_extras) > 0:
            dict.update(post_extras)

        return dict

    def return_data(self, dict, post_extras={}, success_message="Action Successful."):
        if len(post_extras) != 0:
            dict.update(post_extras)

        dict['messages_count'] = len(dict['messages'])

        if dict['messages_count'] == 0:
            dict['messages'].append(success_message)

        """ update messages count """
        dict['messages_count'] = len(dict['messages'])

        """ send positive  back if no error """
        if dict['status'] != settings.NEGATIVE:
            dict['message_type'] = dict['status']

        return dict
    
    def error(self, dict, error_message="An error occurred. Please try again later", error=None, extra={}):
        if len(extra) > 0:
            dict.update(extra)

        dict['status'] = settings.NEGATIVE
        dict['messages'].append(error_message)
        if error is not None:
            dict['error'] = str(error)

        """ send negative back if no error """
        dict['message_type'] = dict['status']
        if error is not None:
            print(error)
        return dict

    def get_validated_time(self, passed_date_time):
        result = ''
        now = datetime.now()
        passed_date_time_format = passed_date_time.strftime('%Y%m%d')
        now_format = now.strftime('%Y%m%d')

        passed_date_time_year = passed_date_time.isocalendar()[0]
        now_year = now.isocalendar()[0]
        passed_date_time_week = passed_date_time.isocalendar()[1]
        now_week = now.isocalendar()[1]

        if passed_date_time_format == now_format:
            result = passed_date_time.strftime("%H:%M")
        else:
            #  same week
            if passed_date_time.strftime("%Y%m") == now.strftime("%Y%m") and now_week == passed_date_time_week:
                result = passed_date_time.strftime("%a, %H:%M")
            #  different weeks same month
            elif passed_date_time.strftime("%Y%m") == now.strftime("%Y%m") and now_week > passed_date_time_week:
                result = passed_date_time.strftime("%b %d, %H:%M")
            #  different months
            elif passed_date_time_format != now_format:
                #  same year
                if passed_date_time_year == now_year:
                    result = passed_date_time.strftime("%b %d, %H:%M")
                else:
                    result = passed_date_time.strftime("%Y %b %d, %H:%M")
        return result

