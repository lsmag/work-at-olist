# Generated by Django 2.1.1 on 2018-09-03 23:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CallRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('st', 'Start'), ('ed', 'End')], max_length=2)),
                ('call_id', models.PositiveIntegerField()),
                ('timestamp', models.DateTimeField()),
                ('source', models.CharField(blank=True, max_length=11, validators=[django.core.validators.RegexValidator(message='Invalid phone number, format should be AAXXXXXXXXX where AA is the area code and XXXXXXXXX is the phone number, composed of 8 to 9 digits', regex='^\\d{10,11}$')])),
                ('destination', models.CharField(blank=True, max_length=11, validators=[django.core.validators.RegexValidator(message='Invalid phone number, format should be AAXXXXXXXXX where AA is the area code and XXXXXXXXX is the phone number, composed of 8 to 9 digits', regex='^\\d{10,11}$')])),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='callrecord',
            unique_together={('type', 'call_id')},
        ),
    ]