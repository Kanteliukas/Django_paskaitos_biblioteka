from django.db import models
from django.utils.translation import gettext_lazy as _
# pirmas variantas - kaip kurso medžiagoje - blogai
# from django.contrib.auth.models import User
# antras variantas - kaip reikėtų daryti
from django.contrib.auth import get_user_model
# trečias variantas
# from django.conf import settings
# print(settings.AUTH_USER_MODEL)


class Profile(models.Model):
    user = models.OneToOneField(
        get_user_model(), 
        verbose_name=_("user"), 
        on_delete=models.CASCADE,
        related_name="profile",
    )
    picture = models.ImageField(
        _("picture"),
        upload_to='user_profile/img/',
        default='user_profile/img/default.png'
    )

    def __str__(self):
        return f'{str(self.user)} {_("profile")}'

    class Meta:
        verbose_name = _("user profile")
        verbose_name_plural = _("user profiles")

