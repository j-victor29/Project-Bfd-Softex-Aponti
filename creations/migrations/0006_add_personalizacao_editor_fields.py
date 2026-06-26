import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creations', '0005_alter_arte_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='personalizacao',
            name='tamanho_fonte',
            field=models.IntegerField(default=24, help_text='Tamanho da fonte do texto personalizado (8 a 72)'),
        ),
        migrations.AddField(
            model_name='personalizacao',
            name='posicao_x',
            field=models.IntegerField(default=50, help_text='Posição horizontal do texto (0 a 100, representa %)'),
        ),
        migrations.AddField(
            model_name='personalizacao',
            name='posicao_y',
            field=models.IntegerField(default=50, help_text='Posição vertical do texto (0 a 100, representa %)'),
        ),
        migrations.AddField(
            model_name='personalizacao',
            name='observacoes',
            field=models.TextField(blank=True, help_text='Observações adicionais para a personalização'),
        ),
        migrations.AddField(
            model_name='personalizacao',
            name='usuario',
            field=models.ForeignKey(
                blank=True,
                help_text='Usuário que criou a personalização',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='personalizacoes',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
