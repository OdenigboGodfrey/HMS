from datetime import date, time
from .models import *
from room.models import *
import random
import string
from django.db.models import Q
import hashlib
from django.conf import settings
from HMS import settings
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
import os
from pages.models import *


APP_NAME = 'staff'
PASSWORD_SALT = '$.2@7!29^Bc;a)f2:144f6$@_)5196b01.%6.FdD04dA0%'


class hotel_inventory:

    def add(self, Id, Post):
        """
        
        :post_requirements: [item_name, item_type, quantity]
        :param Id: The Admin Id
        :return: dictionary
        """
        data = utilities().init_data()
        try:
            employee_object = employee.objects.get(pk=Id)
            try:
                inventory_object = inventory.objects.filter(item_name=Post['item_name'],
                                                            item_type=Post['item_type']).first()
                if inventory_object is None or not inventory:
                    raise Exception()
            except:
                try:
                    inventory_object = inventory()
                    inventory_object.item_name = Post['item_name']
                    inventory_object.item_type = Post['item_type']
                    # inventory_object.quantity = Post['quantity']
                    inventory_object.save()

                    """ save log """
                    inventory_log_object = inventory_log()
                    inventory_log_object.item = inventory_object
                    inventory_log_object.action_by = employee_object
                    inventory_log_object.log_date = datetime.now()
                    inventory_log_object.log = employee_object.email + ' added a new item to the inventory.'
                    inventory_log_object.type = Post['item_type']

                    inventory_log_object.save()
                except Exception as e:
                    print(e)

            """ save quantity with a stock instance """
            result = self.add_to_stock(Id, {'quantity': Post['quantity'], 'inventory_id': inventory_object.pk})
            if result['status'] == settings.NEGATIVE:
                data['messages'].append("Failed to add to stocks. Please add manually.")

            data['status'] = settings.POSITIVE
        except Exception as e:
            data = utilities().error(data, 'Failed to save inventory item.')
        
        return utilities().return_data(data)

    def delete(self, item_id):
        """
        function deletes an unwanted item 
        :param item_id: items id 
        :return: dictionary 
        """
        data = utilities().init_data()
        try:
            inventory_object = inventory.objects.get(pk=item_id)
            inventory_object.status = -1

            inventory_object.save()

            data['status'] = settings.POSITIVE
        except:
            data = utilities().error(data, 'Failed to delete item.')
        
        return utilities().return_data(data)

    def edit(self, Id, item_id, Post):
        """
        
        :post_requirements: [item_name, item_type, status]
        :param Id: admin's id 
        :param item_id: items's id
        :param Post: 
        :return: 
        """
        
        data = utilities().init_data()
        logs = []

        try:
            employee_object = employee.objects.get(pk=Id)

            inventory_object = inventory.objects.get(pk=item_id)

            if Post['item_name'] and Post['item_name'] != inventory_object.item_name:
                logs.append(employee_object.email + " changed this item's name from "
                            + inventory_object.item_name + " to " + Post['item_name'])
                inventory_object.item_name = Post['item_name']

            if Post['item_type'] and Post['item_type'] != inventory_object.item_type:
                logs.append(
                    employee_object.email + " changed this item's type from " + inventory_object.item_type + " to " +
                    Post['item_type'])
                inventory_object.item_type = Post['item_type']

            if Post['status'] and int(Post['status']) != inventory_object.status:
                logs.append(
                    employee_object.email + " changed this item's status from " + inventory_object.status + " to " +
                    Post['status'])
                inventory_object.status = Post['status']

            # if Post['quantity'] and Post['quantity'] != inventory_object.quantity:
            #     logs.append(
            #         employee_object.email + " changed this item's quantity from " + inventory_object.quantity + " to " +
            #         Post['quantity'])
            #     inventory_object.quantity = Post['quantity']

            inventory_object.save()

            """ save logs """
            for log in logs:
                inventory_log_object = inventory_log()
                inventory_log_object.item_name = Post['item_name']
                inventory_log_object.action_by = employee_object
                inventory_log_object.log = log

                inventory_log_object.save()
            data['status'] = settings.POSITIVE
        except:
            data = utilities().error(data, error_message='Failed to edit item.')

        return utilities().return_data(data)

    def get_inventory(self):
        data = utilities().init_data({'inventory_object': []})

        try:
            inventory_object = inventory.objects.filter(status=0).order_by('-id')
            if inventory_object is not None and inventory_object:
                for child in inventory_object:
                    subcontent = {'inventory': child}
                    """ append stock information"""
                    result = self.get_stock(child.item_name)
                    if result['status'] != settings.NEGATIVE:
                        subcontent['stock'] = result['stock_object']
                    data['inventory_object'].append(subcontent)
                print(data['inventory_object'])
            else:
                raise Exception()
        except Exception as e:
            data = utilities().error(data, "Failed to get inventory items.")
        return utilities().return_data(data)

    def get_todays_stock(self):
        data = utilities().init_data()
        try:
            stock_object = stock.objects.filter(date__date=date.today()).order_by('-id')
            if stock_object is not None and len(stock_object) > 0:
                data['stocks'] = stock_object
                data['stock_count'] = len(stock_object)
            else:
                raise Exception()
        except:
            data = utilities().error(data, error_message="Failed to get today's stocks.")

        return utilities().return_data(data)

    def get_all_stock(self):
        data = utilities().init_data()
        try:
            stock_object = stock.objects.all().order_by('-id')
            if stock_object is not None and len(stock_object) > 0:
                data['stocks'] = stock_object
                data['stock_count'] = len(stock_object)
            else:
                raise Exception()
        except:
            data = utilities().error(data, 'Failed to get all stocks.')

        
        return utilities().return_data(data)

    def add_to_stock(self, Id, Post):
        """
        :post_requirements: [inventory_id, quantity]
        :param Id:
        :param Post:
        :return:
        """
        data = utilities().init_data()
        item_name = "item"
        try:

            """ get inventory info """
            inventory_object = inventory.objects.get(pk=Post['inventory_id'])
            item_name = inventory_object.item_name
            """ get employee info """
            employee_object = employee.objects.get(pk=Id)
            try:
                """ get last stock info for this inventory """
                previous_stock_object = stock.objects.filter(date__date=date.today(),
                                                             item=inventory_object).order_by('-id').first()
                if previous_stock_object is not None and previous_stock_object:
                    previous_stock_object = previous_stock_object.current
                else:
                    raise Exception()
            except:
                previous_stock_object = 0

            stock_object = stock()
            stock_object.item = inventory_object
            stock_object.action_by = employee_object
            stock_object.current = int(previous_stock_object) + int(Post['quantity'])
            stock_object.type = 1

            stock_object.save()
            data['status'] = settings.POSITIVE
        except Exception as e:
            print(e)
            data = utilities().error(data, "Failed to add to " + item_name + "'s stock.")
        
        return utilities().return_data(data)

    def get_stock(self, item):
        """
        gets the stock for the passed item
        :param item: str item's name
        :return: dictionary
        """
        data = utilities().init_data()

        try:
            item_object = inventory.objects.get(item_name=item)

            stock_object = stock.objects.filter(item=item_object).order_by('-id').first()
            if stock_object is not None and stock_object:
                data['stock_object'] = stock_object
            else:
                raise Exception()
        except:
            data = utilities().error(data,'Failed to get stock details for ' + item + ' .')
        
        return utilities().return_data(data)


