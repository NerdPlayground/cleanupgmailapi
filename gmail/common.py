from __future__ import print_function
import random
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from gmail.authentication import credentials

def get_top_level_domains():
    domains=list()
    read_from=open("gmail/tlds-alpha-by-domain.txt")
    for line in read_from:
        line=line.strip()
        domains.append(line)
    return domains

def get_labels(type="all"):
    try:
        service=build('gmail','v1',credentials=credentials())
        results=service.users().labels().list(userId='me').execute()
        labels=results.get('labels',[])
        if type!="all":
            requested_labels=list()
            for label in labels:
                if label.get("type")==type:
                    requested_labels.append(label)
            labels.clear()
            labels.extend(requested_labels)
        return {"labels":labels}
    except HttpError as error:# pragma: no cover
        error_message={"error":error._get_reason()}
        return {"error_message":error_message}

def get_label_names(labels):
    return [label.get("id") for label in labels]

def get_label(label_id):
    try:
        service=build('gmail', 'v1', credentials=credentials())
        label=service.users().labels().get(userId="me",id=label_id).execute()
        return {"label":label}
    except HttpError as error:# pragma: no cover
        error_message={"error":error._get_reason()}
        return {"error_message":error_message}

def get_message(message_id):
    try:
        service=build('gmail','v1',credentials=credentials())
        results=service.users().messages().get(
            userId="me",id=message_id
        ).execute()
        return {"message":results}
    except HttpError as error:# pragma: no cover
        error_message={"error":error._get_reason()}
        return {"error_message":error_message}

def get_emails(labels,query=""):
    messages=list()
    try:
        service=build('gmail','v1',credentials=credentials())
        results=service.users().messages().list(
            userId="me",labelIds=labels,
            q=query,includeSpamTrash=False
        ).execute()
        if "messages" in results:
            messages.extend(results.get("messages"))
        
        while "nextPageToken" in results:
            results=service.users().messages().list(
                userId="me",includeSpamTrash=False,q=query,
                labelIds=labels,pageToken=results.get("nextPageToken")
            ).execute()
            if "messages" in results:
                messages.extend(results.get("messages"))
        return {"messages": messages}
    except HttpError as error:# pragma: no cover
        error_message={"error":error._get_reason()}
        return {"error_message":error_message}

def clean_emails(emails):
    ungrouped_emails=list()
    if emails.get("messages")!=None:
        custom_labels=get_labels(type="user")
        if custom_labels.get("labels")!=None:
            custom_labels=get_label_names(custom_labels.get("labels"))
            for message_details in emails.get("messages"):
                received_message=get_message(message_details.get("id"))
                if received_message.get("message")!=None:
                    message_labels=received_message.get("message").get("labelIds")
                    if not any(label in message_labels for label in custom_labels):
                        ungrouped_emails.append(message_details)
                else:# pragma: no cover
                    return {"error_message":received_message.get("error_message")}
            return {"messages":ungrouped_emails}
        else:# pragma: no cover
            return {"error_message":custom_labels.get("error_message")}
    else:# pragma: no cover
        return {"error_message":emails.get("error_message")}

def get_senders(emails):
    if emails.get("messages")!=None:
        senders=dict()
        for message_details in emails.get("messages"):
            received_message=get_message(message_details.get("id"))
            if received_message.get("message")!=None:
                headers=received_message.get("message").get("payload").get("headers")
                sender=filter(lambda header: header['name'] == 'From',headers)
                sender=list(sender)[0]
                senders[sender['value']]=senders.get(sender['value'],0)+1
            else:# pragma: no cover
                return {"error_message":received_message.get("error_message")}
        return {"senders":senders}
    return {"error_message":emails.get("error_message")}# pragma: no cover

def clean_senders(senders):
    cleaned_senders=list()
    for sender in senders.get("senders"):
        sender=sender.replace('"','')
        email_start=sender.find('<')
        if email_start!=-1 and sender.find("via",0,email_start)!=-1:
            new_label=sender[
                sender.find("via")+4:sender.find(")")]
            sender=new_label+sender[email_start-1:]
        email_start=sender.find('<')
        if email_start!=-1 and sender.find('@',0,email_start)!=-1:
            sender=sender[sender.find('@')+2:]
        cleaned_senders.append(sender)
    return cleaned_senders

def get_random_color():
    colors=[
        '#000000','#434343','#cc3a21','#ac2b16','#0b804b','#285bac',
        '#653e9b','#b65775','#822111','#a46a21','#076239','#1a764d',
        '#1c4587','#41236d','#83334c','#464646','#0d3472','#0d3b44',
        '#3d188e','#711a36','#8a1c0a','#7a2e0b','#7a4706','#594c05',
        '#684e07','#0b4f30','#04502e','#994a64','#662e37','#094228',
    ]
    return random.choice(colors)

