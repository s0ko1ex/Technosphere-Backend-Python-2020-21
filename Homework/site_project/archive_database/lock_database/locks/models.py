from django.db import models

# Create your models here.
class Lock(models.Model):
    name = models.CharField("Lock name", max_length=32, null=False)
    company = models.CharField("Lock company", max_length=32, null=True)
    model = models.CharField("Lock model", max_length=32, null=True)
    lock_type = models.CharField("Lock type", max_length=32, null=True)
    core = models.CharField("Core type", max_length=32, null=True)
    description = models.TextField("Lock description", null=True)
    image = models.FilePathField(path="/img")