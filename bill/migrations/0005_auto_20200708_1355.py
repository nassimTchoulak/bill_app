# Generated by Django 3.0.6 on 2020-07-08 12:55

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bill', '0004_auto_20200618_1414'),
    ]

    operations = [
        migrations.CreateModel(
            name='Commande',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('termine', models.BooleanField(default=False)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bill.Client')),
                ('facture', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='commande_facture', to='bill.Facture')),
            ],
        ),
        migrations.AddField(
            model_name='produit',
            name='produit_image',
            field=models.ImageField(default=None, null=True, upload_to='./'),
        ),
        migrations.CreateModel(
            name='LigneCommande',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qte', models.IntegerField(default=1)),
                ('commande', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lignes_commande', to='bill.Commande')),
                ('produit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bill.Produit')),
            ],
        ),
        migrations.AddConstraint(
            model_name='lignecommande',
            constraint=models.UniqueConstraint(fields=('produit', 'commande'), name='produit-commande'),
        ),
    ]