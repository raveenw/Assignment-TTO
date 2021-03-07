import json
import boto3
import paramiko
import os
import datetime

def btos(by):
    return (str(by, 'utf-8'))

def log(txt):
    s3_logger = boto3.client('s3')
    x = datetime.datetime.now()
    date = x.strftime("%d-%m-%Y %H:%M:%S")
    s3_logger.put_object(Body=txt, Bucket='assignments3toec2', Key='log1.txt')

def lambda_handler(event, context):
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
    
    # downloading pem file from S3
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
    log("Connected to :" + host)
    
    # command list
    
    stdin , stdout, stderr = ssh_client.exec_command('systemctl is-active nginx.service')
    out = btos(stdout.read()).split("\n")
    output = out[0]
    print(output)
    log(f'Status of Server: {output}')
    
    if output != 'active':
        stdin , stdout, stderr = ssh_client.exec_command('sudo systemctl start nginx.service')
        output = btos(stdout.read())
       # print(f'errors  {stdout}' )
        stdin , stdout, stderr = ssh_client.exec_command('systemctl is-active nginx.service')
        out = btos(stdout.read()).split("\n")
        output = out[0]
        
        if output != 'active':
            print('send mail')
            #mail
       
        else:
            print('Service is restarted')
    print(f"System is on {output} state")
    return {
        'statusCode': 200,
        'body': json.dumps('Thanks!')
    }
