from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class HourlyRateRole(models.Model):
    """ To store the hourly rate of different roles or specific employees """
    name = models.CharField(max_length=100, help_text="e.g., ຄູສອນທົ່ວໄປ (General Teacher)")
    rate_per_hour = models.DecimalField(max_digits=10, decimal_places=2, help_text="e.g., 90000 Kip")

    class Meta:
        verbose_name = "Hourly Rate Role (ຕຳແໜ່ງ/ອັດຕາຄ່າຈ້າງ)"
        verbose_name_plural = "Hourly Rate Roles (ຕຳແໜ່ງ/ອັດຕາຄ່າຈ້າງ)"

    def __str__(self):
        return self.name

class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.ForeignKey(HourlyRateRole, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Employee Profile (ປະຫວັດພະນັກງານ)"
        verbose_name_plural = "Employee Profiles (ປະຫວັດພະນັກງານ)"

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.phone_number})"


class Timesheet(models.Model):
    """
    ບັນທຶກວັນເຮັດວຽກ ແລະ ຊົ່ວໂມງ (1-31)
    """
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='timesheets')
    date = models.DateField(help_text="The exact date worked")
    hours_worked = models.DecimalField(max_digits=4, decimal_places=1, default=0.0, help_text="e.g., 2.0 or 3.0")
    remark = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Timesheet (ບັນທຶກຊົ່ວໂມງເຮັດວຽກ)"
        verbose_name_plural = "Timesheets (ບັນທຶກຊົ່ວໂມງເຮັດວຽກ)"
        unique_together = ['employee', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee.user.first_name} - {self.date} - {self.hours_worked} hrs"


class PayrollSummary(models.Model):
    """ 
    ລວມຈຳນວນເງິນ ແລະ ຊົ່ວໂມງປະຈຳເດືອນ 
    """
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='payrolls')
    month_year = models.CharField(max_length=7, help_text="MM/YYYY e.g., 11/2025")
    total_hours = models.DecimalField(max_digits=6, decimal_places=1, default=0.0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    is_paid = models.BooleanField(default=False)
    notes = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Payroll Summary (ສະຫຼຸບເງິນເດືອນ)"
        verbose_name_plural = "Payroll Summaries (ສະຫຼຸບເງິນເດືອນ)"

    def __str__(self):
        return f"{self.employee} - {self.month_year} - {self.total_amount:,} Kip"
