from django.urls import path
from gmail.views import labels,emails,senders,clean_up_mailbox

app_name="gmail"
urlpatterns=[
    path("labels/",labels,name="labels"),
    path("emails/",emails,name="emails"),
    path("senders/",senders,name="senders"),
    path("clean-up-mailbox/",clean_up_mailbox,name="clean-up-mailbox")
]