# Generated by Django 3.1.6 on 2021-02-06 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seller', '0004_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(upload_to='photos/%s/'),
        ),
    ]
