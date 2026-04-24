from django.db import models

class SchoolHistory(models.Model):
    title = models.CharField(max_length=255, default="ປະຫວັດຂອງໂຮງຮຽນ (History)")
    content = models.TextField()
    image = models.ImageField(upload_to='school_info/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "School History (ປະຫວັດໂຮງຮຽນ)"
        verbose_name_plural = "School History (ປະຫວັດໂຮງຮຽນ)"

    def __str__(self):
        return self.title

class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Announcement (ແຈ້ງການ)"
        verbose_name_plural = "Announcements (ແຈ້ງການ)"

    def __str__(self):
        return self.title

class NewsActivity(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='news_activities/')
    date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "News & Activity (ຂ່າວສານ ແລະ ກິດຈະກຳ)"
        verbose_name_plural = "News & Activities (ຂ່າວສານ ແລະ ກິດຈະກຳ)"

    def __str__(self):
        return self.title

class OrgChart(models.Model):
    title = models.CharField(max_length=255, default="ຜັງອົງກອນ (Organization Chart)")
    image = models.ImageField(upload_to='org_chart/')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Organization Chart (ຜັງອົງກອນ)"
        verbose_name_plural = "Organization Chart (ຜັງອົງກອນ)"

    def __str__(self):
        return self.title
