# Generated by Django 4.0.5 on 2023-01-05 07:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agent_candidate', '0002_candidateformmodels_agsined_to'),
    ]

    operations = [
        migrations.RenameField(
            model_name='candidateformmodels',
            old_name='agsined_to',
            new_name='asigned_to',
        ),
    ]
