import json
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.db import transaction
from datetime import datetime, date
from timeclock.models import Employee, Hours, Job
from django.db.models import Q

def timedelta_to_hours_minutes(td):
    if isinstance(td, str):
        return td

    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours}:{minutes:02}"

@login_required
def index(request):
    user = request.user
    dates = list(set(Hours.objects.all().values_list('date', flat=True)))
    dates = [datetime.strptime(date, '%Y-%m-%d').date() for date in dates]
    min_date = str(min(dates))
    max_date = str(max(dates))
    last_updated = open('last-updated.txt').read()
    start_date = request.GET.get('start-date')
    end_date = request.GET.get('end-date')
    context = {
        'user': user,
        'min_date': min_date,
        'max_date': max_date,
        'last_updated': last_updated,
        'invalid_date_range': False,
        'start_date': start_date,
        'end_date': end_date,
    }

    if request.method == 'GET' and start_date and end_date:
        start_date = request.GET.get('start-date')
        end_date = request.GET.get('end-date')

        if datetime.strptime(start_date, '%Y-%m-%d').date() > datetime.strptime(end_date, '%Y-%m-%d').date():
            context['invalid_date_range'] = True
        
        hours = Hours.objects.select_related('job_id', 'pin').filter(date__range=(start_date, end_date)).order_by('pin__last_name')
        employees = {hrs.pin.pin: f'{hrs.pin.first_name} {hrs.pin.last_name}' for hrs in hours}
        employees = list(employees.values())
        jobs = list(set([hrs.job_id.job_id for hrs in hours]))
        
        job_dict = {hrs.job_id.job_id: {employee: '0:00' for employee in employees} for hrs in hours}
        for job_id, employees_and_hours in job_dict.items():
            employees_and_hours['total'] = '0:00'

        employee_dict = {f'{hrs.pin.first_name} {hrs.pin.last_name}': {job: '0:00' for job in jobs} for hrs in hours}
        for employee, job_and_hours in employee_dict.items():
            job_and_hours['total'] = '0:00'

        for hrs in hours:
            job_id = hrs.job_id.job_id
            first_name = hrs.pin.first_name
            last_name = hrs.pin.last_name
            if not hrs.end_time:
                continue
            start_time = datetime.strptime(hrs.start_time, '%H:%M').time()
            end_time = datetime.strptime(hrs.end_time, '%H:%M').time()
            hours_for_session = datetime.combine(date.min, end_time) - datetime.combine(date.min, start_time)

            if job_dict[job_id][f'{first_name} {last_name}'] == '0:00':
                job_dict[job_id][f'{first_name} {last_name}'] = hours_for_session
            else:
                job_dict[job_id][f'{first_name} {last_name}'] = job_dict[job_id][f'{first_name} {last_name}'] + hours_for_session
            
            if job_dict[job_id]['total'] == '0:00':
                job_dict[job_id]['total'] = hours_for_session
            else:
                job_dict[job_id]['total'] = job_dict[job_id]['total'] + hours_for_session
                
            
            if employee_dict[f'{first_name} {last_name}'][job_id] == '0:00':
                employee_dict[f'{first_name} {last_name}'][job_id] = hours_for_session
            else:
                employee_dict[f'{first_name} {last_name}'][job_id] = employee_dict[f'{first_name} {last_name}'][job_id] + hours_for_session
            
            if employee_dict[f'{first_name} {last_name}']['total'] == '0:00':
                employee_dict[f'{first_name} {last_name}']['total'] = hours_for_session
            else:
                employee_dict[f'{first_name} {last_name}']['total'] = employee_dict[f'{first_name} {last_name}']['total'] + hours_for_session
        
        employees = list(employee_dict.keys())
        employees.append('Total')

        jobs = list(job_dict.keys())
        jobs.append('Total')

        for job_id, employees_and_hours in job_dict.items():
            for employee, hours in employees_and_hours.items():
                #job_dict[job_id][employee] = str(hours)[:-3]
                job_dict[job_id][employee] = str(timedelta_to_hours_minutes(hours))


        for name, jobs_and_hours in employee_dict.items():
            for job, hours in jobs_and_hours.items():
                #employee_dict[name][job] = str(hours)[:-3]
                employee_dict[name][job] = str(timedelta_to_hours_minutes(hours))

        context['start_date'] = start_date
        context['end_date'] = end_date
        context['hours'] = hours
        context['job_dict'] = job_dict
        context['employee_dict'] = employee_dict
        context['employees'] = employees
        context['jobs'] = jobs

    return render(request, 'timeclock/index.html', context)

