from django.urls import path, include
from .views import *

app_name = "gamerecord"


urlpatterns = [
    path("rererererer/", RecordView.as_view({'post':'create'})),
    # path("getusernum/<str:nickname>/", getusernum),
    path("getsearch/<str:nickname>/", RecordView.as_view({'get':'list', 'post':'create'})),
    path("getdetail/<str:nickname>/", UserDetailView.as_view({'get':'retrieve'})),
    path("getdetail/", UserDetailView.as_view({'get':'list'})),
    path("recentgainrp/<str:nickname>/", recentgainrp),
    path("refresh/<str:nickname>/", refresh),
    path("userch/<str:nickname>/", UseChView.as_view({'get':'retrieve'})),
    path("crop/", detect_text),

]