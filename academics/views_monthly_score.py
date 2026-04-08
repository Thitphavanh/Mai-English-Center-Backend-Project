"""
views/monthly_scores.py — ໜ້າສະຫຼຸບຄະແນນ Letter Grade ປະຈຳເດືອນ
"""
import json
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from academics.models import MonthlyScore, Enrollment, ClassSchedule
from academics.forms import MonthlyScoreBulkForm


MONTH_NAMES_LO = {
    1: 'ມັງກອນ', 2: 'ກຸມພາ', 3: 'ມີນາ',
    4: 'ເມສາ', 5: 'ພຶດສະພາ', 6: 'ມິຖຸນາ',
    7: 'ກໍລະກົດ', 8: 'ສິງຫາ', 9: 'ກັນຍາ',
    10: 'ຕຸລາ', 11: 'ພະຈິກ', 12: 'ທັນວາ',
}


def get_year_calendar(year):
    """Return a list of 12 months with their month string (MM/YYYY)."""
    return [
        {
            'num': m,
            'name_lo': MONTH_NAMES_LO[m],
            'name_en': datetime.date(year, m, 1).strftime('%b'),
            'month_str': f"{m:02d}/{year}",
        }
        for m in range(1, 13)
    ]


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        from django.urls import reverse
        if self.request.user.is_authenticated:
            return redirect('home:portal_dashboard')
        return redirect('backoffice:login')


class MonthlyScoreCalendarView(StaffRequiredMixin, View):
    """
    ປະຕິທິນ 12 ເດືອນ — ສະແດງສະຖານະການບັນທຶກຄະແນນ
    URL: /backoffice/monthly-scores/
    """
    template_name = 'backoffice/monthly_score_calendar.html'

    def get(self, request):
        today = datetime.date.today()
        year = int(request.GET.get('year', today.year))
        schedule_id = request.GET.get('schedule')

        schedules = ClassSchedule.objects.select_related('course').all()
        selected_schedule = None
        month_stats = {}

        if schedule_id:
            selected_schedule = get_object_or_404(ClassSchedule, pk=schedule_id)
            # For each month of the year, count how many students have scores
            enrollments = Enrollment.objects.filter(class_schedule=selected_schedule)
            total_students = enrollments.count()

            for m in range(1, 13):
                month_str = f"{m:02d}/{year}"
                scored = MonthlyScore.objects.filter(
                    enrollment__class_schedule=selected_schedule,
                    month=month_str
                )
                scored_count = scored.count()
                avg_total = None
                grade_dist = {}
                if scored_count:
                    from django.db.models import Avg
                    avg_total = scored.aggregate(avg=Avg('total_score'))['avg']
                    for ms in scored:
                        grade_dist[ms.letter_grade] = grade_dist.get(ms.letter_grade, 0) + 1

                month_stats[m] = {
                    'month_str': f"{m:02d}/{year}",
                    'total_students': total_students,
                    'scored_count': scored_count,
                    'is_complete': scored_count >= total_students and total_students > 0,
                    'avg_total': round(float(avg_total), 1) if avg_total else None,
                    'grade_dist': grade_dist,
                }

        calendar = get_year_calendar(year)

        return render(request, self.template_name, {
            'year': year,
            'prev_year': year - 1,
            'next_year': year + 1,
            'schedules': schedules,
            'selected_schedule': selected_schedule,
            'calendar': calendar,
            'month_stats': month_stats,
            'today': today,
        })


