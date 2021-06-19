# Assisted Bare Metal CLI

### Background

There are many ways to get started with Openshift. One of the option is the new Assisted Bare Metal installer which will generate the ISO for you and will automate the full process. Since this portal is evolving very fast to provides a good experience to the end users, some features may be temporarely disabled for quality control. This is the case with the User Managed Network option which may be required for some users. 

Warnings
- This tool is NOT supported in anyway.
- This tool will simply create a draft cluster in the assisted installer
- The draft cluster will be configured with User Managed Network option enabled
- It is your responsability to follow the Openshift documentation to setup your own VIP and DNS entries. 
- No validation of your network will be done. 

### Project

This small Python script uses the Assisted Bare Metal installer API to create a draft cluster with the Managed Network Option enabled. 

Some other features only available though the API may be added in the future.

Enjoy !