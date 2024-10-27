from django.db import models

# Create your models here.

class Tag(models.Model):
	name = models.CharField(max_length=50, unique=True, verbose_name='Nome')
	class Meta:
		verbose_name = 'Tag'
		verbose_name_plural = 'Tags'
    
	def __str__(self) -> str:
		return self.name

class Media(models.Model):
	class Meta:
		abstract = True


class Video(Media):
	title = models.CharField(verbose_name='Title', max_length=255)
	description = models.TextField(verbose_name='Description')
	thumbnail = models.ImageField(verbose_name='Thumbnail', upload_to='thumbnails/')
	slug = models.SlugField(unique=True)
	published_at = models.DateTimeField(verbose_name='Published at', null=True, editable=False)
	is_published = models.BooleanField(verbose_name='Published', default=False)
	num_likes = models.IntegerField(verbose_name='Likes', default=0, editable=False)
	num_views = models.IntegerField(verbose_name='Views', default=0, editable=False)
	tags = models.ManyToManyField(Tag, verbose_name='Tags', related_name='videos')

	class Meta:
		verbose_name = 'Video'
		verbose_name_plural = 'Videos'

	def __str__(self) -> str:
		return self.title
