# Generated by Django 5.1.6 on 2025-02-18 11:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_pet'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pet',
            name='categories',
        ),
        migrations.RemoveField(
            model_name='pet',
            name='Pet_Type',
        ),
        migrations.DeleteModel(
            name='Category',
        ),
        migrations.DeleteModel(
            name='Pet',
        ),
        migrations.DeleteModel(
            name='PetType',
        ),
    ]
