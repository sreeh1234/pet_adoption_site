# Generated by Django 5.1.6 on 2025-02-18 09:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_delete_pet'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('p_name', models.TextField()),
                ('p_dis', models.TextField()),
                ('breed', models.TextField()),
                ('p_age', models.IntegerField()),
                ('price', models.IntegerField()),
                ('p_img', models.FileField(upload_to='')),
                ('Pet_Type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.pettype')),
                ('categories', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.category')),
            ],
        ),
    ]
