from django.urls import path
from . import views
urlpatterns=[
    path('user/',views.createUser),
    path('user/auth/',views.loginUser),
    path('sites/list/',views.listUserNotes),
    path('sites/',views.addNotes)
]