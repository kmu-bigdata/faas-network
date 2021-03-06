import boto3
import random
import time

s3_client = boto3.client('s3')
dynamodb = boto3.client('dynamodb')

# NETWORK INDEX
recv_index = 0
send_index = 8

# VM IDENTIFIER INDEX
model_name_index = 4
value_index = 1


def s3_object_download(bucket, key):
    start = time()
    s3_response_object = s3_client.get_object(Bucket=bucket, Key=key)
    print(s3_response_object['ContentLength'])
    object_content = s3_response_object['Body'].read()
    latency = time() - start
    return latency


def get_network_bandwidth():
    with open('/proc/net/dev', 'r') as dev:
        lines = dev.readlines()
        for line in lines:
            if 'vinternal' in str(line):
                line = line.split(' ')
                info = filter(str.isdigit, line)
                recv = int(info[recv_index])
                send = int(info[send_index])
                return recv, send


def get_vm_id():
    buf = open('/proc/self/cgroup').read().split('\n')[-3].split('/')
    vm_id, c_id = buf[1], buf[2]
    return vm_id, c_id


def lambda_handler(event, context):
    bucket = event['bucket']
    key = event['key']

    r_id, c_id = get_vm_id()

    s_recv, s_send = get_network_bandwidth()

    latency = s3_object_download(bucket, key)
    print('latency : {}'.format(latency))

    e_recv, e_send = get_network_bandwidth()

    recv_per_sec = (e_recv - s_recv) / (1024 ** 2) / latency
    send_per_sec = (e_send - s_send) / (1024 ** 2) / latency
    print('send-packets/s : {} MB/s recv-packets/s : {} MB/s'.format(send_per_sec, recv_per_sec))

    """
    DynamoDB Table
     - partition key -> r_id(String)
     - sort_key -> timestamp(Number)
    """
    dynamodb.put_item(TableName='[YOUR_DYNAMODB_TABLE_NAME]',
        Item={
             'r_id': {'S': r_id},
             'c_id': {'S': c_id},
             'timestamp': {'N': str(int(time() + random.randrange(1, 100)))},
             'lambda_mem_limit': {'S': context.memory_limit_in_mb},
             'latency': {'S': str(latency)},
             'send_per_sec': {'S': str(send_per_sec)},
             'recv_per_sec': {'S': str(recv_per_sec)}
        }
    )
