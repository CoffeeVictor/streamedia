from django import forms

MAX_VIDEO_CHUNK_SIZE = 1 * 1024 * 1024  # 1 Mb


class VideoChunkUploadForm(forms.Form):
    chunk = forms.FileField(required=True)
    chunkIndex = forms.IntegerField(required=True, min_value=0)

    def clean_chunk(self):
        chunk = self.cleaned_data.get('chunk')

        if chunk.size > MAX_VIDEO_CHUNK_SIZE:
            raise forms.ValidationError('Chunk exceeds than max size of 1 MB')

        return chunk


class VideoChunkFinishUploadForm(forms.Form):
    filename = forms.CharField(max_length=255, required=True)
    totalChunks = forms.IntegerField(min_value=1, required=True)
