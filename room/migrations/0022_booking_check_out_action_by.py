# Generated by Django 2.1.7 on 2019-05-22 11:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0019_revenue_type'),
        ('room', '0021_room_images'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='check_out_action_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checkout_by', to='staff.employee'),
        ),
    ]
