# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-14 16:27
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def forward(apps, schema_editor):
    User = apps.get_model(settings.AUTH_USER_MODEL)
    Membership = apps.get_model("nadine", "Membership")
    MembershipPlan = apps.get_model("nadine", "MembershipPlan")
    Membership2 = apps.get_model("nadine", "Membership2")
    IndividualMembership = apps.get_model("nadine", "IndividualMembership")
    MembershipPackage = apps.get_model("nadine", "MembershipPackage")
    DefaultAllowance = apps.get_model("nadine", "DefaultAllowance")
    ResourceAllowance = apps.get_model("nadine", "ResourceAllowance")
    Resource = apps.get_model("nadine", "Resource")
    print

    print("    Creating Resources and Defaults...")
    DAY = Resource.objects.create(name="Coworking Day")
    DESK = Resource.objects.create(name="Dedicated Desk")
    MAIL = Resource.objects.create(name="Mail Service")
    KEY = Resource.objects.create(name="Key")
    DAY_DEFAULT = DefaultAllowance.objects.create(resource=DAY, allowance=0, monthly_rate=0, overage_rate=0)
    DESK_DEFAULT = DefaultAllowance.objects.create(resource=DESK, allowance=0, monthly_rate=0, overage_rate=0)
    MAIL_DEFAULT = DefaultAllowance.objects.create(resource=MAIL, allowance=0, monthly_rate=0, overage_rate=0)
    KEY_DEFAULT = DefaultAllowance.objects.create(resource=KEY, allowance=0, monthly_rate=0, overage_rate=0)

    print("    Migrating Membership Plans to Packages...")
    for plan in MembershipPlan.objects.all():
        package = MembershipPackage.objects.create(name=plan.name)
        day_default = DefaultAllowance.objects.create(resource=DAY, allowance=plan.dropin_allowance, monthly_rate=plan.monthly_rate, overage_rate=plan.daily_rate)
        package.allowances.add(day_default)
        if plan.has_desk:
            desk_default = DefaultAllowance.objects.create(resource=DESK, allowance=1, monthly_rate=0, overage_rate=0)
            package.allowances.add(day_default)

    print("    Migrating Memberships...")
    for user in User.objects.all():
        old_memberships = Membership.objects.filter(user=user).order_by('start_date')
        if old_memberships:
            new_membership = IndividualMembership.objects.create(user=user)
            for m in old_memberships:
                # package = MembershipPackage.objects.get(name=m.membership_plan.name)
                # day_default = package.allowances.filter(resource=DAY).first()
                day_allowance = ResourceAllowance.objects.create(resource=DAY,
                    start_date = m.start_date,
                    end_date = m.end_date,
                    monthly_rate = m.monthly_rate,
                    allowance = m.dropin_allowance,
                    overage_rate = m.daily_rate,
                    paid_by = m.paid_by,
                    default = DAY_DEFAULT,
                )
                new_membership.allowances.add(day_allowance)
                if m.has_desk:
                    desk_allowance = ResourceAllowance.objects.create(resource=DESK,
                        start_date = m.start_date,
                        end_date = m.end_date,
                        monthly_rate = 0,
                        allowance = 1,
                        overage_rate = 0,
                        paid_by = m.paid_by,
                        default = DESK_DEFAULT,
                    )
                    new_membership.allowances.add(desk_allowance)
                if m.has_mail:
                    mail_allowance = ResourceAllowance.objects.create(resource=MAIL,
                        start_date = m.start_date,
                        end_date = m.end_date,
                        monthly_rate = 0,
                        allowance = 1,
                        overage_rate = 0,
                        paid_by = m.paid_by,
                        default = MAIL_DEFAULT,
                    )
                    new_membership.allowances.add(mail_allowance)
                if m.has_key:
                    key_allowance = ResourceAllowance.objects.create(resource=KEY,
                        start_date = m.start_date,
                        end_date = m.end_date,
                        monthly_rate = 0,
                        allowance = 1,
                        overage_rate = 0,
                        paid_by = m.paid_by,
                        default = KEY_DEFAULT,
                    )
                    new_membership.allowances.add(key_allowance)
                new_membership.save()


def reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('nadine', '0026_bill_in_progress'),
    ]

    operations = [
        migrations.CreateModel(
            name='DefaultAllowance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allowance', models.IntegerField(default=0)),
                ('monthly_rate', models.DecimalField(decimal_places=2, max_digits=9)),
                ('overage_rate', models.DecimalField(decimal_places=2, max_digits=9)),
            ],
        ),
        migrations.CreateModel(
            name='Membership2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='MembershipPackage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('allowances', models.ManyToManyField(to='nadine.DefaultAllowance')),
            ],
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                # ('default_monthly_rate', models.DecimalField(decimal_places=2, max_digits=9)),
                # ('default_overage_rate', models.DecimalField(decimal_places=2, max_digits=9)),
            ],
        ),
        migrations.CreateModel(
            name='ResourceAllowance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_ts', models.DateTimeField(auto_now_add=True)),
                ('allowance', models.IntegerField(default=0)),
                ('start_date', models.DateField(db_index=True)),
                ('end_date', models.DateField(blank=True, db_index=True, null=True)),
                ('monthly_rate', models.DecimalField(decimal_places=2, max_digits=9)),
                ('overage_rate', models.DecimalField(decimal_places=2, max_digits=9)),
                ('bill_day', models.SmallIntegerField(default=0)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('default', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nadine.DefaultAllowance')),
                ('paid_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('resource', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nadine.Resource')),
            ],
        ),
        migrations.AlterField(
            model_name='membership',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='IndividualMembership',
            fields=[
                ('membership2_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='nadine.Membership2')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='membership', to=settings.AUTH_USER_MODEL)),
            ],
            bases=('nadine.membership2',),
        ),
        migrations.CreateModel(
            name='OrganizationMembership',
            fields=[
                ('membership2_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='nadine.Membership2')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='membership', to='nadine.Organization')),
            ],
            bases=('nadine.membership2',),
        ),
        migrations.AddField(
            model_name='membership2',
            name='allowances',
            field=models.ManyToManyField(to='nadine.ResourceAllowance'),
        ),
        migrations.AddField(
            model_name='defaultallowance',
            name='resource',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nadine.Resource'),
        ),
        migrations.RunPython(forward, reverse),
        # migrations.RenameModel(
        #     old_name='Membership2',
        #     new_name='Membership',
        # ),
        # migrations.RenameField(
        #     model_name='individualmembership',
        #     old_name='membership2_ptr',
        #     new_name='membership_ptr',
        # ),
        # migrations.RenameField(
        #     model_name='organizationmembership',
        #     old_name='membership2_ptr',
        #     new_name='membership_ptr',
        # ),
]
