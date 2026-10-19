from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Q, ProtectedError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from .report_excel import build_workbook
from .report_pdf import build_pdf


from .forms import PekerjaForm, DepartmentForm, DivisionForm, ReportFilterForm
from .models import Pekerja, Department, Division
from .report_utils import filter_pekerja, filter_label, build_summary

@login_required
def home(request):
    return render(request, 'pekerja/home.html')

@login_required
def kebun(request):
    return render(request, 'pekerja/kebun.html')

# View Pekerja
@login_required
@permission_required('pekerja.view_pekerja', raise_exception=True)
def pekerja_list(request):
    # request.GET.get('q') mengambil kata kunci dari URL, misalnya /?q=budi.
    q = request.GET.get('q', '').strip()
    
    pekerja = Pekerja.objects.select_related('division__department')
    if q:
        # Q(...) | Q(...) berarti ATAU: data cocok jika salah satu kolom mengandung kata kunci. icontains tidak membedakan huruf besar dan kecil.
        pekerja = pekerja.filter(
            Q(emp_code__icontains=q) |
            Q(emp_name__icontains=q) |
            # Q(id_card__icontains=q) |
            Q(division__division_name__icontains=q) |
            Q(division__department__department_name__icontains=q)
        )
    
    # Paginator(pekerja, 10) membagi data menjadi halaman berisi 10 baris.
    paginator = Paginator(pekerja, 10)
    # get_page(...) mengambil halaman sesuai ?page=2 di URL.
    page_obj = paginator.get_page(request.GET.get('page'))
    
    # Template menerima page_obj (data satu halaman),
    return render (request, 'pekerja/pekerja_list.html', {
        'page_obj': page_obj,
        'q': q,
    })

# Create Pekerja
@login_required
@permission_required('pekerja.add_pekerja', raise_exception=True)
def pekerja_create(request):
    if request.method == 'POST':
        form = PekerjaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data pekerja berhasil ditambahkan.')
            return redirect('pekerja:list')
    else:
        form = PekerjaForm()
    return render(request, 'pekerja/pekerja_form.html', {'form': form, 'judul': 'Tambah Pekerja'})

# Update Pekerja
@login_required
@permission_required('pekerja.change_pekerja', raise_exception=True)
def pekerja_update(request, pk):
    obj = get_object_or_404(Pekerja, pk=pk)
    if request.method == 'POST':
        form = PekerjaForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data pekerja berhasil diperbarui')
            return redirect('pekerja:list')
    else:
        form = PekerjaForm(instance=obj)
    return render(request, 'pekerja/pekerja_form.html', {'form':form, 'judul': 'Edit Pekerja'})

