
import json
import boto3
import paramiko
import os
import datetime

#byte to string function
def btos(by):
    return (str(by, 'utf-8'))
    

def log(txt):
    x = datetime.datetime.now()
    date = x.strftime("%d-%m-%Y %H:%M:%S")
    log_file = open("log.txt","a")
    log_file.write(f"{date} :{txt}\n")

def lambda_handler(event, context):
    
    x = datetime.datetime.now()
    date = x.strftime("%d-%b-%Y")

    # boto3 client
    client = boto3.client('ec2')
    s3_client = boto3.client('s3')
    
    # getting instance information
    describeInstance = client.describe_instances()

    
    hostPublicIP=[]
    # fetchin public IP address of the running instances
    for i in describeInstance['Reservations']:
        for instance in i['Instances']:
            if instance["State"]["Name"] == "running":
                hostPublicIP.append(instance['PublicIpAddress'])
    
    print(hostPublicIP)
    
    # downloading pem filr from S3
    s3_client.download_file('assignments3toec2','lseg2.pem', '/tmp/file.pem')

    # reading pem file and creating key object
    key = paramiko.RSAKey.from_private_key_file("/tmp/file.pem")
    # an instance of the Paramiko.SSHClient
    ssh_client = paramiko.SSHClient()
    # setting policy to connect to unknown host
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    host=hostPublicIP[0]
    print("Connecting to : " + host)
    # connecting to server
    ssh_client.connect(hostname=host, username="ubuntu", pkey=key)
    print("Connected to :" + host)

    # command list
    command = f'cat /var/log/nginx/access.log | grep "{date}"'
    
    stream = os.popen(command)
    output = stream.readlines()


    for i in output:
    print(i)

   
    
    return {
        'statusCode': 200,
        'body': json.dumps('Thanks!')
    }
