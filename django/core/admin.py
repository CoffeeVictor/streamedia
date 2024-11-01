from core.models import Tag, Video

from django.contrib import admin
from django.shortcuts import render
from django.urls import path, reverse
from django.urls.resolvers import URLPattern
from django.utils.html import format_html


# Register your models here.
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    filter_horizontal = ('tags',)
    list_display = ('title', 'published_at', 'is_published',
                    'num_likes', 'num_views', 'redirect_to_upload', )

    def get_urls(self) -> list[URLPattern]:
        base_urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/video_upload', self.upload_video,
                 name='core_video_upload')
        ]

        return base_urls + custom_urls

    def redirect_to_upload(self, video: Video):
        url = reverse('admin:core_video_upload', args=[video.id])
        return format_html(f'<a href="{url}">Upload</a>')

    redirect_to_upload.short_description = 'Upload'

    def upload_video(self, request, object_id):
        print('Request:', request)
        return render(request, 'admin/core/video_upload.html')


admin.site.register(Tag)
