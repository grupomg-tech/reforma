# Generated migration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sped', '0002_registro0200_registroc100_registroc170'),
    ]

    operations = [
        migrations.CreateModel(
            name='Registro0150',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cod_part', models.CharField(max_length=60, verbose_name='Código do Participante')),
                ('nome', models.CharField(max_length=200, verbose_name='Nome/Razão Social')),
                ('cnpj', models.CharField(blank=True, max_length=14, verbose_name='CNPJ')),
                ('cpf', models.CharField(blank=True, max_length=11, verbose_name='CPF')),
                ('ie', models.CharField(blank=True, max_length=20, verbose_name='Inscrição Estadual')),
                ('cod_mun', models.CharField(blank=True, max_length=7, verbose_name='Código Município')),
                ('uf', models.CharField(blank=True, max_length=2, verbose_name='UF')),
                ('endereco', models.CharField(blank=True, max_length=200, verbose_name='Endereço')),
                ('situacao_cadastral', models.CharField(blank=True, max_length=50, verbose_name='Situação Cadastral')),
                ('optante_simples', models.BooleanField(blank=True, null=True, verbose_name='Optante Simples Nacional')),
                ('data_opcao_simples', models.DateField(blank=True, null=True, verbose_name='Data Opção Simples')),
                ('data_exclusao_simples', models.DateField(blank=True, null=True, verbose_name='Data Exclusão Simples')),
                ('optante_mei', models.BooleanField(blank=True, null=True, verbose_name='Optante MEI')),
                ('natureza_juridica', models.CharField(blank=True, max_length=100, verbose_name='Natureza Jurídica')),
                ('porte', models.CharField(blank=True, max_length=50, verbose_name='Porte')),
                ('cnae_principal', models.CharField(blank=True, max_length=10, verbose_name='CNAE Principal')),
                ('descricao_cnae', models.CharField(blank=True, max_length=200, verbose_name='Descrição CNAE')),
                ('consultado', models.BooleanField(default=False, verbose_name='Consultado')),
                ('data_consulta', models.DateTimeField(blank=True, null=True, verbose_name='Data da Consulta')),
                ('erro_consulta', models.TextField(blank=True, verbose_name='Erro na Consulta')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('registro_0000', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participantes', to='sped.registro0000')),
            ],
            options={
                'verbose_name': 'Participante (Registro 0150)',
                'verbose_name_plural': 'Participantes (Registros 0150)',
                'unique_together': {('registro_0000', 'cod_part')},
            },
        ),
    ]