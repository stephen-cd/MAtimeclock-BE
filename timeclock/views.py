import json
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.db import transaction
import datetime

from timeclock.models import Employee, Hours, Job

# User.objects.create_user(username="Dan", password="fithaboo123!")

@login_required
def index(request):
    user = request.user
    dates = list(set(Hours.objects.all().values_list('date', flat=True)))
    dates = [datetime.datetime.strptime(date, '%Y-%m-%d').date() for date in dates]
    min_date = str(min(dates))
    max_date = str(max(dates))
    context = {
        'user': user,
        'min_date': min_date,
        'max_date': max_date,
    }

    if request.method == 'GET':
        start_date = request.GET.get('start-date')
        end_date = request.GET.get('end-date')
        hours = Hours.objects.filter(date__range=(start_date, end_date))
        context['start_date'] = start_date
        context['end_date'] = end_date
        context['hours'] = hours

    return render(request, 'timeclock/index.html', context)

@ensure_csrf_cookie
def update_db(request):
    if request.method == 'GET':
        token = get_token(request)
        return HttpResponse(token, headers={'Set-Cookie': f'csrftoken={token}; SameSite=None; Secure'})
    if request.method == 'POST':
        data = json.loads(request.body)
        with transaction.atomic():
            Employee.objects.all().delete()
            Job.objects.all().delete()
            Hours.objects.all().delete()
            employees = [Employee(pin=employee['pin'], first_name=employee['first_name'], last_name=employee['last_name'], manager=employee['manager']) for employee in data[0]]
            Employee.objects.bulk_create(employees)
            jobs = [Job(job_id=job['job_id'], status=job['status']) for job in data[1]]
            Job.objects.bulk_create(jobs)
            hours = [Hours(id=hrs['id'], date=hrs['date'], start_time=hrs['start_time'], end_time=hrs['end_time'], pin=Employee.objects.get(pin=hrs['pin']), job_id=Job.objects.get(job_id=hrs['job_id'])) for hrs in data[2]]
            Hours.objects.bulk_create(hours)
            print(Employee.objects.all())
            print(Job.objects.all())
            print(Hours.objects.all())
            return HttpResponse('OK')