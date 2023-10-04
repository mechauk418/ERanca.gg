from django.urls import path, include
from .views import *


urlpatterns = [
    path("character/", CharacterView.as_view({'get':'list', 'post':'create'})),
    path("item/", ItemView.as_view({'get':'list', 'post':'create'})),
    path("<int:pk>/", CharacterView.as_view({'get':'retrieve', "put": "update", "patch": "partial_update"})),
    path("characterload/", Characterload),
    path("itemload/", Itemload),
    path("rpview/", CharacterRPView.as_view({'get':'list', 'post':'create'})),
    path("item/<int:pk>", ItemView.as_view({'get':'retrieve', "put": "update", "patch": "partial_update"}))
]