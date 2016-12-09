from boto.ec2.connection import EC2Connection
from boto.ec2.regioninfo import RegionInfo
import boto.sns
from datetime import datetime
import time
import sys
import logging
# Message to return result via SNS
from boto.exception import EC2ResponseError

message = ""
errmsg = ""

# Counters
total_creates = 0
total_deletes = 0
count_errors = 0

# List with snapshots to delete
deletelist = []

# define period
period = "day"
date_suffix = datetime.today().strftime('%a')

# period = 'week'
# date_suffix = datetime.today().strftime('%U')

# period = 'month'
# date_suffix = datetime.today().strftime('%b')

# Setup logging
logging.basicConfig(filename="./EBS-Snapshot.log", level=logging.INFO)
start_message = 'Started taking %(period)s snapshots at %(date)s' % {
    'period': period,
    'date': datetime.today().strftime('%d-%m-%Y %H:%M:%S')
}
message += start_message + "\n\n"
logging.info(start_message)

# Get settings from config.py
aws_access_key = "****"
aws_secret_key = "****"
ec2_region_name = "eu-west-1"
ec2_region_endpoint = "ec2.eu-west-1.amazonaws.com"
sns_arn = "arn:aws:sns:eu-west-1:******:EBS_Snapshots"

region = RegionInfo(name=ec2_region_name, endpoint=ec2_region_endpoint)

# Number of snapshots to keep
keep_week = 3
keep_day = 3
keep_month = 1
count_success = 0
count_total = 0

# Connect to AWS using the credentials provided above or in Environment vars or using IAM role.
print 'Connecting to AWS'
if aws_access_key:
    conn = EC2Connection(aws_access_key, aws_secret_key, region=region)
else:
    conn = EC2Connection(region=region)

if sns_arn:
    print 'Connecting to SNS'
    if aws_access_key:
        sns = boto.sns.connect_to_region(ec2_region_name, aws_access_key_id=aws_access_key,
                                         aws_secret_access_key=aws_secret_key)
    else:
        sns = boto.sns.connect_to_region(ec2_region_name)


def get_resource_tags(resource_id):
    resource_tags = {}
    if resource_id:
        tags = conn.get_all_tags({'resource-id': resource_id})
        for tag in tags:
            # Tags starting with 'aws:' are reserved for internal use
            if not tag.name.startswith('aws:'):
                resource_tags[tag.name] = tag.value
    return resource_tags


def set_resource_tags(resource, tags):
    for tag_key, tag_value in tags.iteritems():
        if tag_key not in resource.tags or resource.tags[tag_key] != tag_value:
            print 'Tagging %(resource_id)s with [%(tag_key)s: %(tag_value)s]' % {
                'resource_id': resource.id,
                'tag_key': tag_key,
                'tag_value': tag_value
            }
            resource.add_tag(tag_key, tag_value)


def date_compare(snap1, snap2):
    if snap1.start_time < snap2.start_time:
        return -1
    elif snap1.start_time == snap2.start_time:
        return 0
    return 1


print 'Finding all volumes ...'
vols = conn.get_all_volumes()

ids_to_snapshots = {}
for vol in vols:
    ids_to_snapshots.setdefault(vol.id, []).append(vol.snapshots())


for vol in vols:
    try:
        count_total += 1
        logging.info(vol)
        tags_volume = get_resource_tags(vol.id)
        description = '%(period)s_snapshot %(vol_id)s_%(period)s_%(date_suffix)s by snapshot script at %(date)s' % {
            'period': period,
            'vol_id': vol.id,
            'date_suffix': date_suffix,
            'date': datetime.today().strftime('%d-%m-%Y %H:%M:%S')
        }
        # Creating snapshots
        try:
            current_snap = vol.create_snapshot(description)
            set_resource_tags(current_snap, tags_volume)
            suc_message = 'Snapshot created with description: %s and tags: %s' % (description, str(tags_volume))
            print '     ' + suc_message
            logging.info(suc_message)
            total_creates += 1
        except Exception, e:
            print "Unexpected error:", sys.exc_info()[0]
            logging.error(e)
            pass

        # Deleting old snapshots

        snapshots = vol.snapshots()
        deletelist = []
        for snap in snapshots:
            sndesc = snap.description
            if (sndesc.startswith('week_snapshot') and period == 'week'):
                deletelist.append(snap)
            elif (sndesc.startswith('day_snapshot') and period == 'day'):
                deletelist.append(snap)
            elif (sndesc.startswith('month_snapshot') and period == 'month'):
                deletelist.append(snap)
            else:
                logging.info('     Skipping, not added to deletelist: ' + sndesc)

        for snap in deletelist:
            logging.info(snap)
            logging.info(snap.start_time)

        deletelist.sort(date_compare)
        if period == 'day':
            keep = keep_day
        elif period == 'week':
            keep = keep_week
        elif period == 'month':
            keep = keep_month
        delta = len(deletelist) - keep
        for i in range(delta):
            del_message = '     Deleting snapshot ' + deletelist[i].description
            logging.info(del_message)
            try:
                logging.info('Deleting: ' + vol.id)
                deletelist[i].delete()
            except EC2ResponseError, e:
                pass
                logging.info(e.errors)
                total_deletes -= 2
            total_deletes += 1
        time.sleep(3)


    except:
        print "Unexpected error:", sys.exc_info()[0]
        logging.error('Error in processing volume with id: ' + vol.id)
        errmsg += 'Error in processing volume with id: ' + vol.id
        count_errors += 1
    else:
        count_success += 1

result = '\nFinished making snapshots at %(date)s with %(count_success)s snapshots of %(count_total)s possible.\n\n' % {
    'date': datetime.today().strftime('%d-%m-%Y %H:%M:%S'),
    'count_success': count_success,
    'count_total': count_total
}

message += result
message += "\nTotal snapshots created: " + str(total_creates)
message += "\nTotal snapshots errors: " + str(count_errors)
message += "\nTotal snapshots deleted: " + str(total_deletes) + "\n"

for key, value in ids_to_snapshots.items():
    message += "\n" + str(key) + " have " + str(len(value[0])) + " snapshots ==> " + "\n" \
                                                                             "Snapshot ids:  " + str(value[0]) + "\n"
print '\n' + message + '\n'
print result

# SNS reporting
if sns_arn:
    if errmsg:
        sns.publish(sns_arn, 'Error in processing volumes: ' + errmsg, 'Error with AWS Snapshot')
    sns.publish(sns_arn, message, 'Finished AWS snapshotting')

logging.info(result)
