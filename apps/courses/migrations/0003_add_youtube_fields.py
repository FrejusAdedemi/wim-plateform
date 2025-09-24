# apps/courses/migrations/0003_add_youtube_fields.py

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_initial'),
    ]

    operations = [
        # Ajout des champs YouTube au modèle Course
        migrations.AddField(
            model_name='course',
            name='youtube_playlist_id',
            field=models.CharField(
                max_length=100,
                blank=True,
                verbose_name='ID Playlist YouTube'
            ),
        ),
        migrations.AddField(
            model_name='course',
            name='youtube_channel_id',
            field=models.CharField(
                max_length=100,
                blank=True,
                verbose_name='ID Chaîne YouTube'
            ),
        ),
        migrations.AddField(
            model_name='course',
            name='youtube_channel_name',
            field=models.CharField(
                max_length=200,
                blank=True,
                verbose_name='Nom Chaîne YouTube'
            ),
        ),
        migrations.AddField(
            model_name='course',
            name='youtube_thumbnail_url',
            field=models.URLField(
                blank=True,
                verbose_name='URL Miniature YouTube'
            ),
        ),
        migrations.AddField(
            model_name='course',
            name='is_youtube_synced',
            field=models.BooleanField(
                default=False,
                verbose_name='Synchronisé YouTube'
            ),
        ),
        migrations.AddField(
            model_name='course',
            name='last_youtube_sync',
            field=models.DateTimeField(
                null=True,
                blank=True,
                verbose_name='Dernière sync YouTube'
            ),
        ),

        # Ajout des champs YouTube au modèle Lesson
        migrations.AddField(
            model_name='lesson',
            name='youtube_video_id',
            field=models.CharField(
                max_length=20,
                blank=True,
                verbose_name='ID Vidéo YouTube'
            ),
        ),
        migrations.AddField(
            model_name='lesson',
            name='youtube_title',
            field=models.CharField(
                max_length=300,
                blank=True,
                verbose_name='Titre YouTube'
            ),
        ),
        migrations.AddField(
            model_name='lesson',
            name='youtube_description',
            field=models.TextField(
                blank=True,
                verbose_name='Description YouTube'
            ),
        ),
        migrations.AddField(
            model_name='lesson',
            name='youtube_thumbnail_url',
            field=models.URLField(
                blank=True,
                verbose_name='Miniature YouTube'
            ),
        ),
        migrations.AddField(
            model_name='lesson',
            name='youtube_duration_seconds',
            field=models.IntegerField(
                null=True,
                blank=True,
                verbose_name='Durée YouTube (sec)'
            ),
        ),
        migrations.AddField(
            model_name='lesson',
            name='youtube_view_count',
            field=models.IntegerField(
                default=0,
                verbose_name='Vues YouTube'
            ),
        ),
        migrations.AddField(
            model_name='lesson',
            name='youtube_published_at',
            field=models.DateTimeField(
                null=True,
                blank=True,
                verbose_name='Publié sur YouTube'
            ),
        ),
    ]