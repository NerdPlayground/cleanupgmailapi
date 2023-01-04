from django.urls import path
from gmail.views import (
    labels,filters,
    senders,clean_up_mailbox
)

app_name="gmail"
urlpatterns=[
    path("labels/",labels,name="labels"),
    path("filters/",filters,name="filters"),
    path("senders/",senders,name="senders"),
    path("clean-up-mailbox/",clean_up_mailbox,name="clean-up-mailbox")
]