from django.db import migrations


def move_to_certification(apps, schema_editor):
    """Move every AdditionalCertification and every ExperienceEntry into Certification.

    All existing ExperienceEntry rows are certificates (confirmed by Bunny).
    File paths are copied as-is; nothing in media/ is touched.
    """
    AdditionalCertification = apps.get_model('portfolio', 'AdditionalCertification')
    ExperienceEntry = apps.get_model('portfolio', 'ExperienceEntry')
    Certification = apps.get_model('portfolio', 'Certification')

    # Keep today's About page order: former experience certificates first,
    # then the old "Additional Certifications".
    entries = list(ExperienceEntry.objects.all())
    offset = max((entry.order for entry in entries), default=-1) + 1

    for cert in AdditionalCertification.objects.all():
        Certification.objects.create(
            title=cert.title,
            certificate_file=cert.certificate_file.name or None,
            order=cert.order + offset,
        )

    for entry in entries:
        Certification.objects.create(
            title=entry.role,
            issuer=entry.organization,
            category=entry.year_label,
            certificate_file=entry.certificate_file.name or None,
            certificate_file_2=entry.certificate_file_2.name or None,
            order=entry.order,
        )
    ExperienceEntry.objects.all().delete()
    AdditionalCertification.objects.all().delete()


def restore_from_certification(apps, schema_editor):
    """Reverse: rows with an issuer go back to ExperienceEntry, the rest to AdditionalCertification."""
    AdditionalCertification = apps.get_model('portfolio', 'AdditionalCertification')
    ExperienceEntry = apps.get_model('portfolio', 'ExperienceEntry')
    Certification = apps.get_model('portfolio', 'Certification')

    for cert in Certification.objects.all():
        if cert.issuer:
            ExperienceEntry.objects.create(
                year_label=cert.category,
                organization=cert.issuer,
                role=cert.title,
                certificate_file=cert.certificate_file.name or None,
                certificate_file_2=cert.certificate_file_2.name or None,
                order=cert.order,
            )
        else:
            AdditionalCertification.objects.create(
                title=cert.title,
                certificate_file=cert.certificate_file.name or None,
                order=cert.order,
            )
    Certification.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0015_experience_fields_and_certification'),
    ]

    operations = [
        migrations.RunPython(move_to_certification, restore_from_certification),
    ]
