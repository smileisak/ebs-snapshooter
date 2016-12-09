# EBS-SnapShooter

EBS-SnapShooter is a python script based on [boto2], that creates daily, weekly on monthly snapshots for all your aws ebs volumes.

### Requirements:

* [boto2] - Python package that provides interfaces to Amazon Web Services

To install requirements :
```
(env)$ pip install -r requirements.txt
```

And of course EBS-Snapshooter itself is open source on GitHub.

### How to run

*  Edit ebs-snpshooter.py file with your aws api creadentials 

```aws_access_key = "****"
aws_secret_key = "****"
ec2_region_name = "eu-west-1"
ec2_region_endpoint = "ec2.eu-west-1.amazonaws.com"
sns_arn = "arn:aws:sns:eu-west-1:******:EBS_Snapshots"
```

* And just run the script ebs-snpshooter.py

License
----
**Free Software, Hell Yeah!**

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [boto2]: <https://github.com/boto/boto>
