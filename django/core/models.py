from django.db import models

# Create your models here.

class Tag(models.Model):
	name = models.CharField(max_length=50, unique=True, verbose_name='Nome')
	class Meta:
		verbose_name = 'Tag'
		verbose_name_plural = 'Tags'
    
	def __str__(self) -> str:
		return self.name
