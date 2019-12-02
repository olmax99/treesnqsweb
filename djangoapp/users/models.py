from django.db import models
from django.contrib.auth.models import User

# import PIL.Image


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f"{self.user.username} profile"

    # Only if media files are stored locally, otherwise handle in AWS Lambda
    # def save(self, *args, **kwargs):
    #     super(Profile, self).save(*args, **kwargs)
    #     img = PIL.Image.open(self.image.path)
    #     max_size_allowed = (300, 300)
    #     if img.width > max_size_allowed[0] or img.height > max_size_allowed[1]:
    #         # thumbnail calculates min(maxwidth/width, maxheight/height) by default
    #         img.thumbnail(max_size_allowed)
    #         img.save(self.image.path)
