from django.db import models


class History(models.Model):
    table_name = models.CharField(max_length=255, editable=False)
    user = models.ForeignKey("User", on_delete=models.PROTECT, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    item_id = models.CharField(max_length=255, editable=False)
    action = models.CharField(max_length=25, editable=False)
    body= models.TextField(default ='',editable=False)

    class Meta:
        verbose_name_plural = "History model"

    def __str__(self):
        return self.action