from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    tree = models.CharField(max_length=54, default='Business')
    name = models.CharField(max_length=54, blank=True, null=True)
    organization = models.CharField(max_length=54, blank=True, null=True)
    # Indicates label in order to verify eligibility for discount in case of NonProfit or Member tree
    # Can be only changed by admin and will result in different pricing model
    verified = models.BooleanField(default=False)

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

