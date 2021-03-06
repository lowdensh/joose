# Generated by Django 3.2.2 on 2021-05-10 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'ordering': ['-is_superuser', '-is_staff', 'last_name', 'first_name']},
        ),
        migrations.AlterField(
            model_name='customuser',
            name='dob',
            field=models.DateField(default='1990-01-01', help_text='YYYY-MM-DD e.g. 1990-01-30', verbose_name='date of birth'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(max_length=30, verbose_name='first name'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=30, verbose_name='last name'),
        ),
        migrations.AddConstraint(
            model_name='customuser',
            constraint=models.CheckConstraint(check=models.Q(('email', ''), _negated=True), name='users_customuser_email_not_blank'),
        ),
        migrations.AddConstraint(
            model_name='customuser',
            constraint=models.CheckConstraint(check=models.Q(('first_name', ''), _negated=True), name='users_customuser_first_name_not_blank'),
        ),
    ]
