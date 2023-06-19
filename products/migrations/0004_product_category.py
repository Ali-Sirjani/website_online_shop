# Generated by Django 4.2.1 on 2023-06-19 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ManyToManyField(blank=True, default=None, related_name='categories', to='products.category'),
        ),
    ]