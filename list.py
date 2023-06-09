import boto3
aws_mag_con=boto3.session.Session()
ec2_con_cli=aws_mag_con.client(service_name='ec2',region_name='ap-south-1')
response=ec2_con_cli.describe_instances()
print(response['Reservations'])
for each_item in response['Reservations']:
    for each_instance in each_item['Instances']:
        print(each_instance['InstanceType'])
        print("-----------------------------------------------")

#list s3 bucket         

s3_con_cli=aws_mag_con.client("s3",region_name='ap-south-1')
s3_response=s3_con_cli.list_buckets()
Footer
