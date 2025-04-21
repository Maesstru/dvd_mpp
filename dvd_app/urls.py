# chat/urls.py
from django.urls import path

from . import views

app_name = 'dvd_app'

urlpatterns = [
    path("", views.MainView.as_view(), name="main_view"),#gata
    path("confirm_copil/<int:copil_id>/", views.ConfirmCopilView.as_view(), name="confirm_copil"),#gata
    path("login/", views.LoginView.as_view(), name="login"),#gata
    path("signup/", views.SignupView.as_view(), name="signup"),#gata
    path("actualizeaza_date/", views.UpdateUserView.as_view(), name="actualizeaza_date"),#gata
    path("copiii_mei/", views.CopiiiMeiView.as_view(), name="copiii_mei"),#gata
    path("logout/", views.LogoutView.as_view(), name="logout"),#gata
    path("cadou_livrat/<int:copil_id>/", views.CadouLivratView.as_view(), name="cadou_livrat"),#gata
    path("confirm_renunta/<int:copil_id>/", views.ConfirmRenuntaView.as_view(), name="confirm_renunta"),#gata
    path("detalii/<int:copil_id>/", views.DetaliiCopilView.as_view(), name="detalii"),#gata
    path("schimba_parola/", views.EmailParolaView.as_view(), name="schimba_parola"),#gata
    path("parola_noua/<str:password_change_key>/", views.UpdateParolaView.as_view(), name="parola_noua"),#gata
]