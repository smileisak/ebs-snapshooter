
# EBS-SnapShooter [![Build Status](https://travis-ci.org/smileisak/ebs-snapshooter.svg?branch=master)](https://travis-ci.org/smileisak/ebs-snapshooter) [![Docker Repository on Quay](https://quay.io/repository/smile/ebs-snapshooter/status "Docker Repository on Quay")](https://quay.io/repository/smile/ebs-snapshooter)


EBS-SnapShooter is a python script based on boto2, that creates daily, weekly or monthly snapshots for all your aws ebs volumes.

### Requirements:

* [boto2] - Python package that provides interfaces to Amazon Web Services

To install requirements :
```
(env)$ pip install -r requirements.txt
```

And of course EBS-Snapshooter itself is open source on GitHub.

### How to run
* Edit ebs-snpshooter.py file with your aws api creadentials 

* And just run the script ebs-snpshooter.py

```
export AWS_ACCESS_KEY=<aws-access-key> -e AWS_SECRET_KEY=<aws-secret-key> & python ebs-snapshooter.py
```

You can also run it within docker container. Go to --> https://quay.io/repository/smile/ebs-snapshooter

---
### Run it as Kubernetes Job:

To run it as a Kubernetes Job all you need is to base64 your secrets within `manifests/secrets.yaml`.
 Note that `aws-sns-arn` is optional if you want to create AWS SNS Notifications.

```yml
apiVersion: v1
type: Opaque
kind: Secret
metadata:
  name: ebs-snapshooter-seretes
data:
  aws-acces-key-id: <base64 encoded aws-access-key-id>
  aws-secret-acces-key: <base64 encoded aws-secret-acces-key>
  aws-sns-arn: <base64 encoded aws-sns-arn>
```

## License

EBS-SnapShooter is BSD-licensed.