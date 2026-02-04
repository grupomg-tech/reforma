# Generated migration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sped', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Registro0200',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cod_item', models.CharField(max_length=60, verbose_name='Código do Item')),
                ('descr_item', models.TextField(verbose_name='Descrição do Item')),
                ('cod_barra', models.CharField(blank=True, max_length=14, verbose_name='Código de Barras')),
                ('unid_inv', models.CharField(blank=True, max_length=6, verbose_name='Unidade de Inventário')),
                ('tipo_item', models.CharField(blank=True, max_length=2, verbose_name='Tipo do Item')),
                ('cod_ncm', models.CharField(blank=True, max_length=8, verbose_name='NCM')),
                ('cest', models.CharField(blank=True, max_length=7, verbose_name='CEST')),
                ('aliq_icms', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='Alíquota ICMS')),
                ('registro_0000', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens', to='sped.registro0000')),
            ],
            options={
                'verbose_name': 'Item (Registro 0200)',
                'verbose_name_plural': 'Itens (Registros 0200)',
                'unique_together': {('registro_0000', 'cod_item')},
            },
        ),
        migrations.CreateModel(
            name='RegistroC100',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ind_oper', models.CharField(max_length=1, verbose_name='Indicador de Operação')),
                ('ind_emit', models.CharField(max_length=1, verbose_name='Indicador do Emitente')),
                ('cod_part', models.CharField(blank=True, max_length=60, verbose_name='Código do Participante')),
                ('cod_mod', models.CharField(max_length=2, verbose_name='Código do Modelo')),
                ('cod_sit', models.CharField(max_length=2, verbose_name='Código da Situação')),
                ('ser', models.CharField(blank=True, max_length=3, verbose_name='Série')),
                ('num_doc', models.CharField(max_length=9, verbose_name='Número do Documento')),
                ('chv_nfe', models.CharField(blank=True, max_length=44, verbose_name='Chave NF-e')),
                ('dt_doc', models.DateField(blank=True, null=True, verbose_name='Data do Documento')),
                ('dt_e_s', models.DateField(blank=True, null=True, verbose_name='Data Entrada/Saída')),
                ('vl_doc', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Valor do Documento')),
                ('vl_merc', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Valor das Mercadorias')),
                ('vl_icms', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Valor do ICMS')),
                ('vl_pis', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Valor do PIS')),
                ('vl_cofins', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Valor do COFINS')),
                ('registro_0000', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documentos_c100', to='sped.registro0000')),
            ],
            options={
                'verbose_name': 'Documento C100',
                'verbose_name_plural': 'Documentos C100',
            },
        ),
        migrations.CreateModel(
            name='RegistroC170',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_item', models.CharField(max_length=3, verbose_name='Número do Item')),
                ('cod_item', models.CharField(max_length=60, verbose_name='Código do Item')),
                ('descr_compl', models.TextField(blank=True, verbose_name='Descrição Complementar')),
                ('qtd', models.DecimalField(decimal_places=5, default=0, max_digits=15, verbose_name='Quantidade')),
                ('unid', models.CharField(blank=True, max_length=6, verbose_name='Unidade')),
                ('vl_item', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Valor do Item')),
                ('vl_desc', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Valor do Desconto')),
                ('cst_icms', models.CharField(blank=True, max_length=3, verbose_name='CST ICMS')),
                ('cfop', models.CharField(blank=True, max_length=4, verbose_name='CFOP')),
                ('cod_nat', models.CharField(blank=True, max_length=10, verbose_name='Código Natureza')),
                ('vl_bc_icms', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Base ICMS')),
                ('aliq_icms', models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name='Alíquota ICMS')),
                ('vl_icms', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Valor ICMS')),
                ('cst_pis', models.CharField(blank=True, max_length=2, verbose_name='CST PIS')),
                ('vl_bc_pis', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Base PIS')),
                ('aliq_pis', models.DecimalField(decimal_places=4, default=0, max_digits=8, verbose_name='Alíquota PIS')),
                ('vl_pis', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Valor PIS')),
                ('cst_cofins', models.CharField(blank=True, max_length=2, verbose_name='CST COFINS')),
                ('vl_bc_cofins', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Base COFINS')),
                ('aliq_cofins', models.DecimalField(decimal_places=4, default=0, max_digits=8, verbose_name='Alíquota COFINS')),
                ('vl_cofins', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Valor COFINS')),
                ('cod_ncm', models.CharField(blank=True, max_length=8, verbose_name='NCM')),
                ('registro_c100', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens', to='sped.registroc100')),
            ],
            options={
                'verbose_name': 'Item C170',
                'verbose_name_plural': 'Itens C170',
            },
        ),
    ]