class hotel_room:
    def add(self, Id, Post):
        """
        function to create a new hotel room
        :post_requirements: [type, room_no]
        :param Id:
        :param Post:
        :return:
        """

        data = utilities().init_data()
        try:
            employee_object = employee.objects.filter(pk=Id).first()
            room_type_object = room_type.objects.get(pk=Post['type'])

            room_object = room()
            room_object.type = room_type_object
            room_object.room_no = Post['room_no']
            room_object.price = room_type_object.price
            room_object. save()

            room_log_object = room_log()
            room_log_object.room = room_object
            room_log_object.log = employee_object.email + " added a new room. Price " + str(room_object.price)
            room_log_object.action_by = employee_object

            room_log_object.save()
            
            """ add new room to the number of total rooms for that type """
            room_type_object.no_of_rooms = room_type_object.no_of_rooms + 1
            room_type_object.free_rooms = room_type_object.free_rooms + 1
            
            room_type_object.save()

            data['status'] = settings.POSITIVE
        except IntegrityError as e:
            data = utilities().error(data, "Room number already exists.")

        except Exception as e:
            data = utilities().error(data, 'Failed to add new room.' + str(e))

        return utilities().return_data(data)

    def delete(self, Id, Post):
        """
        :post_requirements: [room_no]
        :param Id:
        :param Post:
        :return:
        """

        data = utilities().init_data()
        try:
            employee_object = employee.objects.filter(pk=Id).first()

            room_object = room.objects.filter(room_no=Post['room_no']).first()

            if employee_object is not None and len(employee_object) != 0 and \
                    room_object is not  None or len(room_object) != 0:
                room_object.status = -5
                room_object.save()

                room_log_object = room_log()
                room_log_object.room = Post['room_no']
                room_log_object.log = employee_object.email + " removed " + Post['room_no'] + "."
                room_log_object.action_by = employee_object

                room_log_object.save()

                data['status'] = settings.POSITIVE
            else:
                raise Exception()
        except:
            data = utilities().error(data, 'Failed to add new room.')
        
        return utilities().return_data(data)

    def edit(self, Id, Post):
        """
        function to edit a room
        :post_requirements: [room_no,type]
        :param Id: admin's id
        :param Post:
        :return: dictionary
        """

        data = utilities().init_data()
        logs = []
        try:
            employee_object = employee.objects.filter(pk=Id).first()

            room_object = room.objects.filter(room_no=Post['room_no']).first()
            if employee_object is not None and len(employee_object) != 0 and\
                    room_object is not None and len(room_object) != 0:

                """ check if this admin is changing the name and keep in log"""
                if Post['room_no'] and Post['room_no'] != room_object.room_no:
                    logs.append(employee_object.email + " changed this room's no from "
                                + room_object.room_no + " to " + Post['room_no'])
                    room_object.room_no = Post['room_no']
                if Post['type'] and Post['type'] != room_object.type:
                    logs.append(employee_object.email + " changed this room's type from "
                                + room_object.room_no + " to " + Post['room_no'])
                    room_object.type = Post['type']

                room_object.save()

                """ save logs """
                for log in logs:
                    room_log_object = room_log()
                    room_log_object.room = Post['room_no']
                    room_log_object.log = log
                    room_log_object.action_by = employee_object

                    room_log_object.save()

                data['status'] = settings.POSITIVE
            else:
                raise Exception()

        except:
            data = utilities().error(data, 'Failed to add new room.')
        
        return utilities().return_data(data)

    def set_room_types(self, Id, Post):
        """
        function to create rom type
        :post_requirements: [room_type, price, discount, **wifi, **breakfast]
        :param Id:
        :param Post:
        :return:
        """

        data = utilities().init_data()

        try:
            employee_object = employee.objects.get(pk=Id)

            room_type_object = room_type()

            room_type_object.type = Post['room_type']
            room_type_object.price = Post['price']
            room_type_object.discount = Post['discount']
            room_type_object.des
            room_type_object.action_by = employee_object

            room_type_object.save()

            """ save room services information too """

            if 'wifi' in Post:
                result = self.set_room_services(Id, {
                    'title': Post['wifi'],
                    'room_type_object': room_type_object,
                    'employee_object': employee_object
                })
                if result['status'] == settings.NEGATIVE:
                    data['messages'].extend(result['messages'])
                else:
                    data['messages'].append("Failed to add service '" + Post['service'] + "' to this room type.")

            if 'breakfast' in Post:
                result = self.set_room_services(Id, {
                    'title': Post['breakfast'],
                    'room_type_object': room_type_object,
                    'employee_object': employee_object
                })
                
                if result['status'] == settings.NEGATIVE:
                    data['messages'].extend(result['messages'])
                    data['messages'].append("Failed to add service '" + Post['service'] + "' to this room type.")

                else:
                    data['status'] = result['status']

        except Exception as e:
            data = utilities().error(data, error=e)

        return utilities().return_data(data)

    def get_room_types(self, type="all", Post = {}, only_count=False):
        """
        function gets room types
        :post_requirements: [**room_type_title]
        :param type:  all='get all room type', strict='get only room types with free rooms'
        :return:
        """

        data = utilities().init_data()

        try:
            if type == "all":
                if 'room_type_title' in Post:
                    room_types = room_type.objects.filter(~Q(no_of_rooms=0), ~Q(free_rooms=0),
                                                          type=Post['room_type_title']).order_by('id').first()
                else:
                    room_types = room_type.objects.all().order_by('id')

                if room_types is not None and len(room_types) > 0:
                    if only_count:
                        data['count'] = room_types.free_rooms
                    else:
                        data['room_types'] = room_types
                else:
                    raise Exception()
            if type == "strict":
                if 'room_type_title' in Post:
                    room_types = room_type.objects.filter(~Q(no_of_rooms=0), ~Q(free_rooms=0),
                                                          type=Post['room_type_title']).order_by('id').first()
                else:
                    room_types = room_type.objects.filter(~Q(no_of_rooms=0), ~Q(free_rooms=0)).order_by('id')
                
                if room_types is not None:
                    if only_count:
                        data['count'] = room_types.free_rooms
                    else:
                        data['room_types'] = room_types
                else:
                    raise Exception()
        except:
            data = utilities().error(data, 'Failed to get room types.')
        
        return utilities().return_data(data)

    def set_room_services(self, Id, Post):
        """

        :post_requirements: [(**room_type_object || **room_type), (**employee_object || **employee), title]
        :param Id: Admin's id
        :param Post: a dictionary with the services the passed room should have
        :return:
        """
        data = utilities().init_data()

        try:
            if 'room_type_object' in Post:
                room_type_object = Post['room_type_object']
            elif 'room_type' in Post:
                room_type_object = room_type.objects.get(pk=Post['room_type'])

            if 'employee_object' in Post:
                employee_object = Post['employee_object']
            elif 'employee' in Post:
                employee_object = employee.objects.get(pk=Post['employee'])

            room_services = room_type_service()
            room_services.room_type = room_type_object
            room_services.file_name = "n/a"
            room_services.title = Post['title']
            room_services.active = 1
            room_services.created_by = employee_object
            room_services.description = "n/a"

            room_services.save()

            data['status'] = settings.POSITIVE
        except Exception as e:
            print('===\n\nroom_service\ne\n\n\n====')
            data = utilities().error(data)

        return utilities().return_data(data)

    def get(self, type='all', only_count=False, Post={}):
        """
        function to get rooms based on the type param
        :post_requirements: [**room_type_title]
        :param type:  all='get all rooms', strict='get only free rooms'
        :param only_count: only Return the number of rooms
        :return:

        types:
        all: all rooms
        strict: all free rooms which are active and not reserved
        """
        data = utilities().init_data(post_extras={'rooms': []})
        try:
            if type == 'all':
                if 'room_type_title' in Post:
                    """ limit query to specific room type"""
                    rooms = room.objects.filter(type__type=Post['room_type_title']).order_by('-id')
                else:
                    rooms = room.objects.all().order_by('-id')

                if rooms is not None and len(rooms) > 0:
                    if only_count:
                        data['rooms_count'] = len(rooms)
                    else:
                        for room_object in rooms:
                            sub_content = {'room': room_object}
                            data['rooms'].append(sub_content)
                elif len(rooms) == 0:
                    raise Exception('No rooms available.')
                else:
                    raise Exception('Failed to get rooms.')
            elif type == 'strict':
                if 'room_type_title' in Post:
                    """ limit query to specific room type"""
                    rooms = room.objects.filter(reserved=0, status=1, type__type=Post['room_type_title'])
                else:
                    rooms = room.objects.filter(reserved=0, status=1)

                print(rooms)
                print(len(rooms))

                if rooms is not None and len(rooms) > 0:
                    if only_count:
                        data['rooms_count'] = len(rooms)
                    else:
                        for room_object in rooms:

                            if room_object.type is not None and room_object.type.free_rooms != 0 \
                                    and room_object.type.no_of_rooms != 0:
                                sub_content = {'room': room_object}
                                data['rooms'].append(sub_content)
                elif len(rooms) == 0:
                    print('here')
                    raise Exception('No free rooms available.')
                else:
                    raise Exception('Failed to get free rooms.')
            else:
                raise Exception()
        except Exception as e:
            print(e)
            data['messages'].append(str(e))
            data = utilities().error(data)

        return utilities().return_data(data)

    """ booking functions """

    def get_booked_rooms(self, only_count=False):
        """
        :param only_count:
        :return:
        """

        data = utilities().init_data()

        try:
            booking_object = booking.objects.filter(~Q(check_in_date=None), check_out_date=None)
            if booking_object is not None and len(booking_object) > 0:
                if only_count:
                    data['booked_rooms_count'] = len(booking_object)
                else:
                    data['booking_object'] = booking_object
            else:
                raise Exception()
        except Exception as e:
            data = utilities().error(data, "Failed to get booked rooms.")

        return utilities().return_data(data)

    def get_reservations(self, only_count=False):
        """
        :param only_count:
        :return:
        """

        data = utilities().init_data(post_extras={'reservations': [], 'total': 0})

        try:
            booking_object = booking.objects.filter(~Q(user=None), check_in_date=None)
            if booking_object is not None and len(booking_object) > 0:
                if only_count:
                    data['reservations_count'] = len(booking_object)
                else:
                    for child in booking_object:
                        subcontent = {'booking': child}
                        data['reservations'].append(subcontent)
                        data['total'] = data['total'] + 1
            else:
                raise Exception()
        except Exception as e:
            data = utilities().error(data, "Failed to get booked rooms.")

        return utilities().return_data(data)

    def booking_order(self, Id, Post):
        """

        :post_requirements: [room_no, item, price,quantity, ]
        :param Id:
        :param Post:
        :return:
        """

        data = utilities().init_data()

        try:

            booking_object = booking.objects.filter(room__room_no=Post['room_no'], check_out_date=None).\
                order_by('-id').first()
            if booking_object is None:
                raise Exception()

            employee_object = employee.objects.get(pk=Id)
            inventory_object = inventory.objects.filter(item_name=Post['item']).first()

            if inventory_object is not None and inventory_object:
                order_object = order()
                order_object.booking = booking_object
                order_object.item = inventory_object.item_name
                order_object.price = Post['price']
                order_object.quantity = Post['quantity']

                order_object.save()

                """ update stocks for the item """
                try:

                    previous_stock = stock.objects.filter(item=inventory_object).first()

                    stock_object = stock()
                    stock_object.current = previous_stock.current - int(Post['quantity'])
                    stock_object.item = inventory_object
                    stock_object.action_by = employee_object

                    stock_object.save()

                    """ add to revenue """
                    if not Post['reason']:
                        reason = "Order from " + booking_object.room__room_no + " on " + order_object.date.strftime(
                            "%Y-%m-%d %H:%M:%S") + ""
                    else:
                        reason = Post['reason']
                    result = hotel_management().add_revenue(Id, {'amount': Post['price'], 'source': booking_object.pk,
                                                                 'message': reason,
                                                                 'type': 'order'})
                    if result['status'] == settings.NEGATIVE:
                        data['messages'].extend(result['messages'])
                    else:
                        data['status'] = result['status']
                except Exception as e:
                    print(e)
                    raise Exception()
            else:
                raise Exception()
        except Exception as e:
            print(e)
            data = utilities().error(data, "Failed to place order.")

        return utilities().return_data(data)

    def get_orders(self, type='all', only_count=False, Post={}):
        """

        :post_requirements: [room_no, item, price,quantity, ]
        :param Id:
        :param Post:
        :return:
        """
        data = utilities().init_data()

        try:
            if type == 'all':
                orders_object = order.objects.all()
                if orders_object is not None:
                    data['orders_object']
            else:
                raise Exception('Unknown Type.')
        except:
            data = utilities().error(data)

        return utilities().return_data(data)

    def book(self, Id, POST):
        """
        function books a room
        :post_requirements: [room_id, password, price, discount, proposed_check_out_date, **reserve]
        :param Id:
        :param POST:
        :return:
        """
        data = utilities().init_data()

        password = POST['password']
        try:

            room_object = room.objects.get(pk=POST['room_id'])
            admin_object = employee.objects.get(pk=Id)

            if room_object is not None and room_object:
                if room_object.type.free_rooms > 0:
                    if room_object.reserved != 1:
                        booking_object = booking()
                        booking_object.room = room_object
                        booking_object.reservation_date = datetime.now()

                        user_info_object = self.handle_user_information(Post=POST)['user_info_object']

                        booking_object.price = POST['price']
                        booking_object.user = user_info_object
                        if 'reserve' not in POST:
                            booking_object.check_in_date = datetime.now()
                        booking_object.discount = POST['discount']
                        booking_object.password = utilities().hash(password)
                        booking_object.proposed_check_out_date = POST['proposed_check_out_date']

                        if 'reserve' in POST:
                            booking_object.reserve_action_by = admin_object
                        else:
                            booking_object.action_by = admin_object
                        booking_object.save()

                        if 'reserve' not in POST:
                            """
                                if reserved, do not mark the room as taken
                                after booking. take out a room from no of free rooms 
                            """
                            result = self.take_room({'room_id': room_object.pk})
                            if result['status'] == settings.NEGATIVE:
                                data['messages'].extend(result['messages'])

                        if 'pb' in POST:
                            """
                                take the public reservation off the list of not handled PBs
                            """
                            public_booking_object = public_booking.objects.get(pk=POST['pb'])
                            public_booking_object.status = 1

                            public_booking_object.save()

                        """ save to revenue """
                        result = hotel_management().add_revenue(Id, {'amount': POST['price'],
                                                                     'source': booking_object.pk,
                                                                     'message': "",
                                                                     'type': 'booking'})
                        if result['status'] == settings.NEGATIVE:
                            data['messages'].extend(result['messages'])
                        else:
                            data['status'] = settings.POSITIVE
                    else:
                        data['messages'].append('Selected room already reserved.')
                else:
                    data['messages'].append('No free rooms for in ' + room_object.type.type)
            else:
                raise Exception()
        except IntegrityError as e:
            if 'phone' in str(e):
                data['messages'].append("An error occurred while handling the phone number.")
            if 'email' in str(e):
                data['messages'].append("An error occurred while handling the email.")
        except Exception as e:
            print(e)
            data = utilities().error(data, "Failed to book room.", error=e)

        return utilities().return_data(data)

    def take_my_reservation(self, Id, Post):
        """

        :post_requirements: [room_no]
        :param Id:
        :param Post:
        :return:
        """
        data = utilities().init_data()

        try:
            room_object = room.objects.get(room_no=Post['room_no'])
            admin_object = employee.objects.get(pk=Id)

            if room_object is not None and room_object:
                if room_object.type.free_rooms > 0:
                    if room_object.reserved != 1:
                        """ Get Booking information """
                        booking_object = booking.objects.filter(check_in_date=None,
                                                                room=room_object).first()
                        if booking_object is not None and booking_object:
                            booking_object.check_in_date = datetime.now()
                            booking_object.action_by = admin_object

                            booking_object.save()

                            data['booking_object'] = booking_object

                            """ take room"""
                            result = self.take_room({'room_id': room_object.pk})
                            if result['status'] != settings.NEGATIVE:
                              data['status'] = settings.POSITIVE
                        else:
                            raise Exception()
                    else:
                        data['messages'].append('Selected room already reserved.')
                else:
                    data['messages'].append('No free rooms for in ' + room_object.type.type)
            else:
                raise Exception()
        except Exception as e:
            data = utilities().error(data, "Failed to take reservation.")

        return utilities().return_data(data)

    def take_room(self, Post):
        """
        function is used to mark a room as taken/not free.

        :post_requirements: [room_id]
        :param Post:
        :return:
        """
        """  """
        data = utilities().init_data()

        try:
            room_object = room.objects.get(pk=Post['room_id'])
            room_type_object = room_object.type

            no_of_free_rooms = room_type_object.free_rooms
            if no_of_free_rooms != 0:
                room_type_object.free_rooms = room_object.type.free_rooms - 1
            else:
                room_type_object.free_rooms = 0
            room_type_object.save()
            """ mark this room as reserved """
            room_object.reserved = 1
            room_object.save()

            data['status'] = settings.POSITIVE
        except:
            data = utilities().error(data,"Failed to mark room as taken.")

        return utilities().return_data(data)

    def release_room(self, Post):
        """
        function is used to release a room.

        :post_requirements: [(**room_id || **room_object)]
        :param Post:
        :return:
        """
        """ """
        data = utilities().init_data()

        try:
            if 'room_object' in Post:
                room_object = Post['room_object']
            else:
                room_object = room.objects.get(pk=Post['room_id'])
            """ mark this room as reserved """
            room_object.reserved = 0
            room_object.save()

            room_type_object = room_object.type
            room_type_object.free_rooms = room_type_object.free_rooms + 1
            room_type_object.save()

            data['status'] = settings.POSITIVE
        except:
            data = utilities().error(data,
                                     "Failed free up room. please contact admin(Room no : " + room_object.room_no + ")")

        return utilities().return_data(data)

    def edit_booking(self, Id, Post):
        data = utilities().init_data()

        password = Post['password']
        try:

            booking_object = booking.objects.filter(~Q(reservation_date=None), room=Post['room_id'],
                                                    check_out_date=None).first()
            admin_object = employee.objects.get(pk=Id)

            """ edit booking information """
        except:
            data = utilities().error(data, "Failed to reserve room.")

        return utilities().return_data(data)

    def handle_user_information(self, Post):
        """
        function is used to save user information
        
        #  :post_requirements: [phone, full_name, email, phone, NKName, NKphone]
        :param Post: 
        :return: 
        """
        
        data = utilities().init_data()

        try:
            """ get user info if already saved. """
            user_info_object = user_information.objects.filter(
                (Q(email=Post['email']) | Q(phone=Post['phone']))).first()
            user_info_object.count = user_info_object.count + 1
        except Exception as e:
            user_info_object = user_information()
            user_info_object.full_name = Post['full_name']
            user_info_object.email = Post['email']
            user_info_object.phone = Post['phone']
            user_info_object.next_of_kin_name = Post['NKName']
            user_info_object.next_of_kin_phone = Post['NKphone']
            if 'source' in Post:
                user_info_object.source = Post['source']

        user_info_object.save()

        data['status'] = settings.POSITIVE

        return utilities().return_data(data, post_extras={'user_info_object': user_info_object})

    def public_reservations(self):
        """
        function is used to get reservations made from the client side

        :param Post:
        :return:
        """
        data = utilities().init_data(post_extras={'public_booking_object': [], 'count': 0})
        try:
            public_booking_object = public_booking.objects.filter(status=0)
            print(public_booking_object)
            if public_booking_object is not None and len(public_booking_object) > 0:
                for object in public_booking_object:
                    subcontent = {'booking': object}
                    data['public_booking_object'].append(subcontent)
                    data['count'] += data['count'] + 1
            else:
                raise Exception()
        except Exception as e:
            data = utilities().error(data, error=e)

        return utilities().return_data(data)

    def get_public_reservation_by_id(self, Post):
        """
        function is used to get a public reservation information

        #  :post_requirements: [pb_id,]
        :param Post:
        :return:
        """
        data = utilities().init_data()
        try:
            public_booking_object = public_booking.objects.filter(pk=Post['pb_id'], status=0).first()
            if public_booking_object is not None and public_booking_object:
                data['public_booking_object'] = public_booking_object
        except Exception as e:
            data = utilities().error(data, error=e)

        return utilities().return_data(data)

    """ conversation functions"""

    def conversation_counter(self, Post, type="add"):
        """
        function is used to get a public reservation information

        #  :post_requirements: [employee_id]
        :param Post:
        :return:
        """
        data = utilities().init_data()
        try:
            if type == 'add':
                employee_object = employee.objects.get(pk=Post['employee_id'])

                admin_conversation_object = admin_conversation()
                admin_conversation_object.employee = employee_object
                admin_conversation_object.conversations = admin_conversation_object.conversations + 1

                admin_conversation_object.save()
            else:
                raise Exception()
        except Exception as e:
            data = utilities().error(data, "Conversation counter error occurred.", error=e)
        return utilities().return_data(data)


