from django.urls import path

from sparrow.call_records.views import CallRecordsView, get_telephone_bill


app_name = 'call_records'
urlpatterns = [
    path('', CallRecordsView.as_view(), name='index'),
    path('telephone_bill/', get_telephone_bill, name='telephone_bill'),
]
