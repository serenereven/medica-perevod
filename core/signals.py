import logging
import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from core.models import Document

log = logging.getLogger(__name__)

def _remove(field):
    if not field:
        return
    try:
        path = field.path
    except (ValueError, NotImplementedError):
        return
    if os.path.isfile(path):
        try:
            os.remove(path)
            log.info('Файл удалён с диска: %s', path)
        except OSError as exc:
            log.warning('Не удалось удалить файл %s: %s', path, exc)

@receiver(post_delete, sender=Document)
def delete_files_on_record_delete(sender, instance, **kwargs):
    """Удаляет файл и превью при удалении записи."""
    _remove(instance.file)
    _remove(instance.preview)

@receiver(pre_save, sender=Document)
def delete_old_file_on_replace(sender, instance, **kwargs):
    """Удаляет старый файл, если в админке загрузили новый."""
    if not instance.pk:
        return
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    if old.file and old.file != instance.file:
        _remove(old.file)
    if old.preview and old.preview != instance.preview:
        _remove(old.preview)