class hotel_admin:

    def create_staff(self, Id, Post):
        """
        :post_param: [email,password,phone,full_name,department,employed_on,address,position,]
        :param Id:
        :param Post:
        :return:
        """
        data = utilities().init_data()
        try:
            employee_object = employee()
            employee_object.email = Post['email']
            employee_object.password = utilities().hash(Post['password'])
            employee_object.phone = Post['phone']
            employee_object.full_name = Post['full_name']
            employee_object.auth_level = settings.DEPARTMENTS[Post['department']]['auth_level']
            employee_object.employed_on = Post['employed_on']
            employee_object.address = Post['address']
            employee_object.department = settings.DEPARTMENTS[Post['department']]['name']
            employee_object.position = Post['position']

            employee_object.save()

            """ if user is a receptionist/front-desk(er) create a conversation column """
            if employee_object.auth_level == settings.LEVELS['front_desk']:
                admin_conversation_object = admin_conversation()
                admin_conversation_object.conversations = 0
                admin_conversation_object.employee = employee_object

                admin_conversation_object.save()

            data['status'] = settings.POSITIVE
        except Exception as e:
            data = utilities().error(data, "Failed to create new user.", error=e)

        return utilities().return_data(data)

    def get_staff(self, type='all'):
        data = utilities().init_data(post_extras={'employee_objects': []})
        try:
            if type == 'all':
                employee_objects = employee.objects.all()
                if employee_objects is not None and len(employee_objects) > 0:

                    for child in employee_objects:
                        subcontent = {'employee': child}
                        result = self.get_staff_attendance({'employee_id': child.pk})

                        if result['status'] != settings.NEGATIVE:
                            subcontent['attendance'] = result['attendance_object']

                        result = hotel_management().get_salary_payment(Post={'employee_id': child.pk})

                        if result['status'] != settings.NEGATIVE:
                            subcontent['salary'] = result['salary_object'][0]['salary']

                        data['employee_objects'].append(subcontent)
                else:
                    raise Exception()
            else:
                raise Exception()
        except Exception as e:
            print(e)
            data = utilities().error(data, "Failed to get staffs.")
        return utilities().return_data(data)

    def login(self, Post):
        data = utilities().init_data()
        correct_pasword = True
        try:
            employee_object = employee.objects.filter(email=Post['email']).first()
            if employee_object.password == utilities().hash(Post['password']):
                data['employee'] = employee_object
            else:
                correct_pasword = False
                raise Exception("Password incorrect.")
        except Exception as e:
            if not correct_pasword:
                data = utilities().error(data, str(e))
            else:
                data = utilities().error(data, "Email incorrect.")
        
        return utilities().return_data(data)

    def attendance_signin(self, Post):
        data = utilities().init_data()

        try:
            employee_object = get_object_or_404(employee, email=Post['email'], password=utilities().hash(Post['password']))
            try:
                """
                    check if this employee has signed in before for today
                """
                attendance_object = attendance.objects.filter(employee=employee_object,
                                                              check_in__date=date.today()).first()
                if attendance_object is not None or attendance_object:
                    data['messages'].append("Already taken attendance for the day.")
                else:
                    """ raise exception"""
                    raise Exception()
            except:
                """ 
                    create new attendance instance if user hasn't singed in for the day
                """
                attendance_object = attendance()
                attendance_object.check_in = datetime.now()
                attendance_object.employee = employee_object

                attendance_object.save()


                """ sign out user for previous days which check out is none """
                try:
                    attendance_object = attendance.objects.filter(employee=employee_object, check_out=None)
                    for child in attendance_object:
                        """ set signout for that day to be time max for said day."""
                        sigin_max = str(child.check_in__date) + " " + str(time.max)
                        child.check_out = datetime.strptime(sigin_max, '%Y-%m-%d %H:%M:%S.%f')

                        child.save()
                except:
                    """n/a"""

            data['status'] = settings.POSITIVE
        except Exception as e:
            data = utilities().error(data, "An error occurred.", error=e)


        return utilities().return_data(data)

    def attendance_signout(self, Post):
        data = utilities().init_data()

        try:
            """
                get employee attendance info
            """
            employee_object = get_object_or_404(employee, email=Post['email'],
                                                password=utilities().hash(Post['password']))

            attendance_object = attendance.objects.filter(employee=employee_object,
                                                          check_in__contains=date.today()).first()
            if attendance_object is None or not attendance_object:
                """ employee hasn't signed in """
                raise Exception()
            else:
                attendance_object.check_out = datetime.now()
                attendance_object.save()

                data['status'] = settings.POSITIVE
        except Exception as e:
            data = utilities().error(data, "Sign in information not found, have you signed in today?")

        return utilities().return_data(data)

    def get_attendance(self, type="today", Post={}):
        """
        :post_requirements: [date]
        :param Post:
        :return:
        """
        e = "Failed to get attendance information."
        no_attendance = "No Attendance for "

        data = utilities().init_data()

        try:
            if type == "today":
                """ getting attendance for the day"""
                attendance_object = attendance.objects.filter(check_in__date=date.today())
                if attendance_object is not None and len(attendance_object) > 0:
                    data['attendance_object'] = attendance_object
                else:
                    if len(attendance_object) == 0:
                        raise Exception(no_attendance +  'today.')
                    else:
                        raise Exception(e)

            elif type == "all":
                attendance_object = attendance.objects.all().order_by('-id')
                if attendance_object is not None and len(attendance_object) > 0:
                    data['attendance_object'] = attendance_object
                else:
                    raise Exception()
            elif type == "custom":
                if len(Post) > 0:
                    attendance_object = attendance.objects.filter(check_in__date=Post['date'])
                    if attendance_object is not None and len(attendance_object) > 0:
                        data['attendance_object'] = attendance_object
                    else:
                        if len(attendance_object) == 0:
                            e = no_attendance + Post['date'] +"."
                        raise Exception(e)
                else:
                    raise Exception(e)
            else:
                raise Exception("Unknown type passed.")
        except Exception as ex:
            data = utilities().error(data, str(ex))
        
        return utilities().return_data(data)

    def get_staff_attendance(self, Post, type="today"):
        """
        function is used to select a particular staff from todays attendance, fails if staff is not signed in
        :post_requirements: [employee_id]
        :param Post:
        :return:
        """

        data = utilities().init_data()

        try:
            if type == 'today':
                employee_object = get_object_or_404(employee, pk=Post['employee_id'])
                data['attendance_object'] = attendance.objects.filter(check_in__date=date.today(),
                                                                      employee=employee_object, check_out__date=None)
            else:
                raise Exception()
        except Exception as e:
            data = utilities().error(data, "Failed to get staff's attendance for " + type + ".", error=e)
        return utilities().return_data(data)

    def get_employees_by_department(self, department, only_count=False):
        data = utilities().init_data()

        try:
            employee_object = employee.objects.filter(department=department).order_by('-id')
            if employee_object is not None and len(employee_object) > 0:
                if only_count:
                    data['employees_count'] = len(employee_object)
                else:
                    data['employee_object'] = employee_object
            else:
                raise Exception()
        except:
            data = utilities().error(data, "Failed to get employees for " + department)

        return utilities().return_data(data)

    """ public(customer side data funtions) """

    def get_public_contact_data(self):
        """
        function is used to get data saved from the contact us page
        :return:
        """
        data = utilities().init_data(post_extras={'public_contact_object': [], 'count': 0})
        try:
            public_contact_object = public_contact.objects.filter(status=0)
            if public_contact_object is not None and len(public_contact_object) > 0:
                for child in public_contact_object:
                    subcontent = {'contact': child}
                    data['public_contact_object'].append(subcontent)
                    data['count'] = data['count'] + 1
        except Exception as e:
            data = utilities().error(data,
                                     "Failed to get public contact us information. Please try again later.",
                                     error=e)

        return utilities().return_data(data)

    def mark_public_contact_data(self, pcu_id):
        """
        function is used to mark selected contact us instance as handled.
        :pcu_id: the PK(id) for the selected contact us instance
        :return:
        """
        data = utilities().init_data()
        try:
            public_contact_object = public_contact.objects.get(pk=pcu_id)
            public_contact_object.status = 1

            public_contact_object.save()

            data['status'] = settings.POSITIVE
        except:
            data = utilities().error(data,
                                     "Failed to mark contact data as done.",
                                     error=e)
        return utilities().return_data(data)


