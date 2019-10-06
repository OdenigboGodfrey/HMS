from django.db import models
from datetime import datetime

# Create your models here.


class room_type(models.Model):
    type = models.CharField(max_length=25, blank=True, null=True)
    no_of_rooms = models.IntegerField(default=0, blank=True, null=True)
    free_rooms = models.IntegerField(default=0, blank=True, null=True)
    price = models.FloatField(default=0, blank=True, null=True)
    discount = models.FloatField(default=0, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    action_by = models.ForeignKey('staff.employee', on_delete=models.CASCADE,
                                  blank=True, null=True, related_name='room_type_action_by')

    def __str__(self):
        return self.type


class room_type_service(models.Model):
    file_name = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    active = models.IntegerField(default=1, blank=True, null=True)
    created_by = models.ForeignKey('staff.employee',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_on = models.DateTimeField(default=datetime.now, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    room_type = models.ForeignKey(room_type, on_delete=models.CASCADE,
                                  blank=True, null=True, related_name="room_type_service")

    def __str__(self):
        return str(self.room_type) + " " + str(self.title)


class room(models.Model):
    room_no = models.CharField(max_length=10, blank=True, null=True, unique=True)
    reserved = models.IntegerField(default=0, blank=True, null=True)
    status = models.IntegerField(default=1, blank=True, null=True)
    type = models.ForeignKey(room_type,
                             on_delete=models.CASCADE, blank=True, null=True, related_name='room_type')

    def __str__(self):
        return str(self.room_no) + " " + str(self.type)


class room_image(models.Model):
    room = models.ForeignKey(room, on_delete=models.CASCADE,
                             blank=True, null=True, related_name="room_image")
    file_name = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(default=datetime.now, blank=True, null=True)
    created_by = models.ForeignKey('staff.employee', on_delete=models.CASCADE,
                                   blank=True, null=True, related_name="image_created_by_admin")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.file_name)


class room_log(models.Model):
    room = models.ForeignKey(room,
                             on_delete=models.CASCADE, blank=True, null=True, related_name='log_for_room_no')
    action_by = models.ForeignKey('staff.employee',
                                  on_delete=models.CASCADE, blank=True, null=True, related_name='employee')
    log_date = models.DateTimeField(default=datetime.now, blank=True, null=True)
    log = models.TextField(blank=True, null=True)


class review(models.Model):
    review_content = models.TextField(blank=True, null=True)
    user = models.ForeignKey('user_information', on_delete=models.CASCADE,
                             blank=True, null=True, related_name='user_review')
    review_date = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(default=0, blank=True, null=True)
    booking = models.ForeignKey('booking', on_delete=models.CASCADE, blank=True, null=True,
                                related_name='review_for_booking')

    def __str__(self):
        return str(self.review_content)


class user_information(models.Model):
    full_name = models.CharField(max_length=250, blank=True, null=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True, unique=True)
    count = models.IntegerField(default=1, blank=True, null=True)
    next_of_kin_name = models.CharField(max_length=250, blank=True, null=True)
    next_of_kin_phone = models.CharField(max_length=250, blank=True, null=True)
    source = models.CharField(max_length=250, default="staff", blank=True, null=True)

    def __str__(self):
        return str(self.email)


class booking(models.Model):
    room = models.ForeignKey(room, on_delete=models.CASCADE, blank=True, null=True, related_name='room_booking')
    check_in_date = models.DateTimeField(blank=True, null=True)
    check_out_date = models.DateTimeField(blank=True, null=True)
    reservation_date = models.DateTimeField(blank=True, null=True)
    proposed_check_out_date = models.DateTimeField(blank=True, null=True)
    date = models.DateTimeField(default=datetime.now, blank=True, null=True)
    user = models.ForeignKey('user_information', on_delete=models.CASCADE, blank=True, null=True,
                             related_name='user_info')
    price = models.FloatField(blank=True, null=True)
    discount = models.FloatField(blank=True, null=True)
    password = models.CharField(max_length=50, blank=True, null=True)
    action_by = models.ForeignKey('staff.employee',  on_delete=models.CASCADE, blank=True, null=True,
                                  related_name='booked_by')
    check_out_action_by = models.ForeignKey('staff.employee',  on_delete=models.CASCADE, blank=True, null=True,
                                            related_name='checkout_by')
    reserve_action_by = models.ForeignKey('staff.employee', on_delete=models.CASCADE, blank=True, null=True,
                                          related_name='reserved_by')

    def __str__(self):
        return str(self.pk) + " " + str(self.room.room_no) + \
               " " + " (" + str(self.check_in_date) + "-" + str(self.check_out_date) + ")"


class order(models.Model):
    booking = models.ForeignKey(booking, on_delete=models.CASCADE, blank=True, null=True)
    item = models.CharField(max_length=250, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    quantity = models.IntegerField(default=1, blank=True, null=True)
    date = models.DateTimeField(default=datetime.now, blank=True, null=True)

    def __str__(self):
        return str(self.item)


class message(models.Model):
    room = models.ForeignKey(room, on_delete=models.CASCADE,
                             blank=True, null=True, related_name="room_message")
    booking = models.ForeignKey(booking, on_delete=models.CASCADE,
                                blank=True, null=True, related_name="booking_message")
    employee = models.ForeignKey('staff.employee', on_delete=models.CASCADE, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(default=datetime.now, blank=True, null=True)
    sent_by = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return str(self.booking)
