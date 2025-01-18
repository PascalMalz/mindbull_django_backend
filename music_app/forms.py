from django import forms

class MusicUploadForm(forms.Form):
    music = forms.FileField(label='Select Music', help_text='Only audio files allowed.')
