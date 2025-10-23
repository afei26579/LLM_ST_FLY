# Manual migration to fix painting_url field length

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0003_alter_poetrypaintingwork_painting_url'),
    ]

    operations = [
        migrations.RunSQL(
            # 修改 painting_url 字段长度为 1000
            sql="ALTER TABLE agent_poetry_painting_work ALTER COLUMN painting_url TYPE VARCHAR(1000);",
            reverse_sql="ALTER TABLE agent_poetry_painting_work ALTER COLUMN painting_url TYPE VARCHAR(200);"
        ),
    ]

