# Generated migration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('empresa', '0001_initial'),
        ('sped', '0002_registro0200_registroc100_registroc170'),
        ('reforma_tributaria', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemNCM',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cod_item', models.CharField(max_length=60, verbose_name='Código do Item')),
                ('descricao', models.TextField(verbose_name='Descrição')),
                ('cod_ncm', models.CharField(max_length=8, verbose_name='NCM')),
                ('cest', models.CharField(blank=True, max_length=7, verbose_name='CEST')),
                ('cod_barra', models.CharField(blank=True, max_length=14, verbose_name='Código de Barras')),
                ('unidade', models.CharField(blank=True, max_length=6, verbose_name='Unidade')),
                ('cst_icms', models.CharField(blank=True, max_length=3, verbose_name='CST ICMS')),
                ('cst_pis', models.CharField(blank=True, max_length=2, verbose_name='CST PIS')),
                ('cst_cofins', models.CharField(blank=True, max_length=2, verbose_name='CST COFINS')),
                ('cfop', models.CharField(blank=True, max_length=4, verbose_name='CFOP')),
                ('aliq_icms', models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name='Alíquota ICMS')),
                ('aliq_pis', models.DecimalField(decimal_places=4, default=0, max_digits=8, verbose_name='Alíquota PIS')),
                ('aliq_cofins', models.DecimalField(decimal_places=4, default=0, max_digits=8, verbose_name='Alíquota COFINS')),
                ('cbs_aliquota', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='CBS Alíquota')),
                ('ibs_aliquota', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='IBS Alíquota')),
                ('origem', models.CharField(choices=[('SPED', 'SPED Fiscal/Contribuições'), ('XML', 'XML de NF-e'), ('MANUAL', 'Cadastro Manual')], default='SPED', max_length=10, verbose_name='Origem')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens_ncm', to='empresa.empresa')),
                ('registro_0000', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='itens_ncm', to='sped.registro0000')),
            ],
            options={
                'verbose_name': 'Item NCM',
                'verbose_name_plural': 'Itens NCM',
                'ordering': ['cod_ncm', 'cod_item'],
                'unique_together': {('empresa', 'cod_item')},
            },
        ),
    ]