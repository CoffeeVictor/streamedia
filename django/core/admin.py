from core.models import Tag, Video

from django.contrib import admin


# Register your models here.
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    filter_horizontal = ('tags',)


admin.site.register(Tag)
