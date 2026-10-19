from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Pekerja, Department, Division

@admin.register(Pekerja)
class PekerjaAdmin(admin.ModelAdmin):
    list_display = ('emp_code', 'emp_name', 'sex', 'division', 'company_begin')
    search_fields = ('emp_code', 'emp_name', 'id_card')
    list_filter = ('sex', 'division__department')
    
# Department dan Division ikut didaftarkan sebagai cadangan pengelolaan lewat /admin/.
admin.site.register(Department)
admin.site.register(Division)
    