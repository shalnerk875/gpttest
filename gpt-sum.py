# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import openai
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
from datetime import date
import time
import feedparser


openai.api_key = "sk-*****************"

def get_summary(url):
	r = requests.get(url)
	soup = BeautifulSoup(r.text, 'html.parser')
	title = soup.find("title")
	title = re.sub(re.compile('<.*?>'), '', str(title))
	title.encode('utf-8')

	if "krebsonsecurity.com" in url:
		bodytext = soup.find("div", class_="entry-content")
	else:
		bodytext = soup.find("body")

	askbody = re.sub(re.compile('<.*?>'), '', str(bodytext))
	askbody = askbody.replace("\n", "")
	print(url)
	print(title)
	print(bodytext)
	if len(askbody) >= 4097:
		askbody = askbody[:4097]

	try:
		response = openai.ChatCompletion.create(
			model="gpt-3.5-turbo",
			messages=[
				{"role": "user", "content": "以下の文章を300文字程度に日本語で要約してください。" + askbody},
			]
		)
	except Exception as e:
		print('GPT Error: ', e)
		return ""

	summary = ""
	summary = summary + response["choices"][0]["message"]["content"]


	summary = "TITLE: " + title + "\n" + summary + "\n\n" + url + "\n\n"
	return (summary)

def send_email(subject, body):
	smtp_server = 'smtp.gmail.com'
	port = 587
	sender = '****@gmail.com'
	password = '**********'
	recipient = '****@gmail.com'

	msg = MIMEText(body, 'plain', 'utf-8')
	msg['Subject'] = subject
	msg['From'] = sender
	msg['To'] = recipient
	msg['Date'] = formatdate()

	try:
		smtpobj = smtplib.SMTP(smtp_server, port)
		smtpobj.ehlo()
		smtpobj.starttls()
		smtpobj.ehlo()
		smtpobj.login(sender, password)
		smtpobj.sendmail(sender, recipient, msg.as_string())
		smtpobj.close()
		print('Mail Send Success')
	except Exception as e:
		print('Mail Send Error: ', e)

def get_rss_feed(url):
	feed = feedparser.parse(url)
	return feed

def is_category_security(entry):
	if 'tags' in entry:
		for tag in entry.tags:
			if tag.term.lower() == 'security':
				return True
	return False


if __name__ == '__main__':


	with open('url.txt') as f:
		urls = f.read().splitlines()

	for url in urls:
		summary = summary + get_summary(url)
		time.sleep(5)

	subject = f"GPT Summary News: ({date.today().strftime('%Y/%m/%d')})"
	body = summary.encode('utf-8')
	send_email(subject, body)