class hotel_back_bone:
    def get_all_departments(self):
        data = utilities().init_data(post_extras={'department_object': []})
        try:
            department_object = department.objects.all().order_by('-id')
            if department_object is not None and len(department_object) > 0:
                subcontent = {'department': department_object}
                data['department_object'].append(subcontent)
            else:
                raise Exception()
        except:
            data = self.synchronize_department()

        return utilities().return_data(data)

    def get_department(self, department_id=0, department_title='n/a'):
        data = utilities().init_data(post_extras={'department_object': []})

        try:
            if department_id != 0:
                department_object = department.objects.get(pk=department_id)
            if department_title != 'n/a':
                department_object = department.objects.filter(department_title=department_title).first()

            if department_object is not None and department_object:
                subcontent = {'department': department_object}
                data['department_object'].append(subcontent)
            else:
                raise Exception()
        except:
            """
                check if department table is empty
            """
            try:
                department_object = department.objects.all()
                if department_object is None and len(department_object) < 1:
                    """
                        load in default department info from settings.py
                    """
                    result = self.create_departments()
                    if result['status'] == settings.NEGATIVE:
                        data['messages'].extend(result['messages'])
            except:
                data = utilities().error(data, "Failed to get department information.")

        return utilities().return_data(data)

    def synchronize_department(self):
        data = utilities().init_data()

        current_departments = self.get_all_departments()
        if current_departments['status'] != settings.NEGATIVE:
            try:
                for dept in settings.DEPARTMENTS:
                    try:
                        department_object = department.objects.filter(department_title=dept['name']).first()
                        if department_object is not None or department_object:
                            """ exists, update if value is different"""
                            if department_object.department_val != dept['val']:
                                department_object.department_val = dept['val']

                            if department_object.auth_level != dept['auth_level']:
                                department_object.auth_level = dept['auth_level']
                        else:
                            raise Exception()
                    except:
                        department_object = department()
                        department_object.department_title = dept['name']
                        department_object.auth_level = dept['auth_level']
                        department_object.department_val = dept['val']

                    department_object.save()

                data['status'] = settings.POSITIVE
            except Exception as e:
                data = utilities().error(data, "Failed to synchronize departments.")
        else:
            result = self.create_departments()
            data = result

        return utilities().return_data(data)

    def create_departments(self):
        data = utilities().init_data()

        try:
            for dept in settings.DEPARTMENTS:
                department_object = department()
                department_object.department_title = dept['name']
                department_object.auth_level = dept['auth_level']
                department_object.department_val = dept['val']

                department_object.save()

            data['status'] = settings.POSITIVE
        except Exception as e:
            print(e)
            data = utilities().error(data, "Failed to create departments.")

        return utilities().return_data(data)


