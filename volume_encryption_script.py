import boto3
import datetime
import time

# AWS credentials and region configuration
aws_access_key_id = 'AKIAVFYPMCWHXMOO4DGR'
aws_secret_access_key = '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'
aws_region = 'us-east-1'

# Input from the user
instance_id = input("Enter the instance ID: ")

# Create AWS EC2 client
ec2_client = boto3.client(
    'ec2',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)

# Step 1: Stop instance
print("Step 1: Stopping the instance...")
ec2_client.stop_instances(InstanceIds=[instance_id])
waiter = ec2_client.get_waiter('instance_stopped')
waiter.wait(InstanceIds=[instance_id])
print("Instance stopped successfully.")

# Step 2: Store volume information
print("Step 2: Storing volume information...")
response = ec2_client.describe_instances(InstanceIds=[instance_id])
instance = response['Reservations'][0]['Instances'][0]
volumes = instance['BlockDeviceMappings']

# Find the volume ID and device name associated with the root device
root_device_name = instance['RootDeviceName']
volume_id = volumes[0]['Ebs']['VolumeId']

print(f"Root device name: {root_device_name}")
print(f"Volume ID associated with the root device: {volume_id}")

# Step 3: Create a snapshot of the existing volume
print("Step 3: Creating a snapshot of the existing volume...")
snapshot_description = f"newcopy_{datetime.datetime.now().strftime('%d-%m-%Y')}_{volume_id}"
snapshot_response = ec2_client.create_snapshot(VolumeId=volume_id, Description=snapshot_description)
snapshot_id = snapshot_response['SnapshotId']

# Wait for the snapshot to be completed
while True:
    snapshot_status = ec2_client.describe_snapshots(SnapshotIds=[snapshot_id])['Snapshots'][0]['State']
    if snapshot_status == 'completed':
        break
    time.sleep(15)

print("Snapshot created successfully.")

# Step 4: Create a new volume from the snapshot
print("Step 4: Creating a new volume from the snapshot...")
new_volume_response = ec2_client.create_volume(
    AvailabilityZone=instance['Placement']['AvailabilityZone'],
    SnapshotId=snapshot_id,
    VolumeType='gp2',  # Adjust volume type if needed
    Encrypted=True
)
new_volume_id = new_volume_response['VolumeId']

print("New volume created successfully.")

# Step 5: Detach existing volume
print("Step 5: Detaching the existing volume...")
ec2_client.detach_volume(InstanceId=instance_id, VolumeId=volume_id)
waiter = ec2_client.get_waiter('volume_available')
waiter.wait(VolumeIds=[volume_id])
print("Existing volume detached successfully.")

# Step 6: Attach new encrypted volume
print("Step 6: Attaching the new encrypted volume...")
ec2_client.attach_volume(
    InstanceId=instance_id,
    VolumeId=new_volume_id,
    Device=root_device_name
)
waiter = ec2_client.get_waiter('volume_in_use')
waiter.wait(VolumeIds=[new_volume_id])
print("New encrypted volume attached successfully.")

# Start the instance
print("Starting the instance...")
ec2_client.start_instances(InstanceIds=[instance_id])
waiter = ec2_client.get_waiter('instance_running')
waiter.wait(InstanceIds=[instance_id])
print("Instance started successfully.")

print("Volume replacement completed successfully.")
