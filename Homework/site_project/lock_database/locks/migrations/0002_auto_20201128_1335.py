# Generated by Django 3.1.3 on 2020-11-28 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lock',
            name='image',
            field=models.FileField(null=True, upload_to='', verbose_name='Lock image'),
        ),
    ]