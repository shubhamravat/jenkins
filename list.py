import boto3
region = 'ap-south-1'
aws_mag_con=boto3.session.Session(region_name=region)
ec2_con_cli=aws_mag_con.client("ec2")
response=ec2_con_cli.describe_instances()
print(response['Reservations'])
for each_item in response['Reservations']:
    for each_instance in each_item['Instances']:
        print(each_instance['InstanceType'])
        print("-----------------------------------------------")

#list s3 bucket         

s3_con_cli=aws_mag_con.client("s3")
s3_response=s3_con_cli.list_buckets()
Footer
