from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_...'),  # ваша предыдущая миграция
    ]

    operations = [
        # Шаг 1: создаём новую таблицу категорий
        migrations.CreateModel(
            name='DocumentCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Категория документа',
                'verbose_name_plural': 'Категории документов',
                'ordering': ['name'],
            },
        ),

        # Шаг 2: добавляем временный FK-столбец (NULL)
        migrations.AddField(
            model_name='document',
            name='document_category_new',
            field=models.ForeignKey(
                null=True, blank=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='core.documentcategory',
                verbose_name='Категория документа',
            ),
        ),

        # Шаг 3: переносим данные через RunPython
        migrations.RunPython(
            migrate_categories,
            reverse_code=migrations.RunPython.noop,
        ),

        # Шаг 4: удаляем старый CharField
        migrations.RemoveField(
            model_name='document',
            name='document_category',
        ),

        # Шаг 5: переименовываем новый столбец
        migrations.RenameField(
            model_name='document',
            old_name='document_category_new',
            new_name='document_category',
        ),
    ]


def migrate_categories(apps, schema_editor):
    Document = apps.get_model('core', 'Document')
    DocumentCategory = apps.get_model('core', 'DocumentCategory')

    # Создаём категории из старых TextChoices
    mapping = {
        'translate': 'Переводы',
        'other': 'Другое',
    }
    category_objects = {}
    for slug, name in mapping.items():
        obj, _ = DocumentCategory.objects.get_or_create(name=name)
        category_objects[slug] = obj

    # Переносим значения
    for doc in Document.objects.all():
        old_value = doc.document_category  # ещё строка, т.к. старое поле
        doc.document_category_new = category_objects.get(old_value)
        doc.save(update_fields=['document_category_new'])