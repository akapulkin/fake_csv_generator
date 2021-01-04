from django.db import models
from .choices import COLUMN_SEPARATOR, STRING_CHARACTER, TYPES, DATASET_STATUS


class Schema(models.Model):
    name = models.CharField(max_length=120, verbose_name='Name', blank=False)
    column_separator = models.CharField(max_length=20, verbose_name='Column separator',
                                        choices=COLUMN_SEPARATOR, blank=False)
    string_character = models.CharField(max_length=20, verbose_name='String character',
                                        choices=STRING_CHARACTER, blank=False)
    modified_date = models.DateField(verbose_name='Modified', auto_now=True)


class SchemaColumn(models.Model):
    schema = models.ForeignKey(Schema, on_delete=models.CASCADE)
    column_name = models.CharField(max_length=120, verbose_name='Column name', blank=False)
    column_type = models.CharField(max_length=50, choices=TYPES, blank=False, verbose_name='Type')
    range_from = models.IntegerField(verbose_name='From', blank=True, null=True)
    range_to = models.IntegerField(verbose_name='To', blank=True, null=True)
    order = models.IntegerField(verbose_name='Order', blank=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['schema', 'order'],
                name='unique order'
            )
        ]


class SchemaDataset(models.Model):
    schema = models.ForeignKey(Schema, on_delete=models.CASCADE)
    created = models.DateField(verbose_name='Created', auto_now=True)
    status = models.CharField(max_length=20, verbose_name='Status', choices=DATASET_STATUS,
                              default='processing', blank=False)
    link = models.CharField(max_length=120, verbose_name='link', blank=True, null=True)
    rows_quantity = models.IntegerField(verbose_name='rows_quantity', blank=False, null=True)
    task_id = models.CharField(max_length=120, verbose_name='task_id', blank=True, null=True)

# TODO Strings and Admin Views