def dump(db, new_employees, new_jobs, new_hours=None, new_hours_data=None):
    current_emps = Employee.objects.using(db).all().values_list('pin', flat=True)
    current_jobs = Job.objects.using(db).all().values_list('job_id', flat=True)
    current_hours = Hours.objects.using(db).all().values_list('id', flat=True)
    new_employee_pins = [employee.pin for employee in new_employees]
    new_job_ids = [job.job_id for job in new_jobs]
    employees_to_delete = [employee for employee in Employee.objects.using(db).all() if employee.pin not in new_employee_pins]
    jobs_to_delete = [job for job in Job.objects.using(db).all() if job.job_id not in new_job_ids]
    if new_hours:
        new_hours_ids = [hrs.id for hrs in new_hours]

    Employee.objects.using(db).bulk_update([employee for employee in new_employees if employee.pin in current_emps], ['first_name', 'last_name', 'manager'])
    Employee.objects.using(db).bulk_create([employee for employee in new_employees if employee.pin not in current_emps])
    Job.objects.using(db).bulk_update([job for job in new_jobs if job.job_id in current_jobs], ['status'])
    Job.objects.using(db).bulk_create([job for job in new_jobs if job.job_id not in current_jobs])
    
    if new_hours_data:
        new_hours = [Hours(id=hrs['id'], date=hrs['date'], start_time=hrs['start_time'], end_time=hrs['end_time'], pin=Employee.objects.using(db).get(pin=hrs['pin']), job_id=Job.objects.using(db).get(job_id=hrs['job_id'])) for hrs in new_hours_data]
        new_hours_ids = [hrs.id for hrs in new_hours]
    
    Hours.objects.using(db).bulk_update([hours for hours in new_hours if hours.id in current_hours], ['start_time', 'end_time', 'pin', 'job_id'])
    Hours.objects.using(db).bulk_create([hours for hours in new_hours if hours.id not in current_hours])

    for employee in employees_to_delete:
        employee.delete()
    for job in jobs_to_delete:
        job.delete()

    hours_to_delete = [hrs for hrs in Hours.objects.using(db).all() if hrs.id not in new_hours_ids]
    for hours in hours_to_delete:
        hours.delete()

@csrf_exempt
def update_db(request):
    if request.method == 'GET':
        token = get_token(request)
        return HttpResponse(token, headers={'Set-Cookie': f'csrftoken={token}; SameSite=None; Secure'})
    if request.method == 'POST':
        data = json.loads(request.body)
        with transaction.atomic():
            # Take all the data from the current main db and update the backup db with it
            current_main_emps = Employee.objects.using('default').all()
            current_main_jobs = Job.objects.using('default').all()
            current_main_hours = Hours.objects.using('default').all()
            dump('backup', current_main_emps, current_main_jobs, current_main_hours)

            employees_from_fe = [Employee(pin=employee['pin'], first_name=employee['first_name'], last_name=employee['last_name'], manager=employee['manager']) for employee in data[0]]
            jobs_from_fe = [Job(job_id=job['job_id'], status=job['status']) for job in data[1]]
            dump('default', employees_from_fe, jobs_from_fe, new_hours_data=data[2])

            last_updated = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
            file = open('last-updated.txt', 'w')
            file.write(last_updated)
            file.close()

            return HttpResponse('OK')
