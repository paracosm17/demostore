from django.urls import path

from store.views.Appeal import AppealApi
from store.views.Category import CategoryApi
from store.views.Product import ProductApi
from store.views.Purchase import PurchaseApi
from store.views.TgUser import TgUserApi, TgUserUpdate

urlpatterns = [
    path('categories/', CategoryApi.as_view()),
    path('purchases/', PurchaseApi.as_view()),
    path('users/', TgUserApi.as_view()),
    path('products/', ProductApi.as_view()),
    path('appeals/', AppealApi.as_view()),

    path('categories/create/', CategoryApi.as_view()),
    path('users/create/', TgUserApi.as_view()),
    path('purchases/create/', PurchaseApi.as_view()),
    path('products/create/', ProductApi.as_view()),
    path('appeals/create/', AppealApi.as_view()),

    path('users/update/', TgUserUpdate.as_view())
]
