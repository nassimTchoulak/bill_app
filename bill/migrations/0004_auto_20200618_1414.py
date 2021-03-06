# Generated by Django 3.0.6 on 2020-06-18 13:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bill', '0003_auto_20200617_1828'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categorie',
            fields=[
                ('designation', models.CharField(max_length=50, primary_key=True, serialize=False)),
            ],
        ),
        migrations.AlterField(
            model_name='lignefacture',
            name='produit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lignes_produit', to='bill.Produit'),
        ),
        migrations.AlterField(
            model_name='produit',
            name='fournisseur',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fournisseur_produit', to='bill.Fournisseur'),
        ),
        migrations.AddField(
            model_name='produit',
            name='categorie',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='categorie_produit', to='bill.Categorie'),
        ),
    ]
