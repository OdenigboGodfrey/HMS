# Generated by Django 2.1.7 on 2019-05-22 11:01

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0019_revenue_type'),
        ('room', '0020_booking_proposed_check_out_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='room_images',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_filename', models.TextField(blank=True, null=True)),
                ('date', models.DateTimeField(blank=True, default=datetime.datetime.now, null=True)),
                ('action_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='staff.employee')),
                ('room', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='room_image', to='room.room')),
            ],
        ),
    ]