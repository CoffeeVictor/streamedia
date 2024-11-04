# Generated by Django 5.1.2 on 2024-11-04 07:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_video_author_alter_videomedia_video'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='videos', to=settings.AUTH_USER_MODEL, verbose_name='Author'),
        ),
    ]
