from django.db import migrations, models
import django.db.models.deletion


def migrate_categories(apps, schema_editor):
    Document = apps.get_model('core', 'Document')
    DocumentCategory = apps.get_model('core', 'DocumentCategory')

    mapping = {
        'translate': 'Переводы',
        'other': 'Другое',
    }
    category_objects = {}
    for slug, name in mapping.items():
        obj, _ = DocumentCategory.objects.get_or_create(name=name)
        category_objects[slug] = obj

    for doc in Document.objects.all():
        old_value = doc.document_category_old
        doc.document_category_new = category_objects.get(old_value)
        doc.save(update_fields=['document_category_new'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_document_file_alter_document_preview_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Категория документа',
                'verbose_name_plural': 'Категории документов',
                'ordering': ['name'],
            },
        ),
        migrations.RenameField(
            model_name='document',
            old_name='document_category',
            new_name='document_category_old',
        ),
        migrations.AddField(
            model_name='document',
            name='document_category_new',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='core.documentcategory',
                verbose_name='Категория документа',
            ),
        ),
        migrations.RunPython(
            migrate_categories,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RemoveField(
            model_name='document',
            name='document_category_old',
        ),
        migrations.RenameField(
            model_name='document',
            old_name='document_category_new',
            new_name='document_category',
        ),
    ]