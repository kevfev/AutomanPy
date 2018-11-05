# AutomanPy
Python bindings for AutoMan. See [AutoMan](https://automan-lang.github.io/). 
This package is currently in development.

## Getting Started
Currently, only Amazon Mechanical Turk is supported for crowdsourcing tasks.
#### 1) Register for an Amazon AWS account
##### 1) a) Delete your root key and make an IAM user. Ensure that the IAM user has all Mechanical Turk privileges 
##### 1) b) Note the access ID and access key for your IAM user, this will be used for the Automan adapter credentials.
#### 2) Register for a Amazon Mechanical Turk (MTurk) Requester account
#### 3) Link your AWS and MTurk accounts in the MTurk account settings
#### 4) Sign up for MTurk Developer account (need to do separate registration, sign up for both requester and worker accounts, both useful for testing)
#### 5) Try using the example code and replace the credential fields. BE SURE TO TEST POSTING TO DEVELOPMENT SANDBOX FIRST!
