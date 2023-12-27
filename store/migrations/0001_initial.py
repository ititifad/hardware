# Generated by Django 4.2.2 on 2023-06-29 19:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('inventory_quantity', models.PositiveIntegerField()),
                ('standard_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('current_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('reorder_point', models.PositiveIntegerField()),
                ('barcode', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('sale_date', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
            ],
            options={
                'ordering': ('-sale_date',),
            },
        ),
    ]
