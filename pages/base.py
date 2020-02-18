from django.conf import settings
from HMS import settings
from .models import *
from room.models import user_information
from staff import base as staff_base


class book:
    def book(self, Post):
        data = {'messages': [], 'status': settings.POSITIVE}
        try:
            result = staff_base.hotel_room().handle_user_information({'phone': Post['phone'],
                                                                      'full_name': Post['full_name'],
                                                                      'email': Post['email'],
                                                                      'NKName': Post['name'],
                                                                      'NKphone': Post['n_phone']})
            print(result)
            if result['status'] == settings.NEGATIVE:
                data['messages'].extend(result['messages'])
            elif result['status'] == settings.POSITIVE:

                result = self.save_reservation(Post, extra={'user_info_object': result['user_info_object']})
                print(result)
                if result['status'] == settings.NEGATIVE:
                    data['messages'].extend(result['messages'])
                elif result['status'] == settings.POSITIVE:
                    data['room_type'] = result['room_type']
        except Exception as e:
            data = utilities().error(data, error=e)

        return utilities().return_data(data)

    def save_reservation(self, Post, user_info_id=0, extra={}):
        data = {'messages': [], 'status': settings.POSITIVE}
        try:
            type = 'n/a'
            result = staff_base.hotel_room().get_room_types()

            if result['status'] == settings.POSITIVE:
                for child in result['room_types']:
                    if Post['room_type'] in child.type.lower():
                        type = child.type
                        data['room_type'] = type

            if 'user_info_object' in extra:
                user_info_object = extra['user_info_object']
            else:
                if user_info_id != 0:
                    user_info_object = user_information.objects.get(pk=user_info_id)
                else:
                    user_info_object = user_information.objects.get(pk=Post['user_info_id'])

            public_booking_object = public_booking()
            public_booking_object.proposed_check_in_date = Post['check_in']
            public_booking_object.proposed_check_out_date = Post['check_out']
            public_booking_object.user = user_info_object
            public_booking_object.room_type = type
            public_booking_object.adults = Post['adults']
            public_booking_object.children = Post['children']
            public_booking_object.save()

        except Exception as e:
            print(e)
            data = utilities().error(data, error=e)

        return utilities().return_data(data)


class contact:
    def contact_us(self, Post):
        data = {'messages': [], 'status': settings.POSITIVE}
        try:
            contact_object = public_contact()
            contact_object.content = Post['content']
            contact_object.full_name = Post['name']
            contact_object.email = Post['email']

            contact_object.save()
        except Exception as e:
            data = utilities().error(data, "Failed to save information, please try again later.", error=e)

        return utilities().return_data(data)


class utilities:

    def return_data(self, dict, post_extras={}, success_message="Action Successful."):
        if len(post_extras) != 0:
            dict.update(post_extras)

        dict['messages_count'] = len(dict['messages'])

        if dict['messages_count'] == 0:
            dict['messages'].append(success_message)

        return dict

    def error(self, dict, error_message="An error occurred. Please try again later", error=None, extra={}):
        if len(extra) > 0:
            dict.update(extra)

        dict['status'] = settings.NEGATIVE
        dict['messages'].append(error_message)
        if error is not None:
            dict['error'] = str(error)

        return dict
