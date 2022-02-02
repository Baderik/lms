# Generated by Django 3.1.8 on 2021-12-30 09:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lesson', '0003_delete_lessonprogress'),
        ('course', '0010_auto_20211111_0559'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rating', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance', to='course.course'),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='lesson',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance', to='lesson.lesson'),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user'),
        ),
        migrations.AlterField(
            model_name='courseprogress',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progress', to='course.course'),
        ),
        migrations.AlterField(
            model_name='courseprogress',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user'),
        ),
        migrations.AlterField(
            model_name='lessonprogress',
            name='attendance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lesson_attendance', to='rating.attendance'),
        ),
        migrations.AlterField(
            model_name='lessonprogress',
            name='lesson',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progress', to='lesson.lesson'),
        ),
        migrations.AlterField(
            model_name='lessonprogress',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user'),
        ),
    ]