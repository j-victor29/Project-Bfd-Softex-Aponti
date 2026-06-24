from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0002_user_documento'),
        ('creations', '0004_alter_arte_options_alter_colecao_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Carrinho',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('aberto', 'Aberto'), ('finalizado', 'Finalizado'), ('cancelado', 'Cancelado')], default='aberto', max_length=20)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carrinhos', to='users.user')),
            ],
            options={
                'verbose_name': 'Carrinho',
                'verbose_name_plural': 'Carrinhos',
                'ordering': ['-criado_em'],
            },
        ),
        migrations.CreateModel(
            name='ItemCarrinho',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('preco_unitario', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('subtotal', models.DecimalField(decimal_places=2, editable=False, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('carrinho', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens', to='cart.carrinho')),
                ('personalizacao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens_carrinho', to='creations.personalizacao')),
            ],
            options={
                'verbose_name': 'Item do Carrinho',
                'verbose_name_plural': 'Itens do Carrinho',
                'ordering': ['criado_em'],
            },
        ),
    ]
