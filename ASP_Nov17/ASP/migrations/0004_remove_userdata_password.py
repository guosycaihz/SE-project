# Generated by Django 2.2 on 2018-11-16 13:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ASP', '0003_clinicmanager_dispatcher_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userdata',
            name='password',
        ),
    ]