class hotel_management:

    def add_expense(self, Id, Post):
        data = utilities().init_data()
        
        try:
            expense_object = expense()
            expense_object.action_by = employee.objects.get(pk=Id)
            expense_object.item = Post['item']
            expense_object.amount = Post['amount']
            expense_object.message = Post['message']
            
            expense_object.save()

            data['status'] = settings.POSITIVE
        except Exception as e:
            data = utilities().error(data, 'Failed to save expense.', e)
        return utilities().return_data(data)

    def get_expense(self, type="today"):
        data = utilities().init_data(post_extras={'expense_object': [], 'total': 0})

        try:
            if type == "today":
                expense_object = expense.objects.filter(date__date=date.today()).order_by('-id')
                if expense_object is not None and len(expense_object) > 0:
                    for child in expense_object:
                        subcontent = {'expense': child}
                        data['expense_object'].append(subcontent)
                        data['total'] = int(data['total']) + child.amount
                else:
                    raise Exception()
        except:
            data = utilities().error(data, "Failed to get expense for " + type + ".")

        return utilities().return_data(data)

    def add_revenue(self, Id, Post):
        data = utilities().init_data()

        try:
            employee_object = employee.objects.get(pk=Id)

            revenue_object = revenue()
            revenue_object.amount = Post['amount']
            revenue_object.message = Post['message']
            revenue_object.source = Post['source']
            revenue_object.type = Post['type']
            revenue_object.action_by = employee_object

            revenue_object.save()

            data['status'] = settings.POSITIVE
        except Exception as e:
            print(e)
            data = utilities().error(data, error=e, error_message="Failed to add revenue.")

        return utilities().return_data(data)

    def get_revenue(self, type='today'):
        data = utilities().init_data(post_extras={'revenue_object': [], 'total': 0})

        try:
            if type == 'today':
                revenue_object = revenue.objects.filter(date__date=date.today()).order_by('-id')
                if revenue_object is not None and len(revenue_object) > 0:
                    for child in revenue_object:
                        subcontent = {'revenue': child}
                        data['revenue_object'].append(subcontent)
                        data['total'] = data['total'] + child.amount
            elif type == 'all':
                revenue_object = revenue.objects.filter().order_by('-id')
                
                if revenue_object is not None and len(revenue_object) > 0:
                    for child in revenue_object:
                        subcontent = {'revenue': child}
                        data['revenue_object'].append(subcontent)
                        data['total'] = data['total'] + child.amount
            else:
                raise Exception()
        except:
            data = utilities().error(data, "Failed to get revenues for " + type + ".")

        return utilities().return_data(data)

    def add_salary(self, Id, Post):
        """
        :post_param: [pay_date, amount, employee(employee_id)]
        :param Id:
        :param Post:
        :return:
        """
        data = utilities().init_data()

        try:
            employee_object = employee.objects.get(pk=Post['employee'])
            admin_object = employee.objects.get(pk=Id)

            salary_object = salary()
            salary_object.employee = employee_object
            salary_object.pay_date = Post['pay_date']
            salary_object.amount = Post['amount']
            salary_object.action_by = admin_object

            salary_object.save()

            data['status'] = settings.POSITIVE
        except Exception as e:
            print(e)
            data = utilities().error(data, "Failed to save salary payment.", error=e)

        return utilities().return_data(data)

    def get_salary_payment(self, type="month", Post={}):
        """
        :post_param: [employee_id]
        :post:
        :param type: [month, year]
        :return:
        """
        data = utilities().init_data(post_extras={'salary_object': [], 'total': 0})

        if 'employee_id' in Post:
            employee_object = employee.objects.get(pk=Post['employee_id'])

        try:
            if type == 'month':
                if 'employee_id' in Post:
                    employee
                    salary_object = salary.objects.filter(pay_date__month=datetime.now().strftime('%m'),
                                                          employee=employee_object)
                else:
                    salary_object = salary.objects.filter(pay_date__month=datetime.now().strftime('%m'))
            elif type == 'year':
                if 'employee_id' in Post:
                    salary_object = salary.objects.filter(pay_date__year=datetime.now().strftime('%Y'),
                                                          employee=employee_object)
                else:
                    salary_object = salary.objects.filter(pay_date__year=datetime.now().strftime('%Y'))

            if salary_object is not None and len(salary_object) > 0:
                for child in salary_object:
                    subcontent = {'salary': child}

                    data['salary_object'].append(subcontent)
                    data['total'] = data['total'] + child.amount
            else:
                raise Exception()
        except Exception as e:
            data = utilities().error(data, "Failed to get payment information.", error=e)

        return utilities().return_data(data)


class utilities:
    def generate_password(self, N):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))

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

        if dict['messages_count'] == 0 and dict['status'] != settings.NEGATIVE:
            """ only append positive message if no messages"""
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

        """ send negative back if error """
        dict['message_type'] = dict['status']
        if error is not None:
            print(error)
        return dict

    def upload_image(self, Post):
        data = {'status': settings.POSITIVE, 'messages': []}

        try:
            for file in Post['file']:
                filename = hashlib.sha1(datetime.now().__str__().encode()).hexdigest()
                base_path = settings.TRANSACTIONPATH
                if not os.path.exists(base_path):
                    os.mkdir(base_path)

                ext = os.path.splitext(str(file))

                filename = filename + "." + ext[1::]

                if ext[1::] not in ['jpg', 'png', 'jpeg']:
                    data["messages"].append(
                        "Image format not supported, Please make sure image is of the type jpg, jpeg or png.")
                else:
                    with open(base_path + filename, 'wb+') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
        except:
            data = self.error(data)

        return data

