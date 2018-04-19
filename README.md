# Imlab-aws_security_group_IP_info
This script is used to fetch source information of IP address for security groups


## Prerequisites
+  [Python 2.7+](http://www.python.org/download/)

## Installation
```bash 
git clone https://github.com/jiamaozheng/fetch-aws-security-group-IP-info.git
``` 

## Command Line Parameters 
  Argument              |  Abbre  | Required | Default  | Description  
  ----------------------| ------- | -------- | -------- | ------------------------
  --bucket_path         |  -b     |   No     |  'b'     | a s3 bucket/folder you choosen to store output
  --output_path         |  -o     |   No     |  'o'     | a directory you choosen to store output
  --log_path            |  -l     |   No     |  'l'     | a directory you choosen to store log

## Run  
**Example 1: all settings by default (Recommended)**
 ```bash 
 python Imlab_aws_security_group_IP_info.py
 ``` 

**Example 2: To save output to user-defined path or s3 bucket**
 ```bash 
 python Imlab_aws_security_group_IP_info.py -o <user-defined path> 
 python Imlab_aws_security_group_IP_info.py -b <s3 bucket/folder> 
 ``` 

 **Example 3: To store log to user-defined path**
 ```bash 
  python Imlab_aws_security_group_IP_info.py -l <user-defined path> 
 ``` 
