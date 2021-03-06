# Network in Serverless Cloud Function Service
## PUBLICATION
_Jeongchul Kim, Jungae Park and Kyungyong Lee, 'Network in Serverless Cloud Function Service',
[AMGCC 2019](http://htcaas.kisti.re.kr/wiki/index.php/AMGCC19), 06/2019 [pdf]()_

## iPerf3 experiment
iperf3 is widely used as a network micro-benchmark.
### EC2(iperf3 server)
 - Start your EC2 instance, Configure EC2 Network and Subnet(same Lambda functions)
 - Configure your Security Group(5201 port - iperf3 server default port)
 - Check your EC2 internal-ip (ex : 172.31.XX.XX)
 - Install iperf3 
   - $ sudo yum -y install iperf3
 - Server start
   - $ iperf3 -s 
 - If you want to multiple test(concurrent exeuction), executed this [code](https://github.com/kmu-bigdata/faas-network/blob/master/ec2/iperf3_server/restart_iperf_server.sh)

### Lambda(iperf3 client)
 - Check your Lambda VPC Permission AWSLambdaVPCAccessExecutionRole
 - Config your Lambda Network(VPC, Subnet)
 - Using iperf3 command, we can let a client (function run-time) work as either a data uploader (default option) or downloader (with -R oprtion).
 - Lambda code(single test) : [iperf3_client](https://github.com/kmu-bigdata/faas-network/tree/master/lambda/iperf3_client)
 - Lambda Invocation code(concurrent test) : [invoke_iperf3_concurrent_execution](https://github.com/kmu-bigdata/faas-network/blob/master/lambda/invoke_iperf3_concurrent_execution/lambda_function.py)
 - Lambda input : 
 ```json
 {
    "server_ip": [SERVER_IP],
    "server_port": [SERVER_PORT],
    "test_time": [NUMBER_OF_TEST_TIME],
    "reverse" : [REVERSE_OPTION] 
 }
 ```
### single test
<img src="https://user-images.githubusercontent.com/10591350/57977928-41614c00-7a3d-11e9-9692-99a66591ddbc.png" width="400">

### concurrent test
<img src="https://user-images.githubusercontent.com/10591350/57977954-c77d9280-7a3d-11e9-8962-be83320e7b6b.png" width="400">

## Realistic Scenario using Cloud Storage(S3)
Evaluation with iperf3 provides an easy way to investigate the network bandwidths available for a function run-time, but it does not represent a realistic scenario for data application that may downloading or uploadingof files from a shared block storage(S3).
To understand the network performance of FaaS under realistic scenario, we performed download and upload experiments using blocks of data.

<img src="https://user-images.githubusercontent.com/10591350/57977932-550cb280-7a3d-11e9-8baa-833b8e28d5c8.png" width="400">

### lambda s3 download
 - code : [s3_get_object_download_network_bandwidth](https://github.com/kmu-bigdata/faas-network/blob/master/lambda/s3_get_object_download_network_bandwidth/lambda_function.py)
 - Lambda input
```json
{
    "object": [S3_BUCKET_NAME],
    "key": [DOWNLOAD_OBJECT_KEY]
}
```
 ### lambda s3 download
 - code : [s3_put_object_upload_network_bandwidth](https://github.com/kmu-bigdata/faas-network/blob/master/lambda/s3_put_object_upload_network_bandwidth/lambda_function.py)
 - Lambda input
```json
{
    "src_object": [SOURCE_S3_BUCKET_NAME],
    "dst_object": [DESTINATION_S3_BUCKET_NAME],
    "key": [UPLOAD_OBJECT_KEY]
}
```

## Concurrent execution using EC2 Docker
<img src="https://user-images.githubusercontent.com/10591350/57978265-a4a2ac80-7a44-11e9-8b99-cd40f5fe9e8d.png" width="400">

### EC2 setup
- Start your EC2 instance
- Install Docker 
  - $ sudo yum -y install docker
  - $ sudo service docker start
  - $ sudo usermod -aG docker ec2-user
- Start Network Orchestrator
  1. Copy [downloader](https://github.com/kmu-bigdata/faas-network/blob/master/ec2/network_orchestrator/download.js) and [uploader](https://github.com/kmu-bigdata/faas-network/blob/master/ec2/network_orchestrator/upload.js) to tmp filesystem(/tmp/)
  2. Start [orchestrator](https://github.com/kmu-bigdata/faas-network/blob/master/ec2/network_orchestrator/orchestrator.js) $ node orchestrator.js
  3. Start [driver](https://github.com/kmu-bigdata/faas-network/blob/master/ec2/network_orchestrator/driver.js) $ node driver.js [NUMBER_OF_DOWNLOADER_CONTAINER] [NUMBER_OF_FILE]
  