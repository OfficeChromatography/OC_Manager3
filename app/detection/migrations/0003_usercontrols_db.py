# Generated by Django 3.0.5 on 2020-06-24 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('detection', '0002_cameracontrols_db'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserControls_Db',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brightness', models.DecimalField(blank=True, decimal_places=0, max_digits=3, null=True)),
                ('contrast', models.DecimalField(blank=True, decimal_places=0, max_digits=3, null=True)),
                ('saturation', models.DecimalField(blank=True, decimal_places=0, max_digits=3, null=True)),
                ('red_balance', models.DecimalField(blank=True, decimal_places=0, max_digits=4, null=True)),
                ('blue_balance', models.DecimalField(blank=True, decimal_places=0, max_digits=4, null=True)),
                ('horizontal_flip', models.BooleanField(blank=True, null=True)),
                ('vertical_flip', models.BooleanField(blank=True, null=True)),
                ('power_line_frequency', models.CharField(blank=True, choices=[(0, 'Disable'), (1, '50 Hz'), (2, '60 Hz'), (3, 'Auto')], max_length=255, null=True)),
                ('sharpness', models.DecimalField(blank=True, decimal_places=0, max_digits=3, null=True)),
                ('color_effects', models.CharField(blank=True, choices=[(10, 'Aqua'), (7, 'Grass Green'), (4, 'Emboss'), (3, 'Negative'), (13, 'Solarization'), (9, 'Vivid'), (8, 'Skin Whiten'), (0, 'None'), (14, 'Set Cb/Cr'), (11, 'Art Freeze'), (12, 'Silhouette'), (2, 'Sepia'), (5, 'Sketch'), (1, 'Black & White'), (6, 'Sky Blue')], max_length=255, null=True)),
                ('rotate', models.DecimalField(blank=True, decimal_places=0, max_digits=3, null=True)),
                ('color_effects_cbcr', models.DecimalField(blank=True, decimal_places=0, max_digits=5, null=True)),
            ],
        ),
    ]