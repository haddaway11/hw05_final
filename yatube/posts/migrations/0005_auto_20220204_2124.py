# Generated by Django 2.2.19 on 2022-02-04 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20220204_2118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(max_length=2000),
        ),
    ]
