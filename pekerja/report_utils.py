from django.db.models import Count
from .models import Pekerja

# menyaring pekerja sesuai pilihan: semua, per Department, atau per Division.
def filter_pekerja(mode, department=None, division=None):
    qs = Pekerja.objects.select_related('division__department')
    if mode == 'department' and department:
        qs = qs.filter(division__department=department)
    elif mode == 'division' and division:
        qs = qs.filter(division=division)
    return qs 

# membuat keterangan filter, misalnya “Department: Teknik”, untuk dicetak di report nanti.
def filter_label(mode, department=None, division=None):
    if mode == 'department' and department:
        return f'Department: {department.department_name}'
    if mode == 'division' and division:
        return f'Division : {division.division_name} ({
            division.department.department_name})'
    return 'Semua data'
    
# menghitung jumlah pekerja per Division, lalu mengelompokkannya per Department. values() menentukan kolom pengelompokan dan Count('id') menghitung barisnya.
def build_summary(qs):
    rows = (
        qs.values(
            'division__department__department_code',
            'division__department__department_name', 
            'division__division_code',
            'division__division_name'
        )
        .annotate(total=Count('id'))
        .order_by('division__department__department_code', 'division__division_code')
    )
    
    result = {}
    for r in rows:
        key = r['division__department__department_code']
        dept = result.setdefault(key, {
            'code': key,
            'name': r['division__department__department_name'],
            'total': 0,
            'divisions': [],
        })
        dept['divisions'].append({
            'code': r['division__division_code'],
            'name': r['division__division_name'],
            'total': r['total'],
        })
        dept['total'] += r['total']
        
    return list(result.values())

