#! /usr/bin/python
# -*- coding: utf-8 -*-

##################################################################################################
# Name         : check_tag_script.py
# Version      : 1.00
# Date Created : 18 Jan 2016
# Author       : Priti Jadhav
# Email        : priti.jadhav57@gmail.com
# Copyright    : Priti.jadhav57@gmail.com
#
# 
#
# Description : This script checks the tags associated with all the EC2 instances in given region.
#		If one or more tags are absent, instance will be stopped.
#
##################################################################################################




import boto.ec2
import boto.sns
import logging
import sys
from config import config
from logging.handlers import RotatingFileHandler




# ===|||=== variable declarations ===|||===

ACCESS_KEY_ID		= config['ACCESS_KEY'] 
SECRET_ACCESS_KEY_ID	= config['SECRET_KEY']
REGION			= config['REGION']
TOPIC			= config['SNS_TOPIC']
NO_TAG_INST		= []




# ===|||=== Logging setup ===|||===

# Initialize logger object with name CheckTagLogs
logger = logging.getLogger('CheckTagLogs')

# Logs will be stored in file, log_filename
log_filename = 'check_tag_logs.log'

# Initialize the file handler object, which will write to log file.
# It will rotae log file when its size is >= 5000 bytes.
# It will keep 2 backup files along with the current log file.
handler = RotatingFileHandler(log_filename, maxBytes=5000,
                                  backupCount=2)

# Logging level is set to Info
logger.setLevel(logging.INFO)

# Define the format in which logs will be stored in logfile.
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Data in handler will be written in format specified in 'formatter' variable.
handler.setFormatter(formatter)

# Add the handler object to logger object
logger.addHandler(handler)

# First message in logging file
#logger.info("\n")
logger.info("====|||==== Script execution started ====|||====")
#logger.info("\n")




def getConnSNS():	
    """ This method establishes connection with SNS service in REGION.
        
        Arguments       : None
        Return Value    : SNS connection object 

    """
    try:
        if ACCESS_KEY_ID =='' :
            logger.info("No Access key, trying using IAM Role.")
            conn_sns = boto.sns.connect_to_region(REGION)
            pass
        else:	
		regions = boto.sns.get_regions('sns')
		for reg in regions:
			if reg.name == REGION:
				region = reg
			else :
				pass
		conn_sns = boto.sns.SNSConnection(ACCESS_KEY_ID,SECRET_ACCESS_KEY_ID,region=region)
        return conn_sns
    except Exception, e:
        logger.info("In method getConnSNS, Except block !!!")
        logger.error(e)
	sys.exit(1)
    



def sendNotification(conn_sns):
    """ This method establishes connection with EC2 service in REGION.
        
        Arguments       : None
        Return Value    : EC2 connection object 

    """
	try:
		message = "One or more tags are missing, hence, stopping below instances :\n"
		inst_id_list = "\n".join(NO_TAG_INST)
		sns_msg = message + inst_id_list
		print "message for sns : ", sns_msg
		conn_sns.publish(topic=TOPIC,message = sns_msg, subject = 'Missing tags for EC2 instances',message_structure=None)
	except Exception, e:
        	logger.info("In method sendNotification, Except block !!!")
        	logger.error(e)
        	pass



def getConnEc2():
    """ This method establishes connection with EC2 service in REGION.
        
        Arguments       : None
        Return Value    : EC2 connection object 

    """

    try:
        if ACCESS_KEY_ID =='' :
            logger.info("No Access key, trying using IAM Role.")
            conn_ec2 = boto.ec2.connect_to_region(REGION)
            pass
        else:	
            region = boto.ec2.get_region(REGION)
            conn_ec2 = boto.ec2.EC2Connection(ACCESS_KEY_ID,SECRET_ACCESS_KEY_ID,region=region)
        return conn_ec2
    except Exception, e:
        logger.info("In method getConnEc2, Except block !!!")
        logger.error(e)
	sys.exit(1)
        pass




def getAllEc2(conn_ec2):
    """ This method fetches the list of all EC2 instances in REGION.
        and passes this list of EC2 instances to 'check_tag' method.

        Arguments       : EC2 connection Object 
        Return Value    : None

    """
    try:
        reservations = conn_ec2.get_all_instances()
        log_str = "Connection to region, "+ REGION + " is successful."
        logger.info(log_str)
        for reservation in reservations:
            for instance in reservation.instances:
                if (instance.state == 'running'):
                    all_tags=instance.tags
                    check_tag(instance.id,all_tags)
    except Exception, e:
        logger.info("In method getAllEc2, Except block !!!")
        logger.error(e)
        logger.info("Script Exiting with Errors !!!")
        sys.exit()
        pass




def check_tag(instance_id,all_tags):
    """ This function analyses the tags for each instance.
        If the instance does not have one or more tags,
        the instance Id is added to the list 'NO_TAG_INST'

        Arguments       : EC2 instance Id, Dictionary containing the tags associated with that EC2
        Return Value    : None

    """
    flag=0
    for tag in all_tags :
        if tag.lower().strip()=='name' :
            if all_tags[tag]=='' :
                print "no name tag"
            else :
                # If the tag is present, increment the flag value
                flag+=1
        elif tag.lower().strip()=='owner' :
            if all_tags[tag]=='':
                print "no owner tag"
            else :
                flag+=1
        elif tag.lower().strip()=='application' :
            if all_tags[tag]=='':
                print "no app tag"
            else :
                flag+=1
        else :
            # If the tag value is not Name, Owner or Application, donot do anything.
            continue

    # If one or more tags are missing, add the instance id to the list, 'NO_TAG_INST'
    if flag < 3 :
        NO_TAG_INST.append(instance_id)




def stopEc2(NO_TAG_INST,conn_ec2):
    """ This function stops the instances given in 'NO_TAG_INST' list.

        Arguments       : List of untagged instances, NO_TAG_INST, EC2 connection object.
        Return Value    : None

    """
    try:
        for i in NO_TAG_INST:
            conn_ec2.stop_instances(i)
            log_str = "One or more tags are missing for the instance, " + i 
            logger.info(log_str)
    except Exception, e:
        logger.info("In method stopEc2, Except block !!!")
        logger.error(e)
        pass




def init():
    # This is main function of the program. Execution starts here.

    #getConnEc2(ACCESS_KEY_ID,SECRET_ACCESS_KEY_ID,REGION)
    conn_ec2=getConnEc2()
    getAllEc2(conn_ec2)

    if NO_TAG_INST == [] :
    	# If all instances are tagged, print to log file and exit
        logger.info("Hurray !!! All instances are tagged.")
    else : 
    	# If there are instances that are not tagged properly, stop them using 'stopEc2' method.
        stopEc2(NO_TAG_INST,conn_ec2)
	conn_sns = getConnSNS()
	sendNotification(conn_sns)




# Start the Program Execution
init()
