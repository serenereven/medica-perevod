from django.db import models
from common.models import (
    UUIDPrimaryKeyModel,
    FullContentModel,
    PhoneField,
    NormalizedEmailField,
    TimeStampedModel,
    PublishableModel,
)


class DocumentCategory(TimeStampedModel):
    """Категория документа"""
    name = models.CharField(max_length=100, verbose_name='Название')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория документа"
        verbose_name_plural = "Категории документов"
        ordering = ['name']

class Document(TimeStampedModel, PublishableModel):
    """Документы"""
    
    class DocumentType(models.TextChoices):
        PDF = 'pdf', 'PDF документ'
        WORD = 'word', 'Word документ'
        EXCEL = 'excel', 'Excel таблица'
        IMAGE = 'image', 'Изображение'
        OTHER = 'other', 'Другое'
    
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    file = models.FileField(upload_to='documents/', verbose_name='Документ')
    preview = models.ImageField(
        upload_to='documents/preview/', 
        blank=True, 
        null=True, 
        verbose_name='Превью'
    )
    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        default=DocumentType.OTHER,
        verbose_name='Тип документа'
    )
    document_category = models.ForeignKey(
        'DocumentCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Категория документа',
        related_name='documents'
    )
    file_size = models.PositiveIntegerField(
        blank=True, 
        null=True, 
        editable=False,
        verbose_name='Размер файла (байты)'
    )
    download_count = models.PositiveIntegerField(
        default=0, 
        verbose_name='Количество скачиваний'
    )

    def save(self, *args, **kwargs):
        creating = self.pk is None
        super().save(*args, **kwargs)  # сначала сохраняем, чтобы self.file.path существовал

        if not self.file:
            return

        updated_fields = []

        # Размер файла
        if not self.file_size:
            self.file_size = self.file.size
            updated_fields.append('file_size')

        # Тип документа
        if self.document_type == self.DocumentType.OTHER:
            extension = self.get_file_extension().lower()
            type_map = {
                'pdf': self.DocumentType.PDF,
                'doc': self.DocumentType.WORD,
                'docx': self.DocumentType.WORD,
                'xls': self.DocumentType.EXCEL,
                'xlsx': self.DocumentType.EXCEL,
                'jpg': self.DocumentType.IMAGE,
                'jpeg': self.DocumentType.IMAGE,
                'png': self.DocumentType.IMAGE,
                'gif': self.DocumentType.IMAGE,
            }
            self.document_type = type_map.get(extension, self.DocumentType.OTHER)
            updated_fields.append('document_type')

        if updated_fields:
            super().save(update_fields=updated_fields)


    def __str__(self):
        return self.title
    
    def get_file_size_display(self):
        """Размер файла в читаемом формате"""
        if not self.file_size:
            return "0 Б"
        
        size = float(self.file_size)
        for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} ТБ"
    
    def get_file_extension(self):
        """Расширение файла"""
        import os
        if self.file:
            return os.path.splitext(self.file.name)[1][1:].upper()
        return ""
    
    def increment_downloads(self):
        """Увеличить счетчик скачиваний"""
        self.download_count += 1
        self.save(update_fields=['download_count'])

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['file'],
                name='unique_document_file'
            )
        ]