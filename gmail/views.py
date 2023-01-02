from __future__ import print_function
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from gmail.common import (
    get_emails,get_labels,get_senders,get_custom_labels,
    clean_emails,create_label,create_filter,delete_filter,
    apply_filter,
)

@api_view()
def clean_up_mailbox(request):
    emails=get_emails(["INBOX"])
    ungrouped_emails=clean_emails(emails)
    if ungrouped_emails.get("messages")!=None:
        custom_labels=get_custom_labels(ungrouped_emails)
        if custom_labels.get("labels")!=None:
            counter=0
            custom_labels=custom_labels.get("labels")
            for custom_label,label_emails in custom_labels.items():
                results=create_label(custom_label)
                if results.get("error_message")!=None:
                    return Response(# pragma: no cover
                        results.get("error_message"),
                        status=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    extras=str()
                    if results.get("filter_id")!=None:
                        criteria_from=delete_filter(results.get("filter_id"))
                        if criteria_from.get("criteria_from")!=None:
                            criteria_from=criteria_from.get("criteria_from")
                            extras=criteria_from+" OR "
                        else:
                            return Response(# pragma: no cover
                                criteria_from.get("error_message"),
                                status=status.HTTP_400_BAD_REQUEST
                            )
                    contents={
                        "from":extras+" OR ".join(label_emails),
                        "label":results.get("label_id")
                    }
                    
                    filter=create_filter(contents)
                    if filter.get("filter")!=None:
                        filter=filter.get("filter")
                        results=apply_filter(filter)
                        if results.get("results")!=None:
                            counter+=1
                        else:
                            return Response(# pragma: no cover
                                results.get("error_message"),
                                status=status.HTTP_400_BAD_REQUEST
                            )
                    else:
                        return Response(# pragma: no cover
                            filter.get("error_message"),
                            status=status.HTTP_400_BAD_REQUEST
                        )
            message={
                "message":"Mailbox Cleaned; Filters Created "+str(counter)
            }
            return Response(message,status=status.HTTP_200_OK)
        else:
            return Response(# pragma: no cover
                custom_labels.get("error_message"),
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        return Response(# pragma: no cover
            ungrouped_emails.get("error_message"),
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view()
def labels(request):
    labels=get_labels()
    if labels.get("labels")!=None:
        message={
            "count":len(labels.get("labels")),
            "labels":labels.get("labels")
        }
        return Response(message,status=status.HTTP_200_OK)
    return Response(labels.get("error_message"),status=status.HTTP_400_BAD_REQUEST)# pragma: no cover

@api_view()
def emails(request):
    emails=get_emails(["INBOX"])
    if emails.get("messages")!=None:
        message={
            "count":len(emails.get("messages")),
            "messages":emails.get("messages")
        }
        return Response(message,status=status.HTTP_200_OK)
    return Response(emails.get("error_message"),status=status.HTTP_400_BAD_REQUEST)# pragma: no cover

@api_view()
def senders(request):
    emails=get_emails(["INBOX"])
    senders=get_senders(emails)
    if senders.get("senders")!=None:
        message={
            "count":len(senders.get("senders")),
            "senders":senders.get("senders"),
        }
        return Response(message,status=status.HTTP_200_OK)
    return Response(senders.get("error_message"),status=status.HTTP_400_BAD_REQUEST)# pragma: no cover