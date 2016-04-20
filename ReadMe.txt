
=====|||===== Read Me =====|||=====


>> Software requirements
	1. Python 2.7
	2. Boto 2.38


>> Before executing the script :
	If the instance has IAM role, 
		Skip the Access key and Secret access key field. Add the Region Name (eg. us-east-1 for North Virginia) ARN of SNS topic in config.py file.
	Else, 
		Add the Access Key and Secret access key along with the Region Name (eg. us-east-1 for North Virginia) and SNS topic ARN in the config.py file.


>> To execute the script :
	$ python check_tag_script.py


>> Crontab Entry :
	*/5  *  *  *  *  /path/to/script/check_tag_script.py


>> How script works :
	The EC2 instances must have following three tags,
	1) Name
	2) Owner
	3) Application

	The Key or value of the tags are Not Case Sensitive.
	Note : The tag, “Application-name” is not same as “Application”.
		The tags must be “name”, “owner”, “application”.

>> If the EC2 instance does not have one or more tags from above list, it will be stopped without any warning message.

>> The log file (check_tag_logs.log) will be created in same directory from where script is being executed.

