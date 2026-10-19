from django import forms 
from .models import Pekerja, Department, Division

class PekerjaForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        label='Department',
        empty_label='-- Pilih Department --',
    )

    field_order = [
        'emp_code', 'emp_name', 'id_card', 'sex',
        'birth_place', 'birth_date', 'company_begin',
        'department', 'division',
    ]

    class Meta:
        model = Pekerja
        fields = [
            'emp_code', 'emp_name', 'id_card', 'sex',
            'birth_place', 'birth_date', 'company_begin',
            'division',
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'company_begin': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'

        division_field = self.fields['division']
        division_field.empty_label = '-- Pilih Division --'
        division_field.queryset = Division.objects.none()

        if self.is_bound:
            dept_pk = self.data.get('department')
            if dept_pk and str(dept_pk).isdigit():
                division_field.queryset = Division.objects.filter(department__pk=dept_pk)
        elif self.instance.pk:
            dept = self.instance.division.department
            self.initial['department'] = dept.pk
            division_field.queryset = Division.objects.filter(department=dept)

    def clean(self):
        cleaned = super().clean()
        dept = cleaned.get('department')
        div = cleaned.get('division')
        if dept and div and div.department_id != dept.department_code:
            self.add_error('division', 'Division tidak sesuai dengan Department yang dipilih.')
        return cleaned

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['department_code', 'department_name']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            
class DivisionForm(forms.ModelForm):
    class Meta:
        model = Division
        fields = ['department', 'division_code', 'division_name']
        
        def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                for field in self.fields.values():
                    field.widget.attrs['class'] = 'form-select'
                else:
                    field.widget.attrs['class'] = 'form-control'
                    
class ReportFilterForm(forms.Form):
    MODE_CHOICES = [
        ('all', 'Semua Data'),
        ('department', 'Berdasarkan Department'),
        ('division', 'Berdasarkan Division'),
    ]
    
    mode  = forms.ChoiceField(
        choices=MODE_CHOICES,
        initial='all',
        widget=forms.RadioSelect,
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label='-- Pilih Department --',
    )
    division = forms.ModelChoiceField(
        queryset=Division.objects.none(),
        required=False,
        empty_label='-- Pilih Division --',
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mode'].widget.attrs['class'] = 'form-check-input'
        self.fields['department'].widget.attrs['class'] = 'form-select'
        self.fields['division'].widget.attrs['class'] = 'form-select'

        if self.is_bound:
            dept_pk = self.data.get('department')
            if dept_pk and str(dept_pk).isdigit():
                self.fields['division'].queryset = Division.objects.filter(department__pk=dept_pk)

    def clean(self):
        cleaned = super().clean()
        mode = cleaned.get('mode')
        dept = cleaned.get('department')
        div = cleaned.get('division')

        if mode == 'department' and not dept:
            self.add_error('department', 'Pilih Department terlebih dahulu.')

        if mode == 'division':
            if not dept:
                self.add_error('department', 'Pilih Department terlebih dahulu.')
            if not div:
                self.add_error('division', 'Pilih Division terlebih dahulu.')
            if dept and div and div.department_id != dept.department_code:
                self.add_error('division', 'Division tidak sesuai dengan Department yang dipilih.')

        return cleaned    