import configparser
import os
import pandas as pd
import boto3

##################################################################################################
#Constants Declaration
##################################################################################################
aws_credentials_path='aws_credentials'
aws_s3_bucket='streamlit-traffic-accidents'
LOCAL=True #Change this to FALSE for the Docker version

if LOCAL:
    data_folder ="./data/"
    img_folder = "./img/"
else:
    data_folder = "data/"
    img_folder = "img/"

##################################################################################################
#This function gets a data file and returns its content
##################################################################################################
def get_file(filename):
    path= data_folder+filename
    if not LOCAL:
        s3_session = get_aws_s3_connection()
        obj = s3_session.get_object(Bucket=aws_s3_bucket, Key=path)
        return obj['Body']
    else:
        return path

##################################################################################################
#This function gets a JSON file and returns its content
##################################################################################################
def get_json_file(filename):
    path = data_folder + filename
    if not LOCAL:
        s3_session = get_aws_s3_connection()
        obj = s3_session.get_object(Bucket=aws_s3_bucket, Key=path)
        return obj['Body']
    else:
        json_file = open(path, 'r')
        return json_file

##################################################################################################
#This function gets an image file and returns the picture
##################################################################################################
def get_image(filename):
        path = img_folder + filename

        if not LOCAL:
            s3_session = get_aws_s3_connection()
            obj = s3_session.get_object(Bucket=aws_s3_bucket, Key=path)
            return obj['Body'].read()
        else:
            return path

##################################################################################################
#This function is responsible to make the S3 connection from the App
##################################################################################################
def get_aws_s3_connection():
    #If the credentials file is not found we assume we are in a container inside the cloud so we try to call S3 directly with no credentials.
    if os.path.exists(aws_credentials_path):
        # Load the configuration file
        config = configparser.ConfigParser()
        config.read(aws_credentials_path)

        # Extract AWS credentials
        aws_access_key_id = config.get('default', 'aws_access_key_id')
        aws_secret_access_key = config.get('default', 'aws_secret_access_key')
        aws_session_token = config.get('default', 'aws_session_token')

        return boto3.session.Session(
                region_name="us-east-1",
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token
                ).client('s3')
    else:
        return boto3.client('s3')