# Delete Pekerja
@login_required
@permission_required('pekerja.delete_pekerja', raise_exception=True)
def pekerja_delete(request, pk):
    obj = get_object_or_404(Pekerja, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Data Pekerja berhasil dihapus')
        return redirect('pekerja:list')
    return render(request, 'pekerja/pekerja_confirm_delete.html', {'obj': obj})

# === Department === 
@login_required
@permission_required('pekerja.view_department', raise_exception=True)
def department_list(request):
    return render(request, 'pekerja/department_list.html', {
        'items': Department.objects.all(),
    })


@login_required
@permission_required('pekerja.add_department', raise_exception=True)
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department berhasil ditambahkan.')
            return redirect('pekerja:department_list')
    else:
        form = DepartmentForm()
    return render(request, 'pekerja/master_form.html', {
        'form': form, 'judul': 'Tambah Department', 'kembali': 'pekerja:department_list',
    })


@login_required
@permission_required('pekerja.change_department', raise_exception=True)
def department_update(request, pk):
    obj = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department berhasil diperbarui.')
            return redirect('pekerja:department_list')
    else:
        form = DepartmentForm(instance=obj)
    return render(request, 'pekerja/master_form.html', {
        'form': form, 'judul': 'Edit Department', 'kembali': 'pekerja:department_list',
    })


@login_required
@permission_required('pekerja.delete_department', raise_exception=True)
def department_delete(request, pk):
    obj = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        try:
            obj.delete()
            messages.success(request, 'Department berhasil dihapus.')
        except ProtectedError:
            messages.error(request, 'Department tidak bisa dihapus karena masih memiliki Division.')
        return redirect('pekerja:department_list')
    return render(request, 'pekerja/master_confirm_delete.html', {
        'obj': obj, 'judul': 'Hapus Department', 'kembali': 'pekerja:department_list',
    })

# === Division ===
@login_required
@permission_required('pekerja.view_division', raise_exception=True)
def division_list(request):
    return render(request, 'pekerja/division_list.html', {
        'items': Division.objects.select_related('department'),
    })


@login_required
@permission_required('pekerja.add_division', raise_exception=True)
def division_create(request):
    if request.method == 'POST':
        form = DivisionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Division berhasil ditambahkan.')
            return redirect('pekerja:division_list')
    else:
        form = DivisionForm()
    return render(request, 'pekerja/master_form.html', {
        'form': form, 'judul': 'Tambah Division', 'kembali': 'pekerja:division_list',
    })


@login_required
@permission_required('pekerja.change_division', raise_exception=True)
def division_update(request, pk):
    obj = get_object_or_404(Division, pk=pk)
    if request.method == 'POST':
        form = DivisionForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Division berhasil diperbarui.')
            return redirect('pekerja:division_list')
    else:
        form = DivisionForm(instance=obj)
    return render(request, 'pekerja/master_form.html', {
        'form': form, 'judul': 'Edit Division', 'kembali': 'pekerja:division_list',
    })


@login_required
@permission_required('pekerja.delete_division', raise_exception=True)
def division_delete(request, pk):
    obj = get_object_or_404(Division, pk=pk)
    if request.method == 'POST':
        try:
            obj.delete()
            messages.success(request, 'Division berhasil dihapus.')
        except ProtectedError:
            messages.error(request, 'Division tidak bisa dihapus karena masih dipakai.')
        return redirect('pekerja:division_list')
    return render(request, 'pekerja/master_confirm_delete.html', {
        'obj': obj, 'judul': 'Hapus Division', 'kembali': 'pekerja:division_list',
    })
    
# Api kecil untuk Drowpdon bertingkat
@login_required
@permission_required('pekerja.view_pekerja', raise_exception=True)
def division_by_department(request):
    dept_id = request.GET.get('department', '')
    if not dept_id.isdigit():
        return JsonResponse([], safe=False)
    
    data = list(
        Division.objects.filter(department__pk=dept_id)
        .values('id', 'division_code', 'division_name')
    )
    return JsonResponse(data, safe=False)

# Report
@login_required
@permission_required('pekerja.export_pekerja', raise_exception=True)
def report_biodata(request):
    form = ReportFilterForm(request.GET or None)
    context = {'form': form, 'show_result': False}
    
    if form.is_bound and form.is_valid():
        cd = form.cleaned_data
        qs = filter_pekerja(cd['mode'], cd['department'], cd['division'])
        context.update({
            'show_result': True,
            'label': filter_label(cd['mode'], cd['department'], cd['division']),
            'total': qs.count(),
            'summary': build_summary(qs),
            'preview': qs[:10],
        })
    
    return render(request, 'pekerja/report.html', context)

# Report Excel
@login_required
@permission_required('pekerja.export_pekerja', raise_exception=True)
def report_excel(request):
    form = ReportFilterForm(request.GET or None)
    if not (form.is_bound and form.is_valid()):
        messages.error(request, 'Filter report tidak valid. Silakan pilih filter lalu klik Tampilkan.')
        return redirect('pekerja:report')

    cd = form.cleaned_data
    qs = filter_pekerja(cd['mode'], cd['department'], cd['division'])
    summary = build_summary(qs)
    label = filter_label(cd['mode'], cd['department'], cd['division'])

    wb = build_workbook(qs, summary, label, request.user.username)

    stamp = timezone.localtime().strftime('%Y%m%d_%H%M')
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="report_biodata_{stamp}.xlsx"'
    wb.save(response)
    return response

# Report PDF
@login_required
@permission_required('pekerja.export_pekerja', raise_exception=True)
def report_pdf(request):
    form = ReportFilterForm(request.GET or None)
    if not (form.is_bound and form.is_valid()):
        messages.error(request, 'Filter report tidak valid. Silakan pilih filter lalu klik Tampilkan.')
        return redirect('pekerja:report')

    cd = form.cleaned_data
    qs = filter_pekerja(cd['mode'], cd['department'], cd['division'])
    summary = build_summary(qs)
    label = filter_label(cd['mode'], cd['department'], cd['division'])

    stamp = timezone.localtime().strftime('%Y%m%d_%H%M')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_biodata_{stamp}.pdf"'
    build_pdf(response, qs, summary, label, request.user.username)
    return response