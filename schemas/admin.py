from django.contrib import admin
from .models import Schema, SchemaColumn, SchemaDataset

admin.site.register(Schema)
admin.site.register(SchemaColumn)
admin.site.register(SchemaDataset)
