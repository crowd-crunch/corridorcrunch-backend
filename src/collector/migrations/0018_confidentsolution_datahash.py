from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collector', '0017_auto_20200118_1721'),
    ]

    operations = [
        migrations.AddField(
            model_name='confidentsolution',
            name='datahash',
            field=models.CharField(default='', max_length=64, verbose_name='sha256 hash for easier comparisons'),
        ),
    ]
