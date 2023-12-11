import boto3
import datetime

# Initialize AWS session
session = boto3.Session(
    aws_access_key_id='AKIAVFYPMCWHUJ5H4BPQ',
    aws_secret_access_key='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',
    region_name='us-east-1'
)

# Initialize EC2 client
ec2 = session.client('ec2')

# Get the current date in the format DD-MM-YYYY
date_today = datetime.datetime.now().strftime('%d-%m-%y')

# Get all running instances
instances = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

for reservation in instances['Reservations']:
    for instance in reservation['Instances']:
        instance_id = instance['InstanceId']
        instance_name = 'Unknown'  # Default name if no tags found

        # Get instance name from tags if available
        for tag in instance['Tags']:
            if tag['Key'] == 'Name':
                instance_name = tag['Value']

        ami_name = f'{instance_name}-{date_today}'   

        print(f'Creating AMI for Instance ID: {instance_id}')
        response = ec2.create_image(
            InstanceId=instance_id,
            Name=ami_name,
            NoReboot=True  # No reboot for this AMI
        )

        print(f'AMI ID: {response["ImageId"]}')


--------------------------------------------------------------------------------
install pythin pip and boto3 

create a user and it's create access & secret keys

python3 "filename"

------------------------------------------------------------------------------------ 
