from django.urls import path

from sparrow.call_records.views import CallRecordsView


app_name = 'call_records'
urlpatterns = [
    path('', CallRecordsView.as_view(), name='index'),
]
