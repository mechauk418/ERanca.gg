from django.urls import path, include
from .views import *

app_name = "gamerecord"


urlpatterns = [
    path("rererererer/", RecordView.as_view({'post':'create'})),
    # path("getusernum/<str:nickname>/", getusernum),
    path("getsearch/<str:nickname>/<int:season>", RecordView.as_view({'get':'list', 'post':'create'})),
    path("getdetail/<str:nickname>/<int:season>", UserDetailView.as_view({'get':'retrieve'})),
    path("getdetail/", UserDetailView.as_view({'get':'list'})),
    path("recentgainrp/<str:nickname>/<int:season>", recentgainrp),
    path("refresh/<str:nickname>/", refresh),
    path("userch/<str:nickname>/<int:season>", UseChView.as_view({'get':'retrieve'})),
    path("crop/", detect_text),
]