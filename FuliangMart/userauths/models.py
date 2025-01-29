from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length = 100)
    bio = models.CharField(max_length = 100)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
	
    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="image", null = True, blank=True)
    full_name = models.CharField(max_length=100, null = True, blank=True)
    bio = models.CharField(max_length=100, null = True, blank=True)
    phone = models.CharField(max_length=100, null = True, blank=True)
    address = models.CharField(max_length=100, null = True, blank=True)
    country = models.CharField(max_length=100, null = True, blank=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile of {self.user.username}, {self.user.first_name} {self.user}"


    # def __str__(self):
    #     return self.full_name
    #     # except:
    #     #     return self.user.username
        # return f"Profile of {self.user.username}"

class ContactUs(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150)
    phone = models.CharField(max_length = 50)
    subject = models.CharField(max_length = 200)
    message = models.TextField()


    class Meta:
        verbose_name_plural = "Contact Us"

    def __str__(self):
        return self.full_name
        
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)







