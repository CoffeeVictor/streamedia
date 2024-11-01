from core.models import Tag, Video

from django.contrib import admin
from django.urls import path
from django.urls.resolvers import URLPattern


# Register your models here.
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    filter_horizontal = ('tags',)

    def get_urls(self) -> list[URLPattern]:
        base_urls = super().get_urls()
        custom_urls = [
            path('<int:id>/video_upload', self.upload_video,
                 name='core_video_upload')
        ]

        return base_urls + custom_urls

    def upload_video(self):
        pass


admin.site.register(Tag)
