from __future__ import print_function
from gmail.common import get_labels
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from gmail.authentication import credentials

def remove_header(read_from):
    for read_line in read_from:
        read_line=read_line.strip()
        if "recepients" in read_line:
            break

def get_senders():
    read_from= open("recepients.txt")
    remove_header(read_from)
    senders=list()
    for read_line in read_from:
        read_line=read_line.strip().replace('"','')
        if '}' in read_line:
            break
        read_line=read_line[0:read_line.find(':')]

        email_start=read_line.find('<')
        if email_start!=-1 and read_line.find("via",0,email_start)!=-1:
            new_label=read_line[
                read_line.find("via")+4:read_line.find(")")
            ]
            read_line=new_label+read_line[read_line.find('\\',1)+1:]

        email_start=read_line.find('<')
        if email_start!=-1 and read_line.find('@',0,email_start)!=-1:
            read_line=read_line[read_line.find('@')+2:]

        read_line=read_line.replace('\\','')
        senders.append(read_line)
    return senders

def get_top_level_domains():
    domains=list()
    read_from=open("gmail/tlds-alpha-by-domain.txt")
    for line in read_from:
        line=line.strip()
        domains.append(line)
    return domains

def custom_labels():
    labels=dict()
    senders=get_senders()
    domains=get_top_level_domains()
    for sender in senders:
        email=sender if sender.find('<')==-1 else sender[sender.find('<')+1:-1]
        label=email[email.find('@')+1:].split('.')[::-1]
        for part in label:
            if part not in domains:
                label=" ".join(label[label.index(part):]).title()
                break
        labels[label]=labels.get(label,set()).union({email})
    
    for label,emails in labels.items():
        print(label,len(emails),sep=": ")
        print(*emails,sep="\n")
        print()

def delete_label(label_id):
    try:
        service=build('gmail','v1',credentials=credentials())
        results=service.users().labels().delete(
            userId='me',id=label_id
        ).execute()
    except HttpError as error:
        error_message={"error":error._get_reason()}
        return {"error_message":error_message}

def get_filters():
    try:
        service=build('gmail', 'v1', credentials=credentials())
        filters=service.users().settings().filters().list(
            userId="me"
        ).execute()
        return {"filters":filters}
    except HttpError as error:
        error_message={"error":error._get_reason()}
        return {"error_message":error_message}

def delete_filter(filter_id):
    try:
        service=build('gmail', 'v1', credentials=credentials())
        results=service.users().settings().filters().delete(
            userId="me",id=filter_id
        ).execute()
    except HttpError as error:
        error_message={"error":error._get_reason()}
        return {"error_message":error_message}

def main():
    labels=get_labels(type="user").get("labels")
    for label in labels:
        delete_label(label.get("id"))
    
    filters=get_filters().get("filters").get("filter")
    for filter in filters:
        delete_filter(filter.get("id"))

if __name__ == '__main__':
    main()