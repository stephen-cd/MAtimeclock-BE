import json
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.db import transaction
from datetime import datetime, date

from timeclock.models import Employee, Hours, Job

# User.objects.create_user(username="Dan", password="fithaboo123!")

@login_required
def index(request):
    user = request.user
    dates = list(set(Hours.objects.all().values_list('date', flat=True)))
    dates = [datetime.strptime(date, '%Y-%m-%d').date() for date in dates]
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
        hours = Hours.objects.select_related('job_id', 'pin').filter(date__range=(start_date, end_date))
        job_dict = {hrs.job_id.job_id: {} for hrs in hours}
        employee_dict = {f'{hrs.pin.first_name} {hrs.pin.last_name}': {} for hrs in hours}
        for hrs in hours:
            start_time = datetime.strptime(hrs.start_time, '%H:%M').time()
            end_time = datetime.strptime(hrs.end_time, '%H:%M').time()
            hours_for_session = datetime.combine(date.min, end_time) - datetime.combine(date.min, start_time)

            if not job_dict[hrs.job_id.job_id]:
                job_dict[hrs.job_id.job_id][f'{hrs.pin.first_name} {hrs.pin.last_name}'] = hours_for_session
                job_dict[hrs.job_id.job_id]['total'] = hours_for_session
            else:
                if not f'{hrs.pin.first_name} {hrs.pin.last_name}' in list(job_dict[hrs.job_id.job_id].keys()):
                    job_dict[hrs.job_id.job_id][f'{hrs.pin.first_name} {hrs.pin.last_name}'] = hours_for_session
                else:
                    job_dict[hrs.job_id.job_id][f'{hrs.pin.first_name} {hrs.pin.last_name}'] = job_dict[hrs.job_id.job_id][f'{hrs.pin.first_name} {hrs.pin.last_name}'] + hours_for_session
                job_dict[hrs.job_id.job_id]['total'] = job_dict[hrs.job_id.job_id]['total'] + hours_for_session
            
            if not employee_dict[f'{hrs.pin.first_name} {hrs.pin.last_name}']:
                employee_dict[f'{hrs.pin.first_name} {hrs.pin.last_name}'][hrs.job_id.job_id] = hours_for_session
                employee_dict[f'{hrs.pin.first_name} {hrs.pin.last_name}']['total'] = hours_for_session
            else:
                if not hrs.job_id.job_id in list(employee_dict[f'{hrs.pin.first_name} {hrs.pin.last_name}'].keys()):
                    employee_dict[f'{hrs.pin.first_name} {hrs.pin.last_name}'][hrs.job_id.job_id] = hours_for_session
                else:
                    employee_dict[f'{hrs.pin.first_name} {hrs.pin.last_name}'][hrs.job_id.job_id] = employee_dict[f'{hrs.pin.first_name} {hrs.pin.last_name}'][hrs.job_id.job_id] + hours_for_session  
                employee_dict[f'{hrs.pin.first_name} {hrs.pin.last_name}']['total'] = employee_dict[f'{hrs.pin.first_name} {hrs.pin.last_name}']['total'] + hours_for_session
        
        employees = list(employee_dict.keys())
        employees.append('Total')

        jobs = list(job_dict.keys())
        jobs.append('Total')

        for job_id, employees_and_hours in job_dict.items():
            for employee in employees:
                if employee != 'Total' and employee not in employees_and_hours.keys():
                    employees_and_hours[employee] = '0:00'
            employees_and_hours['total'] = employees_and_hours.pop('total')
            for employee, hours in employees_and_hours.items():
                job_dict[job_id][employee] = str(hours)[:-3]
        for name, jobs_and_hours in employee_dict.items():
            for job in jobs:
                if job != 'Total' and job not in jobs_and_hours.keys():
                    jobs_and_hours[job] = '0:00'
            jobs_and_hours['total'] = jobs_and_hours.pop('total')
            for job, hours in jobs_and_hours.items():
                employee_dict[name][job] = str(hours)[:-3]

        context['start_date'] = start_date
        context['end_date'] = end_date
        context['hours'] = hours
        context['job_dict'] = job_dict
        context['employee_dict'] = employee_dict
        context['employees'] = employees
        context['jobs'] = jobs

        print(job_dict)

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