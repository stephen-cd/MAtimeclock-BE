from django.db import models

class Employee(models.Model):
    pin = models.CharField(primary_key=True, max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    manager = models.BooleanField()

class Job(models.Model):
    job_id = models.CharField(primary_key=True, max_length=20)
    status = models.CharField(max_length=100)

class Hours(models.Model):
    date = models.CharField(max_length=10)
    start_time = models.CharField(max_length=10)
    end_time = models.CharField(max_length=10)
    pin = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='pin')
    job_id = models.ForeignKey(Job, on_delete=models.CASCADE, db_column='job_id')
