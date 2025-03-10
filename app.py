#!/usr/bin/env python3
import aws_cdk as cdk
from lib.mycompany_stack import MyCompanyStack

app = cdk.App()
MyCompanyStack(app, "MyCompanyStack", env=cdk.Environment(region="us-east-1"))
app.synth()
