#!/usr/bin/python
# coding=utf-8
# For Atlassian JIRA (Ondemand) to send usage report for last 24hr
# Created by Ming Wu <neowym@gmail.com>, 2014/10/16

import urllib
import urllib2
import json
import sys
import datetime

DEBUG = 0
apiURL = 'http://xxx.atlassian.net/rest/api/2/search'
baseURL = 'https://xxx.atlassian.net/browse/'

# mail options
mailServer = 'mail.abc.com.tw'
mailFrom = 'it@abc.com.tw'
mailList = [ 'aaa@abc.com.tw', 'bbb@abc.com.tw', ]

# encoded using Base64 "username:password"
authStr = 'Basic YWFhOmFiYw=='

period = '24h'
limits = 'startAt=0&fields=issuetype,summary,assignee,reporter,priority,status,resolution,created,updated'
qrystrs = {
	0: {    'name': 'Created',
					'qrystr': '%s&jql=created>=-%s+order+by+status+desc,created+desc' % ( limits, period ) },
	1: {    'name': 'Created but not resolved',
					'qrystr': '%s&jql=status=open+and+created>=-%s+order+by+status+desc,created+desc' % ( limits, period ) },
	2: {    'name': 'Have updated',
					'qrystr': '%s&jql=updated>=-%s+order+by+status+desc,created+desc' % ( limits, period ) },
	3: {    'name': 'Have resolved',
					'qrystr': '%s&jql=status=resolved+and+updated>=-%s+order+by+status+desc,created+desc' % ( limits, period ) }
}

def main():
	now = datetime.datetime.today()
	yesterday = now - datetime.timedelta(minutes=59, hours=23)
	mailtitle = 'JIRA Daily Report %s' % now.strftime('%Y/%m/%d')
	mailtext = '<HTML><HEAD><META HTTP-EQUIV=Content-Type CONTENT="text/html; charset=utf-8"><STYLE><!-- table { width:900.0pt; border-collapse:collapse; }  td { border:solid black 1.0pt;padding:0cm 1.4pt 0cm 1.4pt; border-top:none; } th { border:solid black 1.0pt;padding:0cm 1.4pt 0cm 1.4pt; border-top:none; } --></STYLE></HEAD><BODY>Dear All,<BR><BR>The Daily Report is below(%s to %s)<BR><BR>' % ( yesterday.strftime('%Y/%m/%d %H:%M'), now.strftime('%Y/%m/%d %H:%M') )
	for i in range(0,len(qrystrs)):
		mailtext += '%d. %s<BR>' % ( i+1, qrystrs[i]['name'] )
		curtime = datetime.datetime.today()
		if DEBUG: print '%s. %s' % ( i, qrystrs[i]['name'] )
		headers = { 'Authorization': authStr, 'Content-Type': 'application/json' }
		try:
			req = urllib2.Request('%s?%s' % (apiURL, qrystrs[i]['qrystr']), headers=headers)
			r = urllib2.urlopen(req)
		except urllib2.HTTPError as e:
			print e.code
			print e.read()
			continue
		result = r.read()
		if DEBUG: print result
		mailtext += format_output( result, curtime.strftime('%d/%b/%y %I:%M %p') )
		if DEBUG: print
	mailtext += 'Best Regards,<BR>IT Department</BODY></HTML>'
	if DEBUG: print mailtext
	send_email( mailtitle, mailtext )

def format_output( json_str, curtime ):
	data = json.loads(json_str)
	if DEBUG: print 'Parseing %s issues' % data['total']
	output = '<TABLE BORDER=0 CELLSPACING=0 CELLPADDING=0><TR STYLE=\'height:15.6pt\'><TD COLSPAN=10 STYLE=\'width:900.0pt;height:15.6pt; border-top: solid black 1.0pt;\'>Displaying %s issues at %s </TD></TR>' % ( data['total'], curtime )
	output += '<TR STYLE=\'height:13.2pt\'><TH ALIGN=CENTER STYLE=\'width:72.0pt;\'><B>Issue Type</B></TH>'
	output += '<TH ALIGN=CENTER STYLE=\'width:55.0pt;\'><B>Key</B></TH>'
	output += '<TH ALIGN=CENTER STYLE=\'width:192.0pt;\'><B>Summary</B></TH>'
	output += '<TH ALIGN=CENTER STYLE=\'width:143.0pt;\'><B>Assignee</B></TH>'
	output += '<TH ALIGN=CENTER STYLE=\'width:70.0pt;\'><B>Reporter</B></TH>'
	output += '<TH ALIGN=CENTER STYLE=\'width:50.0pt;\'><B>Priority</B></TH>'
	output += '<TH ALIGN=CENTER STYLE=\'width:63.0pt;\'><B>Status</B></TH>'
	output += '<TH ALIGN=CENTER STYLE=\'width:70.0pt;\'><B>Resolution</B></TH>'
	output += '<TH ALIGN=CENTER STYLE=\'width:91.0pt;\'><B>Created</B></TH>'
	output += '<TH ALIGN=CENTER STYLE=\'width:91.0pt;\'><B>Updated</B></TH></TR>'
	for issue in data['issues']:
		if not issue['id']:
			continue
		if DEBUG: print 'Parse issue: %s' % issue['key']
		output += '<TR><TD>%s</TD><TD><A HREF="%s%s">%s</A></TD><TD>%s</TD><TD>%s</TD><TD>%s</TD><TD>%s</TD><TD>%s</TD>' % ( issue['fields']['issuetype']['name'], baseURL, issue['key'], issue['key'], issue['fields']['summary'], issue['fields']['assignee']['displayName'], issue['fields']['reporter']['displayName'], issue['fields']['priority']['name'], issue['fields']['status']['name'] )
		if issue['fields']['resolution']:
			output += '<TD>%s</TD>' % issue['fields']['resolution']['name']
		else:
			output += '<TD><I>Unresolved</I></TD>'
		output += '<TD ALIGN=RIGHT>%s</TD><TD ALIGN=RIGHT>%s</TD></TR>' % ( datetime.datetime.strptime(issue['fields']['created'], '%Y-%m-%dT%H:%M:%S.000+0800').strftime('%Y/%m/%d %H:%M'), datetime.datetime.strptime(issue['fields']['updated'], '%Y-%m-%dT%H:%M:%S.000+0800').strftime('%Y/%m/%d %H:%M') )
	output += '</TABLE><BR><BR>'
	return output

def send_email( title, mailmsg ):
	import smtplib
	from email.mime.text import MIMEText
	msg = MIMEText(mailmsg, "html", "utf-8")
	msg['Subject'] = title
	msg['From'] = mailFrom
	msg['To'] = ', '.join(mailList)
	s = smtplib.SMTP(mailServer)
	s.sendmail( mailFrom, mailList, msg.as_string() )
	s.quit()

if __name__ == '__main__':
	main()
