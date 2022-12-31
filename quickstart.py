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

def main():
    names={"George","Mobisa","Kitawi","Dorobu"}
    extras="William OR Nalana OR "
    joined=" OR ".join(names)
    print(extras+joined)

if __name__ == '__main__':
    main()