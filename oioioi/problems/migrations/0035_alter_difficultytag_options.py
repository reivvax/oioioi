# Generated by Django 4.2.17 on 2025-03-08 22:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0034_alter_problem_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='difficultytag',
            options={'ordering': ['pk'], 'verbose_name': 'difficulty tag', 'verbose_name_plural': 'difficulty tags'},
        ),
    ]
