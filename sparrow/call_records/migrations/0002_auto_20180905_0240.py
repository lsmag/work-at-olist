# Generated by Django 2.1.1 on 2018-09-05 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('call_records', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callrecord',
            name='type',
            field=models.CharField(choices=[('start', 'Start'), ('end', 'End')], max_length=5),
        ),
    ]