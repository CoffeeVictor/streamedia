import traceback

from core.forms import VideoChunkFinishUploadForm, VideoChunkUploadForm
from core.models import Tag, Video
from core.services import (VideoChunkUploadException,
                           VideoMediaInvalidStatusException,
                           VideoMediaNotExistsException,
                           create_video_service_factory)

from django.contrib import admin, messages
from django.contrib.auth.admin import csrf_protect_m
from django.http import HttpRequest, JsonResponse
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

    def get_readonly_fields(self, request: HttpRequest, obj: Video | None) -> list[str]:
        return ['video_status', 'is_published', 'published_at', 'num_likes', 'num_views', 'author'] if not obj else [
            'video_status', 'published_at', 'num_likes', 'num_views', 'author'
        ]

    def video_status(self, obj: Video) -> str:
        return obj.get_video_status_display()

    def get_urls(self) -> list[URLPattern]:
        base_urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/video_upload', self.admin_site.admin_view(self.upload_video_view),
                 name='core_video_upload'),
            path('<int:object_id>/video_upload/finish',
                 self.admin_site.admin_view(self.video_upload_finish_view), name='core_video_upload_finish')
        ]

        return base_urls + custom_urls

    def redirect_to_upload(self, video: Video):
        url = reverse('admin:core_video_upload', args=[video.id])
        return format_html(f'<a href="{url}">Upload</a>')

    redirect_to_upload.short_description = 'Upload'

    @csrf_protect_m
    def upload_video_view(self, request: HttpRequest, object_id: int):

        str_id = str(object_id)

        if request.method == 'POST':
            return self._do_upload_video_in_chunks(request, object_id)

        try:
            video = create_video_service_factory().find_video(object_id)
            context = dict(
                # Include common variables for rendering the admin template.
                self.admin_site.each_context(request),
                opts=self.model._meta,
                id=object_id,
                video=video,
                video_media=video.video_media if hasattr(
                    video, 'video_media') else None,
                has_view_permission=True
            )
            return render(request, 'admin/core/video_upload.html', context)
        except Video.DoesNotExist:
            return self._get_obj_does_not_exist_redirect(
                request, self.opts, str_id
            )

    def _do_upload_video_in_chunks(self, request: HttpRequest, object_id: int):
        form = VideoChunkUploadForm(request.POST, request.FILES)

        if not form.is_valid():
            return JsonResponse({'error': form.errors}, status=400)

        try:
            create_video_service_factory().process_upload(
                video_id=object_id,
                chunk_index=form.cleaned_data['chunkIndex'],
                chunk=form.cleaned_data['chunk'].read()
            )
        except Video.DoesNotExist:
            return JsonResponse({'error': 'Video not found.'}, status=404)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)

    def video_upload_finish_view(self, request: HttpRequest, object_id: int):
        if request.method != 'POST':
            return JsonResponse({'error': 'Method not allowed'}, status=405)

        form = VideoChunkFinishUploadForm(request.POST)

        if not form.is_valid():
            return JsonResponse({'error': form.errors}, status=400)

        try:
            create_video_service_factory().finalize_upload(
                object_id, form.cleaned_data['totalChunks'])
        except Video.DoesNotExist:
            return JsonResponse({'error': 'Video not found'}, status=404)
        except (VideoMediaNotExistsException, VideoMediaInvalidStatusException, VideoChunkUploadException) as e:
            return JsonResponse({'error': str(e)}, status=400)

        self.message_user(
            request, 'Upload successful', messages.SUCCESS)

        return JsonResponse({}, status=204)


admin.site.register(Tag)
