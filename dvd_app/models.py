from django.db import models
from django.core.mail import send_mail
from django.conf import settings

from . import utils


class Binevoitor(models.Model):
    email = models.EmailField(max_length=100)
    parola = models.CharField(max_length=100)
    nume = models.CharField(max_length=100)
    telefon = models.CharField(max_length=20)
    password_change_key = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.email + " " + self.nume

    def send_password_reset(self, reset_url):
        mesaj = utils.password_reset_email % (reset_url)

        send_mail(
            "Resetarea parolei",
            mesaj,
            "daruindveidobandi.ascorcluj@gmail.com",
            [self.email],
            fail_silently=False,
        )



class Copil(models.Model):
    GEN = [
        ("BAIAT", "Baiat"),
        ("FATA", "Fata"),
    ]

    binevoitor = models.ForeignKey(Binevoitor, on_delete=models.SET_NULL, null=True, blank=True)
    varsta = models.PositiveIntegerField(null=True, blank=True)
    gen = models.CharField(max_length=10, choices=GEN)
    descriere = models.CharField(max_length=1000, blank=True, null=True, default="")
    parohie = models.CharField(max_length=100, blank=True, null=True, default="")
    daruit = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["varsta", "gen"]),
        ]

    def __str__(self):
        return str(self.varsta) + " | " + self.gen + \
            (" | " +  self.parohie[:65] if self.parohie else "") + \
            (" | " + self.descriere[:30] if self.descriere else "")

    @staticmethod
    def get_varste_ramase():
        return [(x.varsta, str(x.varsta) + ' an(i)') for x in Copil.objects.filter(binevoitor=None)]


    @staticmethod
    def send_reminder_mails(mesaj):
        recipients = {}
        for copil in Copil.objects.filter(binevoitor__isnull=False, daruit=False):
            mail_binevoitor = copil.binevoitor.email
            str_copil = copil.get_gen_display() + ', ' + str(copil.varsta) + ' an(i)'
            if mail_binevoitor in recipients.keys():
                recipients[mail_binevoitor].append(str_copil)
            else:
                recipients[mail_binevoitor] = [str_copil]

        domain_name = settings.DOMAIN_NAME
        for mail, copii in recipients.items():
            copii_str = '\n'.join(copii)
            send_mail(
                "Nu uita sa daruiesti!",
                mesaj % (copii_str, "https://" + domain_name),
                "daruindveidobandi.ascorcluj@gmail.com",
                [mail],
                fail_silently=False,
            )


