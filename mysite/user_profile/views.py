from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from . models import Profile


@login_required
def profile(request):
    return render(request, 'user_profile/profile.html')