class MonthlyScoreBulkEntryView(StaffRequiredMixin, View):
    """
    ໜ້າ bulk-entry: ປ້ອນຄະແນນທຸກນັກຮຽນໃນຫ້ອງ/ເດືອນດຽວກັນ
    URL: /backoffice/monthly-scores/entry/
    """
    template_name = 'backoffice/monthly_score_entry.html'

    def _get_schedule_and_month(self, request_data):
        schedule_id = request_data.get('schedule')
        month_str = request_data.get('month')
        schedule = None
        if schedule_id:
            schedule = get_object_or_404(ClassSchedule, pk=schedule_id)
        return schedule, month_str

    def get(self, request):
        today = datetime.date.today()
        default_month = today.strftime('%m/%Y')
        schedules = ClassSchedule.objects.select_related('course').all()
        schedule_id = request.GET.get('schedule')
        month_str = request.GET.get('month', default_month)

        rows = []
        selected_schedule = None
        if schedule_id:
            selected_schedule = get_object_or_404(ClassSchedule, pk=schedule_id)
            enrollments = (
                Enrollment.objects
                .filter(class_schedule=selected_schedule)
                .select_related('student')
                .order_by('student__full_name')
            )
            existing_scores = {
                ms.enrollment_id: ms
                for ms in MonthlyScore.objects.filter(
                    enrollment__class_schedule=selected_schedule,
                    month=month_str
                )
            }
            
            # Auto-calculate attendance from DailyChecklist
            from academics.models import DailyChecklist
            try:
                m_part, y_part = month_str.split('/')
                month_int = int(m_part)
                year_int = int(y_part)
            except:
                month_int, year_int = today.month, today.year
            
            # Pre-fetch all checklist records for this schedule + month
            all_checklists = DailyChecklist.objects.filter(
                enrollment__class_schedule=selected_schedule,
                date__month=month_int,
                date__year=year_int
            )
            # Build lookup: {enrollment_id: [list of records]}
            checklist_map = {}
            for chk in all_checklists:
                checklist_map.setdefault(chk.enrollment_id, []).append(chk)
            
            for enr in enrollments:
                score_obj = existing_scores.get(enr.pk)
                
                # Calculate attendance from DailyChecklist
                chk_records = checklist_map.get(enr.pk, [])
                calc_attendance = None
                checklist_present = 0
                checklist_late = 0
                checklist_absent = 0
                checklist_total = len(chk_records)
                
                if chk_records:
                    course_type = selected_schedule.course.class_type
                    hours_per_session = 2 if course_type == 'WN' else 1
                    
                    attended_hours = 0
                    for chk in chk_records:
                        if chk.status == 'P':
                            attended_hours += hours_per_session
                            checklist_present += 1
                        elif chk.status == 'L':
                            attended_hours += (hours_per_session * 0.5)
                            checklist_late += 1
                        elif chk.status == 'A':
                            checklist_absent += 1
                    
                    expected_hours = selected_schedule.total_hours_per_month
                    if expected_hours > 0:
                        calc_attendance = round((attended_hours / float(expected_hours)) * 20, 2)
                        if calc_attendance > 20:
                            calc_attendance = 20.0
                
                # Use calculated attendance if available, otherwise use existing score
                display_attendance = calc_attendance
                if display_attendance is None and score_obj:
                    display_attendance = score_obj.attendance
                
                rows.append({
                    'enrollment': enr,
                    'score': score_obj,
                    'monthly_test': score_obj.monthly_test if score_obj else '',
                    'exercise': score_obj.exercise if score_obj else '',
                    'attendance': display_attendance if display_attendance is not None else '',
                    'attendance_auto': calc_attendance is not None,
                    'checklist_present': checklist_present,
                    'checklist_late': checklist_late,
                    'checklist_absent': checklist_absent,
                    'checklist_total': checklist_total,
                    'engagement': score_obj.engagement if score_obj else '',
                    'remark': score_obj.remark if score_obj else '',
                    'letter_grade': score_obj.letter_grade if score_obj else '',
                    'total_score': score_obj.total_score if score_obj else '',
                })

        return render(request, self.template_name, {
            'schedules': schedules,
            'selected_schedule': selected_schedule,
            'month_str': month_str,
            'rows': rows,
            'today': today,
        })

    @transaction.atomic
    def post(self, request):
        schedule_id = request.POST.get('schedule_id')
        month_str = request.POST.get('month_str')
        schedule = get_object_or_404(ClassSchedule, pk=schedule_id)

        enrollment_ids = request.POST.getlist('enrollment_id')
        saved = 0
        for enr_id in enrollment_ids:
            enr_id = int(enr_id)
            monthly_test = request.POST.get(f'monthly_test_{enr_id}') or None
            exercise = request.POST.get(f'exercise_{enr_id}') or None
            attendance = request.POST.get(f'attendance_{enr_id}') or None
            engagement = request.POST.get(f'engagement_{enr_id}') or None
            remark = request.POST.get(f'remark_{enr_id}', '')

            # Skip rows that have no data at all
            if all(v is None for v in [monthly_test, exercise, attendance, engagement]):
                continue

            enr = get_object_or_404(Enrollment, pk=enr_id)
            obj, _ = MonthlyScore.objects.update_or_create(
                enrollment=enr,
                month=month_str,
                defaults={
                    'monthly_test': monthly_test,
                    'exercise': exercise,
                    'attendance': attendance,
                    'engagement': engagement,
                    'remark': remark,
                    'evaluator': request.user,
                }
            )
            saved += 1

        messages.success(request, f"✅ ບັນທຶກແລ້ວ {saved} ນັກຮຽນ ສຳລັບ {month_str}")
        return redirect(
            f"{request.path}?schedule={schedule_id}&month={month_str}"
        )


class MonthlyScoreDetailView(StaffRequiredMixin, View):
    """
    ສະແດງຕາຕະລາງຄະແນນທຸກໆນັກຮຽນ ສຳລັບ 1 ຫ້ອງ 1 ເດືອນ
    URL: /backoffice/monthly-scores/detail/
    """
    template_name = 'backoffice/monthly_score_detail.html'

    def get(self, request):
        schedule_id = request.GET.get('schedule')
        month_str = request.GET.get('month')
        schedules = ClassSchedule.objects.select_related('course').all()
        selected_schedule = None
        scores = []
        grade_summary = {}

        if schedule_id and month_str:
            selected_schedule = get_object_or_404(ClassSchedule, pk=schedule_id)
            qs = (
                MonthlyScore.objects
                .filter(enrollment__class_schedule=selected_schedule, month=month_str)
                .select_related('enrollment__student')
                .order_by('-total_score')
            )
            scores = list(qs)
            for s in scores:
                g = s.letter_grade or 'F'
                grade_summary[g] = grade_summary.get(g, 0) + 1

        return render(request, self.template_name, {
            'schedules': schedules,
            'selected_schedule': selected_schedule,
            'month_str': month_str,
            'scores': scores,
            'grade_summary': json.dumps(grade_summary),
            'grade_summary_dict': grade_summary,
        })
