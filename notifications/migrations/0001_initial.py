# Generated migration for notifications app
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserNotificationSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_new_message', models.BooleanField(default=True)),
                ('email_new_assignment', models.BooleanField(default=True)),
                ('email_new_announcement', models.BooleanField(default=True)),
                ('email_grade_posted', models.BooleanField(default=True)),
                ('notify_new_message', models.BooleanField(default=True)),
                ('notify_new_assignment', models.BooleanField(default=True)),
                ('notify_new_announcement', models.BooleanField(default=True)),
                ('notify_grade_posted', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='notification_settings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Notification Setting',
                'verbose_name_plural': 'User Notification Settings',
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('MESSAGE', 'New Message'), ('ASSIGNMENT', 'New Assignment'), ('ANNOUNCEMENT', 'New Announcement'), ('GRADE', 'Grade Posted'), ('ATTENDANCE', 'Attendance Alert'), ('CALENDAR', 'Calendar Event'), ('SYSTEM', 'System Notification')], max_length=20)),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('action_url', models.CharField(blank=True, max_length=500)),
                ('action_text', models.CharField(blank=True, max_length=50)),
                ('related_object_id', models.IntegerField(blank=True, null=True)),
                ('related_object_type', models.CharField(blank=True, max_length=50)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['recipient', '-created_at'], name='notificatio_recipie_8c9e5d_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['recipient', 'is_read'], name='notificatio_recipie_0e1a8f_idx'),
        ),
    ]
