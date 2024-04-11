from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token

# User.objects.create_user(username="Dan", password="fithaboo123!")

@login_required
def index(request):
    user = request.user
    return render(request, 'timeclock/index.html', {'user': user})

@ensure_csrf_cookie
def update_db(request):
    if request.method == 'GET':
        return HttpResponse(get_token(request))
    if request.method == 'POST':
        print('sent')
        return request.body