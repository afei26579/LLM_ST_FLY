# Generated manually to fix painting_url length

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0002_poetrypaintingconversation_poetrypaintingwork_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poetrypaintingwork',
            name='painting_url',
            field=models.URLField(max_length=1000, blank=True, null=True, verbose_name='画作URL'),
        ),
    ]

