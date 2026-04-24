from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class PopupMessage(models.Model):
    title = models.CharField(max_length=255, verbose_name="ຫົວຂໍ້")
    message = models.TextField(verbose_name="ຂໍ້ຄວາມ")
    image = models.ImageField(upload_to='popups/', blank=True, null=True, verbose_name="ຮູບພາບປະກອບ")
    
    # Targeting
    target_users = models.ManyToManyField(User, blank=True, related_name='popup_messages', 
                                         verbose_name="ຜູ້ປົກຄອງທີ່ຕ້ອງການສົ່ງໃຫ້ (ປະຫວ່າງໄວ້ເພື່ອສົ່ງໃຫ້ທຸກຄົນ)")
    
    is_active = models.BooleanField(default=True, verbose_name="ເປີດນຳໃຊ້")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Popup Message (ຂໍ້ຄວາມປ໊ອບອັບ)"
        verbose_name_plural = "Popup Messages (ຂໍ້ຄວາມປ໊ອບອັບ)"
        ordering = ['-created_at']

    def __str__(self):
        return self.title
