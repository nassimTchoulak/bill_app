# Generated by Django 3.0.6 on 2020-06-02 03:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bill', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fournisseur',
            name='nom',
            field=models.CharField(default='', max_length=50, null=True),
        ),
    ]