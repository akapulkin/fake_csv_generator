# Generated by Django 3.1.4 on 2020-12-15 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schemas', '0002_auto_20201215_2034'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='schemacolumn',
            constraint=models.UniqueConstraint(fields=('schema', 'order'), name='unique chapter'),
        ),
    ]
