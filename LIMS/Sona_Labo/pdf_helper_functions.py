from .models import Client, Sample, Result, Report
from django.http import HttpResponse
from fpdf import FPDF
import datetime

def _generate_pdf_response(form, queryset):
    reports = form.cleaned_data['report']
    report_date = form.cleaned_data['report_date']
    start_time = form.cleaned_data['start_time']
    end_time = form.cleaned_data['end_time']

    start_datetime = datetime.datetime.combine(report_date, start_time)
    end_datetime = datetime.datetime.combine(report_date, end_time)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=11)

    for report in reports:
        samples_type = report.sample_type.all().order_by('nameST')
        analyses = report.analyse.all()
        orientation = 'L' if len(samples_type) > 8 else 'P'

        for client in queryset:
            pdf.add_page(orientation=orientation)
            _add_client_report_page(
                pdf, client, report, report_date, start_datetime, end_datetime, samples_type, analyses
            )

    response = HttpResponse(pdf.output('clients_reports.pdf', 'S').encode('latin-1'), content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="clients_reports.pdf"'
    return response


def _add_client_report_page(pdf, client, report, report_date, start_datetime, end_datetime, samples_type, analyses):
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, report.name, ln=True, align='C')
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 10, client.nameC, ln=True, align='C')
    pdf.set_left_margin(5)
    pdf.set_x(5)

    # Header (Date and Time)
    left_text = f"Date: {report_date.strftime('%Y-%m-%d')}"
    right_text = f"Time: {start_datetime.strftime('%H:%M')}"
    left_width = pdf.get_string_width(left_text)
    right_width = pdf.get_string_width(right_text)
    pdf.set_x(pdf.l_margin)
    pdf.cell(left_width, 10, left_text, border=0)
    pdf.set_x(pdf.w - pdf.r_margin - right_width)
    pdf.cell(right_width, 10, right_text, border=0)
    pdf.ln(10)

    client_samples = Sample.objects.filter(
        client=client.id,
        date__range=(start_datetime, end_datetime),
        sample_type__in=samples_type
    )
    sample_map = {sample.sample_type_id: sample for sample in client_samples}
    client_results = Result.objects.filter(sample__in=client_samples, analyse__in=analyses)

    # --- Dynamic table layout ---
    total_columns = len(samples_type)
    usable_width = pdf.w - pdf.l_margin - pdf.r_margin
    first_col_width = 50
    column_width = (usable_width - first_col_width) / total_columns
    line_height = 8
    max_y = pdf.h - pdf.b_margin

    # Adjust font size based on column count
    if total_columns > 22:
        font_size = 5
    elif total_columns > 16:
        font_size = 6
    elif total_columns > 10:
        font_size = 7
    else:
        font_size = 8

    # Header
    pdf.set_font("Helvetica", 'B', font_size)
    pdf.cell(first_col_width, line_height * 2, "Analysis / Samples", 1, align='C')

    for sample_type in samples_type:
     name = str(sample_type.nameST)
     max_text_width = column_width - 2  # 1pt padding each side
     while pdf.get_string_width(name) > max_text_width:
        name = name[:-1]
        if len(name) <= 3:
            break
     if len(name) < len(sample_type.nameST):
        name = name[:-3] + "..."
     pdf.cell(column_width, line_height * 2, name, 1, align='C')


    pdf.ln()

    # Table rows
    pdf.set_font("Helvetica", size=font_size)
    for analyse in analyses:
        # Page break check
        if pdf.get_y() + line_height > max_y:
            pdf.add_page()
            # Redraw header
            pdf.set_font("Helvetica", 'B', font_size)
            pdf.cell(first_col_width, line_height * 2, "Analysis / Samples", 1, align='C')
            for sample_type in samples_type:
                name = str(sample_type.nameST)
                name = name if len(name) <= 15 else name[:12] + "..."
                pdf.cell(column_width, line_height * 2, name, 1, align='C')
            pdf.ln()
            pdf.set_font("Helvetica", size=font_size)

        a_name = str(analyse.Nameanl)
        a_name = a_name if len(a_name) <= 30 else a_name[:27] + "..."
        pdf.cell(first_col_width, line_height, a_name, 1)

        for sample_type in samples_type:
            sample = sample_map.get(sample_type.id)
            result = client_results.filter(analyse=analyse, sample=sample).first() if sample else None
            value = f"{result.value:.3f}" if result else "-"
            pdf.cell(column_width, line_height, value, 1, align='C')
        pdf.ln()

    pdf.ln(5)

    # Footer
    page_width = pdf.w - pdf.l_margin - pdf.r_margin
    col_width = page_width / 3

    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", size=font_size + 1)
    pdf.cell(col_width, 10, "Analyzer:", border=0)
    pdf.cell(col_width, 10, "Checker:", border=0)
    pdf.cell(col_width, 10, "Monitor:", border=0)
    pdf.ln(10)
