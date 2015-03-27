# jira\_daily_report
Create and send tables of JIRA usage for last 24HR via Email.

## Description
This script will create HTML format report for last 24 hours and send the report via Email. The report contains "Created", "Created but not resolved", "Have updated", and "Have resolved".
This script is used for JIRA Cloud version, and did not test for JIRA Server version .

## Setup
1. Modify "domainName" to the domain name of your JIRA Cloud.
* Modify mailing settings: "mailServer", "mailFrom", and "mailList".
* Modify "authStr", the string after "Basic" is encoded using Base64 from string "YourUsername:YourPassword".  
	example: 'YWFhOmFiYw==' is encoded 'aaa:abc'.
* Then you can add cron job to run this script everyday.

## Usage
No arguments needed, just type script name to execute.
