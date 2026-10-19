from django.db import models

# Create your models here.

class Pekerja(models.Model):
    SEX_CHOICES = [
        ('M', "Male"),
        ('F', "Female"),
    ]
    
    emp_code = models.CharField('EMP Code', max_length=20, unique=True)
    emp_name = models.CharField('EMP Name', max_length=100)
    id_card = models.CharField('ID Card', max_length=20, unique=True)
    sex = models.CharField('Sex', max_length=1, choices=SEX_CHOICES)
    birth_place = models.CharField('Birth Place', max_length=100)
    birth_date = models.DateField('Birth Date')
    company_begin = models.DateField('Company Begin')
    division = models.ForeignKey(
        'Division',
        on_delete=models.PROTECT,
        related_name='pekerja',
        verbose_name='Division',
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['emp_code']
        verbose_name = 'Pekerja'
        verbose_name_plural = 'Pekerja'
        permissions = [
            ('export_pekerja', 'Can export Pekerja report'),
        ]
        
    def __str__(self):
        return f'{self.emp_code} - {self.emp_name}'
    
    @property
    def department(self):
        return self.division.department
    
class Department(models.Model):
    department_code = models.CharField('Department Code', max_length=10, unique=True)
    department_name = models.CharField('Department Name', max_length=100)
    
    class Meta:
        ordering = ['department_code']
    
    def __str__(self):
        return f'{self.department_code} - {self.department_name}'

class Division(models.Model):
    # Division terhubung ke Department lewat ForeignKey. to_field='department_code' dan db_column='department_code' membuat kolom di tabel division berisi kode department (T)
    # on_delete=models.PROTECT melarang penghapusan Department yang masih punya Division.
    
    department = models.ForeignKey(
        Department,
        to_field='department_code',
        db_column='department_code',
        on_delete=models.PROTECT,
        related_name='divisions',
        verbose_name='Department',
    )
    division_code = models.CharField('Division Code', max_length=10, unique=True)
    division_name = models.CharField('Division Name', max_length=100)
    
    class Meta:
        ordering = ['division_code']
        
    def __str__(self):
        return f'{self.division_code} - {self.division_name}'