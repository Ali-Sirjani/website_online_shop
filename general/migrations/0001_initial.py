# Generated by Django 4.2.1 on 2023-06-19 14:26

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContactUsModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=300, verbose_name='full name')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region='IR', verbose_name='phone')),
                ('email_user', models.EmailField(blank=True, max_length=254, null=True, verbose_name='email')),
                ('message', models.TextField()),
                ('answer', models.BooleanField(default=False, verbose_name='answer')),
                ('datetime_created', models.DateTimeField(auto_now_add=True, verbose_name='datetime created')),
                ('datetime_modified', models.DateTimeField(auto_now=True, verbose_name='datetime modified')),
            ],
        ),
    ]
