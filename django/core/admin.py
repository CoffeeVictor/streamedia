from urllib.request import Request

from core.forms import VideoChunkUploadForm
from core.models import Tag, Video
from core.services import VideoService, create_video_service_factory

from django.contrib import admin
from django.contrib.auth.admin import csrf_protect_m
from django.http import JsonResponse
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
                 name='core_video_upload'),
            path('<int:object_id>/video_upload/finish',
                 self.video_upload_finish, name='core_video_upload_finish')
        ]

        return base_urls + custom_urls

    def redirect_to_upload(self, video: Video):
        url = reverse('admin:core_video_upload', args=[video.id])
        return format_html(f'<a href="{url}">Upload</a>')

    redirect_to_upload.short_description = 'Upload'

    @csrf_protect_m
    def upload_video(self, request: Request, object_id: int):

        if request.method == 'POST':
            form = VideoChunkUploadForm(request.POST, request.FILES)

            if not form.is_valid():
                return JsonResponse({
                    "errors": form.errors
                }, status=400)
            video_service = create_video_service_factory()
            video_service.process_upload(video_id=object_id,
                                         chunk_index=form.cleaned_data['chunkIndex'], chunks=form.cleaned_data['chunk'].read())

        return render(request, 'admin/core/video_upload.html', {
            'id': object_id
        })

    def video_upload_finish(self, request: Request, object_id: int):
        print('Upload finish fn')


admin.site.register(Tag)