def create_label(label):
    try:
        custom_label={
            "name":label,
            "type":"user",
            "color":{
                "textColor": "#ffffff",
                "backgroundColor":get_random_color()
            }
        }
        service=build('gmail','v1',credentials=credentials())
        label=service.users().labels().create(userId="me",body=custom_label).execute()
        return {
            "label_id":label.get("id")
        }
    except HttpError as error:
        error_message={"error":error._get_reason()}
        if error_message.get("error")=="Label name exists or conflicts":
            contents=get_filters_labels()
            if contents.get("contents")!=None:
                contents=contents.get("contents")
                if contents.get(label)!=None:
                    return {
                        "label_id":contents.get(label)[0],
                        "filter_id":contents.get(label)[1]
                    }
                else:
                    return create_label(label+" (filtered)")
            else:
                return {"error_message":contents.get("error_message")}# pragma: no cover
        else:
            return {"error_message":error_message}# pragma: no cover

def get_custom_labels(emails):
    labels=dict()
    senders=get_senders(emails)
    if senders.get("senders")!=None:
        senders=clean_senders(senders)
        domains=get_top_level_domains()
        for sender in senders:
            email=sender if sender.find('<')==-1 else sender[sender.find('<')+1:-1]
            label_parts=email[email.find('@')+1:].split('.')[::-1]
            label=str()
            for part in label_parts:
                if part not in domains:
                    label+=(part+" ")
            label=label.strip()
            labels[label]=labels.get(label,set()).union({email})
        return {"labels":labels}
    return {"error_message":senders.get("error_message")}# pragma: no cover

def apply_filter(filter):
    try:
        emails=get_emails(
            ["INBOX"],
            query=filter.get("criteria").get("from")
        )
        if emails.get("messages")!=None:
            ids=list()
            emails=emails.get("messages")
            for message in emails:
                ids.append(message.get("id"))
            
            modification_content={
                "ids":ids,
                "addLabelIds":[
                    filter.get("action").get("addLabelIds")[0]
                ]
            }
            service=build('gmail', 'v1', credentials=credentials())
            results=service.users().messages().batchModify(
                userId="me",body=modification_content
            ).execute()
            return {"results":results}
        else:# pragma: no cover
            return {"error_message":emails.get("error_message")}
    except HttpError as error:# pragma: no cover
        error_message={"error":error._get_reason()}
        return {"error_message":error_message}

def get_filter(filter_id):
    try:
        service=build('gmail', 'v1', credentials=credentials())
        filter=service.users().settings().filters().get(
            userId="me",id=filter_id
        ).execute()
        return filter
    except HttpError as error:# pragma: no cover
        error_message={"error":error._get_reason()}
        return {"error_message":error_message}

def get_filters():
    try:
        service=build('gmail', 'v1', credentials=credentials())
        filters=service.users().settings().filters().list(
            userId="me"
        ).execute()
        return {"filters":filters}
    except HttpError as error:# pragma: no cover
        error_message={"error":error._get_reason()}
        return {"error_message":error_message}

def create_filter(contents):
    try:
        filter={
            "criteria":{
                "from":contents.get("from")
            },
            "action":{
                "addLabelIds":[contents.get("label")],
                "removeLabelIds":["SPAM"],
            }
        }
        service=build('gmail','v1',credentials=credentials())
        results=service.users().settings().filters().create(
            userId="me",body=filter
        ).execute()
        return {"filter":results}
    except HttpError as error:# pragma: no cover
        error_message={"error":error._get_reason()}
        return {"error_message":error_message}

def delete_filter(filter_id):
    try:
        filter=get_filter(filter_id)
        criteria_from= filter.get("criteria").get("from")
        service=build('gmail','v1',credentials=credentials())
        results=service.users().settings().filters().delete(
            userId="me",id=filter_id
        ).execute()
        return {"criteria_from":criteria_from}
    except HttpError as error:# pragma: no cover
        error_message={"error":error._get_reason()}
        return {"error_message":error_message}

def get_filters_labels():
    try:
        service=build('gmail','v1',credentials=credentials())
        results=service.users().settings().filters().list(userId='me').execute()
        filters=results.get("filter",[])
        contents=dict()
        for filter in filters:
            if filter.get("action").get("addLabelIds")!=None:
                label_id=filter.get("action").get("addLabelIds")[0]
                label=get_label(label_id)
                if label.get("label"):
                    label=label.get("label").get("name")
                    contents[label]=(label_id,filter.get("id"))
                else:# pragma: no cover
                    return {"error_message":label.get("error_message")}
        return {"contents":contents}
    except HttpError as error:# pragma: no cover
        error_message={"error":error._get_reason()}
        return {"error_message":error_message}