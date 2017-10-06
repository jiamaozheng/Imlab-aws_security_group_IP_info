#!/usr/bin/env python 

# this script is used to fetch source information of IP address from security groups on Im-lab AWS account

# reference: http://stackoverflow.com/questions/2543018/what-python-libraries-can-tell-me-approximate-location-and-time-zone-given-an-ip

import urllib2, boto3, json, pandas, time, os, sys, logging, argparse
from datetime import datetime
import uuid as myuuid
from botocore.exceptions import ClientError

__author__ = "Jiamao Zheng <jiamaoz@yahoo.com>"
__version__ = "Revision: 0.0.1"
__date__ = "Date: 2017-09-28"

class SecurityGroup(object):
    def __init_(self):
        # logger 
        self.logger = ' '

        # output path
        self.output_path = ''

        # log path 
        self.log_path = ''

    # Logging function 
    def getLog(self):
        log_file_name = ''
        if self.log_path != 'l':
            if self.log_path[-1] != '/':
                self.log_path = self.log_path + '/'
            log_file_name = self.log_path + str(myuuid.uuid4()) + '.log'
        else: 
            currentPath = os.path.abspath(os.path.abspath(sys.argv[0]))[:-35]
            currentPath = currentPath[:-(len(currentPath.split('/')[-2]) + 1)]
            log_file_name = currentPath + 'log/' + datetime.now().strftime('%Y-%m-%d')

            if not os.path.exists(log_file_name):
                os.makedirs(log_file_name)
            log_file_name = log_file_name + '/' + str(myuuid.uuid4()) + '.log'

        self.logger = logging.getLogger()
        fhandler = logging.FileHandler(filename=log_file_name, mode='w')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fhandler.setFormatter(formatter)
        self.logger.addHandler(fhandler)
        self.logger.setLevel(logging.INFO)

    # Funtion to get a pretty string for a given number of seconds.
    def timeString(self, seconds):
      tuple = time.gmtime(seconds);
      days = tuple[2] - 1;
      hours = tuple[3];
      mins = tuple[4];
      secs = tuple[5];
      if sum([days,hours,mins,secs]) == 0:
        return "<1s";
      else:
        string = str(days) + "d";
        string += ":" + str(hours) + "h";
        string += ":" + str(mins) + "m";
        string += ":" + str(secs) + "s";
      return string;

    # Get arguments 
    def get_args(self):
        # setup commond line arguments 
        parser = argparse.ArgumentParser()

        # output path 
        parser.add_argument('-o', '--output_path', required=False, default='o', type=str, help='a directory path you choosen to save output')

        # log path 
        parser.add_argument('-l', '--log_path', required=False, default='l', type=str, help='a directory path you choosen to store log')

        # parse the arguments 
        args = parser.parse_args()
        self.output_path = args.output_path.strip()
        self.log_path = args.log_path.strip()

        if self.output_path != 'o' and not os.path.exists(self.output_path):
            os.makedirs(self.output_path) 
        if self.log_path != 'l' and not os.path.exists(self.log_path):
            os.makedirs(self.log_path)      

    def find_aws_security_group_ip_information(self): 
        # set up all variables 
        security_group_ip_sources = pandas.DataFrame()
        groups_descriptions = []
        groups_names = []
        groups_ids = []
        citys = []
        states = []
        country_names = []
        zip_codes = []
        ip_addresses = []
        start_time = time.time() 


        # fetch all security group information using boto3, return type is dict 
        ec2 = boto3.client('ec2')
        sg = ec2.describe_security_groups()
        security_groups = sg['SecurityGroups']

        # for loop through all security groups 
        if len(security_groups) > 0: 
            for i in range(len(security_groups)):
                if len(security_groups[i]['IpPermissions']): 

                    # get ip lists 
                    for k in range(len(security_groups[i]['IpPermissions'])): 
                        ip_lists = security_groups[i]['IpPermissions'][k]['IpRanges']
                        security_groups_description = security_groups[i]['Description']
                        group_name = security_groups[i]['GroupName']
                        group_id = security_groups[i]['GroupId']
                        ip_lists = security_groups[i]['IpPermissions'][k]['IpRanges']

                        # loop through all ip addresses 
                        if len(ip_lists) > 0: 
                            msg = '\nFind associated IP address for security group ' + security_groups[i]['GroupId'] +': ' # calculate how long the program is running
                            self.logger.info(msg)
                            print(msg) 

                            for k in range(len(ip_lists)):

                                # get ip address 
                                ip = ip_lists[k]['CidrIp'].split('/')[0]

                                msg = "   %s" % ip
                                self.logger.info(msg)
                                print(msg) 

                                # fetch ip address information 
                                try: 
                                    url = 'http://freegeoip.net/json/'
                                    url = url + ip 
                                    url = url.strip()
                                    req = urllib2.Request(url, headers = {'Content-Type': 'application/json'})
                                    out = urllib2.urlopen(req)
                                    location = json.loads(out.read())
                                except urllib2.URLError, err:
                                    msg = err.reason
                                    self.logger.info(msg)
                                    print(msg) 
                                finally:
                                    try:
                                        out.close()
                                    except NameError: 
                                        pass
                               
                                # insert fetched information into lists 
                                groups_descriptions.append(security_groups_description)
                                groups_names.append(group_name)
                                groups_ids.append(group_id)
                                citys.append(location['city'])
                                states.append(location['region_name'])
                                ip_addresses.append(location['ip'])
                                zip_codes.append(location['zip_code']) 
                                country_names.append (location['country_name'])
                        else: 
                            msg = 'no associated IP addresses for security group ' + security_groups[i]['IpPermissions'][k]['UserIdGroupPairs'][0]['GroupId'] + '!'
                            self.logger.info(msg)
                            print(msg) 

                            no_data = '' 
                            groups_descriptions.append(security_groups_description)
                            groups_names.append(group_name)
                            groups_ids.append(group_id)
                            citys.append(no_data)
                            states.append(no_data)
                            ip_addresses.append(no_data)
                            zip_codes.append(no_data) 
                            country_names.append (no_data)

        else: 
            msg = 'no security group, please create one!'
            self.logger.info(msg)
            print(msg) 

        # convert list to data.frame 
        groups_description_pd = pandas.DataFrame(groups_descriptions, columns =['security_group_description'])
        groups_name_pd = pandas.DataFrame(groups_names, columns=['group_name'])
        groups_id_pd = pandas.DataFrame(groups_ids, columns=['group_id'])
        ips_pd = pandas.DataFrame(ip_addresses, columns=['ip_address'])
        citys_pd = pandas.DataFrame(citys, columns=['city'])
        states_pd = pandas.DataFrame(states, columns =['state'])
        country_name_pd = pandas.DataFrame(country_names, columns=['country_name'])
        zip_pd = pandas.DataFrame(zip_codes, columns = ['zip_code'])

        # union them together 
        security_groups = pandas.DataFrame()
        security_groups =pandas.concat([groups_name_pd, groups_id_pd, groups_description_pd, ips_pd, citys_pd, states_pd, country_name_pd, zip_pd], axis = 1)

        # security_groups = pandas.DataFrame({'security_group_description': groups, 'ip_address': ip_addresses, 'city': citys, 
        #     'state':states, 'country_name': country_names, 'zip_code': zip_codes})

        # write data to files in csv and html format 
        id = str(myuuid.uuid4())
        find_ip_time = datetime.now().strftime('%Y-%m-%d') 

        result_path = ''
        if self.output_path == 'o':
            result_path = '../output/Im_lab_AWS_security_groups_ip_info-' + id + '-' + find_ip_time  
             # create a new directory for hosting data 
            # os.chdir(result_path)
        else:
            if self.output_path[-1] != '/':
                self.output_path = self.output_path + '/'
            result_path = self.output_path + 'Im_lab_AWS_security_groups_ip_info-' + id + '-' + find_ip_time

        os.makedirs(result_path) 
        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pandas.ExcelWriter(result_path + '/Im_lab_AWS_security_groups_ip_info-' + id + '-' + find_ip_time + '.xlsx', engine='xlsxwriter')

        # Convert the dataframe to an XlsxWriter Excel object.
        security_groups.to_excel(writer, sheet_name='Sheet1', index = None)

        # Close the Pandas Excel writer and output the Excel file.
        writer.save()

        # security_groups.to_csv('Im_lab_AWS_security_groups_ip_info-' + id + '-' + find_ip_time + '.csv' , index = None)
        # security_groups.to_html('Im_lab_AWS_security_groups_ip_info-' + id + '-' + find_ip_time + '.html' , index = None)

def main():
    # Instantial class
    start_time = time.time() 
    securityGroup = SecurityGroup()
    securityGroup.get_args()
    securityGroup.getLog()

    # run find_aws_security_group_ip_information function
    securityGroup.find_aws_security_group_ip_information()

    msg = "\nElapsed Time: " + securityGroup.timeString(time.time() - start_time) # calculate how long the program is running
    securityGroup.logger.info(msg)
    print(msg) 

    msg = "\nDate: " + datetime.now().strftime('%Y-%m-%d') + "\n"
    securityGroup.logger.info(msg)
    print(msg)   

# INITIALIZE
if __name__ == '__main__':
    sys.exit(main())

