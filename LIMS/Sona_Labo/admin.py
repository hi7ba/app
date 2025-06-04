from django.contrib import admin
from django.http import HttpResponse
from django import forms
from fpdf import FPDF
from django.shortcuts import render
#from django.conf import settings
import datetime
from django.utils.timezone import now
from .pdf_helper_functions import _generate_pdf_response
from django.urls import reverse
#from django.utils.html import format_html
from django.contrib.admin import AdminSite
from django.apps import apps


from .models import (Client, Category, SampleType, Lot,
                     StorageLocation, Shelf, Localisation, Sample, Manufacturer, Modele,
                     Equipment, Methodology, MethodologyRequirement, Analyse, Result, Report)






class ResultInline(admin.TabularInline):
    model = Result
    extra = 3
class SampleAdmin(admin.ModelAdmin):
    inlines = [ResultInline]


class PrintReportForm(forms.Form):
    report =forms.ModelMultipleChoiceField(
        queryset=Report.objects.all(),
        widget=forms.SelectMultiple(attrs={'size': 6}),
        label="Select Reports"
    )
  
    report_date = forms.DateField(initial=now().date,
        widget=forms.DateInput(attrs={'type': 'date'}), label="Date")
    start_time =  forms.TimeField(
        initial=now().time,
        widget=forms.TimeInput(attrs={'type': 'time'}),label="Start Time")
    end_time = forms.TimeField(initial=now().time,
        widget=forms.TimeInput(attrs={'type': 'time'}), label="End Time")



class ClientAdmin(admin.ModelAdmin):

    actions = ['print_pdf_report']

    def print_pdf_report(self, request, queryset):
        if 'apply' in request.POST:
            form = PrintReportForm(request.POST)
            if form.is_valid():
                return _generate_pdf_response(form, queryset)
        else:
            form = PrintReportForm(
                initial={'_selected_action': request.POST.getlist('_selected_action')})
            return render(request, 'admin/print_report_form.html', {
                'form': form,
                'queryset': queryset,
                'opts': self.model._meta,
                'title': 'Generate PDF report for selected clients'
            })

    print_pdf_report.short_description = "Print"





#Dashboard Admin
class CustomAdminSite(AdminSite):
    site_header = "LIMS"
    site_title = "LIMS"
    index_title = "Home"

    def each_context(self, request):
        context = super().each_context(request)
        app_list = self.get_app_list(request)
        context['app_list'] = app_list
        return context



custom_admin_site = CustomAdminSite(name="custom_admin")





custom_admin_site.register(Sample, SampleAdmin)
custom_admin_site.register(Result)
custom_admin_site.register(Analyse)
custom_admin_site.register(Localisation)
custom_admin_site.register(Client, ClientAdmin)
custom_admin_site.register(Category)
custom_admin_site.register(SampleType)
custom_admin_site.register(Lot)
custom_admin_site.register(StorageLocation)
custom_admin_site.register(Shelf)
custom_admin_site.register(Equipment)
custom_admin_site.register(Methodology)
custom_admin_site.register(MethodologyRequirement)
custom_admin_site.register(Modele)
custom_admin_site.register(Manufacturer)
custom_admin_site.register(Report)












