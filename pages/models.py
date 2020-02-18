from django.db import models
from datetime import datetime
# Create your models here.


class public_booking(models.Model):
    reservation_date = models.DateTimeField(default=datetime.now, blank=True, null=True)
    proposed_check_in_date = models.DateTimeField(blank=True, null=True)
    proposed_check_out_date = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey('room.user_information',
                             on_delete=models.CASCADE, blank=True, null=True)
    room_type = models.CharField(max_length=100, blank=True, null=True)
    status = models.IntegerField(default=0, blank=True, null=True)
    adults = models.IntegerField(default=1, blank=True, null=True)
    children = models.IntegerField(default=0, blank=True, null=True)


class public_contact(models.Model):
    full_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    date = models.DateTimeField(default=datetime.now, blank=True, null=True)
    status = models.IntegerField(default=0, blank=True, null=True)

