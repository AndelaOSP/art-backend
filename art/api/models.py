from django.db import models

class Asset(models.Model):
    full_name = models.CharField(max_length=50)
    cohort = models.CharField(max_length=50)
    mac_book_sn = models.CharField(max_length=12)
    mac_book_tag = models.CharField(max_length=12)
    charger_tag = models.CharField(max_length=12)
    tb_dongle_tag = models.CharField(max_length=12)
    headsets_sn = models.CharField(max_length=12)
    headsets_tag = models.CharField(max_length=12)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name, self.cohort, self.mac_book_sn, self.mac_book_tag,\
         self.charger_tag, self.tb_dongle_tag, self.headsets_sn, self.headsets_tag, \
         self.date_created, self.date_modified

class CheckinLogs(models.Model):
    user_id = models.ForeignKey(Asset, on_delete=models.CASCADE)
    mac_book = models.BooleanField(default=False)
    charger = models.BooleanField(default=False)
    tb_dongle = models.BooleanField(default=False)
    head_set = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user_id, self.mac_book, self.charger, self.tb_dongle, \
        self.head_set, self.date_created

class CheckoutLogs(models.Model):
    user_id = models.ForeignKey(Asset, on_delete=models.CASCADE)
    mac_book = models.BooleanField(default=False)
    charger = models.BooleanField(default=False)
    tb_dongle = models.BooleanField(default=False)
    head_set = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_id, self.mac_book, self.charger, self.tb_dongle, \
        self.head_set, self.date_created
