# Generated by Django 2.1.7 on 2019-05-16 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0003_auto_20190516_1047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory',
            name='item_type',
            field=models.CharField(blank=True, default='unknown', max_length=100, null=True),
        ),
    ]