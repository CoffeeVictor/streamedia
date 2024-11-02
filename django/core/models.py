from django.db import models

# Create your models here.


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Name')

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self) -> str:
        return self.name


class Media(models.Model):

    class Status(models.TextChoices):
        UPLOAD_STARTED = 'UPLOAD_STARTED', 'Upload Started'
        PROCESSING_STARTED = 'PROCESSING_STARTED', 'Processing Started'
        PROCESSING_FINISHED = 'UPLOAD_FINISHED', 'Processing Finished'
        PROCESSING_ERROR = 'UPLOAD_ERROR', 'Processing Error'

    status = models.CharField(max_length=20, verbose_name='Status',
                              choices=Status.choices, default=Status.UPLOAD_STARTED)

    class Meta:
        abstract = True


class Video(models.Model):
    title = models.CharField(verbose_name='Title', max_length=255)
    description = models.TextField(verbose_name='Description')
    thumbnail = models.ImageField(
        verbose_name='Thumbnail', upload_to='thumbnails/')
    slug = models.SlugField(unique=True)
    published_at = models.DateTimeField(
        verbose_name='Published at', null=True, editable=False)
    is_published = models.BooleanField(verbose_name='Published', default=False)
    num_likes = models.IntegerField(
        verbose_name='Likes', default=0, editable=False)
    num_views = models.IntegerField(
        verbose_name='Views', default=0, editable=False)
    tags = models.ManyToManyField(
        Tag, verbose_name='Tags', related_name='videos', blank=True)

    class Meta:
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'

    def __str__(self) -> str:
        return self.title


class VideoMedia(Media):
    path = models.CharField(max_length=255, verbose_name='Video Path')
    video = models.OneToOneField(
        Video, on_delete=models.PROTECT, verbose_name='Media', related_name='video_media')
