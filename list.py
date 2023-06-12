import boto3
import pandas as pd

aws_mag_con = boto3.session.Session()
aws_ec2_con = aws_mag_con.client("ec2")
aws_s3_con = aws_mag_con.client("s3")
ssm = aws_mag_con.client("ssm")
sns_con_cli = aws_mag_con.client("sns")

response = aws_ec2_con.describe_instances()["Reservations"]
instance_list = []
count = 1
hostname_error = "NA"

# Create a dataframe to hold the instance data
data = {"S_No": [],"Name":[], "Host": [], "Instance Id": [], "State": [], "Instance Type": [], "AZ": [], "Private IP": [], "VPC ID": [], "SubnetID": []}
df = pd.DataFrame(data)

for item in response:
    for each in item["Instances"]:
        instance_list.append(each["InstanceId"])

for instance_id in instance_list:
    try:
        instance = aws_ec2_con.describe_instances(InstanceIds=[instance_id])["Reservations"][0]["Instances"][0]
        state = instance["State"]["Name"]
        
        if state != "running":
            print(f"Instance {instance_id} is not running")
            for tag in instance['Tags']:
                if tag['Key'] =='Name':
                    tag_value=tag['Value']
            new_row = {"Name":tag_value,"S_No": count, "Host": hostname, "Instance Id": instance["InstanceId"], "State": instance["State"]["Name"], "Instance Type": instance["InstanceType"], "AZ": instance["Placement"]["AvailabilityZone"], "Private IP": instance["PrivateIpAddress"], "VPC ID": instance["VpcId"], "SubnetID": instance["SubnetId"]}
            df = pd.concat([df, pd.DataFrame(new_row, index=[0])], ignore_index=True)
            count=count+1
            continue
        
        response = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={"commands": ["hostname"]}
        )

        command_id = response["Command"]["CommandId"]

        while True:
            status_response = ssm.list_commands(CommandId=command_id, InstanceId=instance_id)
            status = status_response["Commands"][0]["Status"]
            
            if status in ["Pending", "InProgress"]:
                continue
            
            elif status == "Success":
                output_response = ssm.get_command_invocation(CommandId=command_id, InstanceId=instance_id)
                hostname = output_response["StandardOutputContent"].strip()
                
                # Add the instance data to the dataframe
                for tag in instance['Tags']:
                    if tag['Key'] =='Name':
                        tag_value=tag['Value']
            #new_row = {"Name":tag_value,"S_No": count, "Host": hostname, "Instance Id": instance["InstanceId"], "State": instance["State"]["Name"], "Instance Type": instance["InstanceType"], "AZ": instance["Placement"]["AvailabilityZone"], "Private IP": instance["PrivateIpAddress"], "VPC ID": instance["VpcId"], "SubnetID": instance["SubnetId"]}
                new_row = {"Name":tag_value,"S_No": count, "Host": hostname, "Instance Id": instance["InstanceId"], "State": instance["State"]["Name"], "Instance Type": instance["InstanceType"], "AZ": instance["Placement"]["AvailabilityZone"], "Private IP": instance["PrivateIpAddress"], "VPC ID": instance["VpcId"], "SubnetID": instance["SubnetId"]}
                df = pd.concat([df, pd.DataFrame(new_row, index=[0])], ignore_index=True)
                count=count+1
                break
            
            else:
                print(f"Error executing command on instance {instance_id}")
                break
    
    except Exception as e:
        for tag in instance['Tags']:
                if tag['Key'] =='Name':
                    tag_value=tag['Value']
            #new_row = {"Name":tag_value,"S_No": count, "Host": hostname, "Instance Id": instance["InstanceId"], "State": instance["State"]["Name"], "Instance Type": instance["InstanceType"], "AZ": instance["Placement"]["AvailabilityZone"], "Private IP": instance["PrivateIpAddress"], "VPC ID": instance["VpcId"], "SubnetID": instance["SubnetId"]}
        new_row = {"Name":tag_value,"S_No": count, "Host": hostname_error, "Instance Id": instance["InstanceId"], "State": instance["State"]["Name"], "Instance Type": instance["InstanceType"], "AZ": instance["Placement"]["AvailabilityZone"], "Private IP": instance["PrivateIpAddress"], "VPC ID": instance["VpcId"], "SubnetID": instance["SubnetId"]}
        df = pd.concat([df, pd.DataFrame(new_row, index=[0])], ignore_index=True)
        count=count+1
        continue

# Convert the dataframe to an XLSX file
with pd.ExcelWriter("EC2_inventory.xlsx") as writer:
    df.to_excel(writer, index=False)

# Upload the XLSX file to S3
with open("EC2_inventory.xlsx", "rb") as file:
    aws_s3_con.upload_fileobj(file, "ec2-shubham-inventory", "EC2_inventory.xlsx")
