from django.contrib import admin
from .models import Job, Application
import csv
from django.http import HttpResponse

admin.site.register(Application)
def export_as_csv(modeladmin, request, queryset):
    """
    A Django admin action to export selected objects as a CSV file.
    This action uses the modeladmin's `list_display` to determine which
    fields to include in the export, avoiding sensitive data.
    """
    meta = modeladmin.model._meta
    # Use list_display to define the fields to export.
    # Fallback to all fields if list_display is not set.
    field_names = [field for field in getattr(modeladmin, 'list_display', []) if field != 'action_checkbox']
    if not field_names:
        field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={meta.verbose_name_plural}.csv'
    writer = csv.writer(response)

    writer.writerow(field_names)
    for obj in queryset:
        row = writer.writerow([getattr(obj, field) for field in field_names])

    return response

export_as_csv.short_description = "Export Selected as CSV"

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'state', 'work_style', 'date')
    list_filter = ('work_style', 'visa_sponsorship', 'state', 'country')
    search_fields = ('title', 'description', 'skills')
    actions = [export_as_csv]