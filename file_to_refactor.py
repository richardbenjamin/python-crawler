#!/usr/bin/env python
# encoding=utf8
from bs4 import BeautifulSoup
import ssl
import smtplib
import re
from time import localtime, strftime
import cgi
import cgitb
import sys 
import os
print('>>> ' + sys.version)
cgitb.enable()
from urllib.request import Request, urlopen
import pymysql
conn = pymysql.connect(
	host='localhost',
	user='root',
	password='password',
	db='s1',
	charset='utf8mb4',
	cursorclass=pymysql.cursors.DictCursor
)
a = conn.cursor()
a.execute('drop table if exists images')
a.execute('drop table if exists link_queue')
a.execute('drop table if exists submissions')

submission_table = '''CREATE TABLE IF NOT EXISTS submissions (
	`id` int auto_increment primary key,
	`title` varchar(255) not null,
	`url` varchar(255) not null,
	`html` longtext not null,
	`date` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
)'''

link_queue_table = '''
	CREATE TABLE IF NOT EXISTS link_queue (
	`id` int auto_increment,
	`url` varchar(255) not null unique,
	`text` varchar(255),
	`did` int not null,
	`date` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(id),
  FOREIGN KEY(did) REFERENCES submissions(id)
	)'''


image_table = '''
	CREATE TABLE IF NOT EXISTS images (
	`id` int auto_increment,
	`url` varchar(255) not null unique,
	`size` varchar(255) not null,
	`alt` varchar(255),
	`did` int not null,
	`date` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(id),
  FOREIGN KEY(did) REFERENCES submissions(id)
	)'''

a.execute(submission_table)
a.execute(link_queue_table)
a.execute(image_table)



# url
url1 = 'http://www.useragentstring.com/pages/useragentstring.php'
url = 'https://mattsatv.com'
url = re.sub(r"\/$",  '', url) # replace last slash
domain = re.sub(r"http:\/\/|https:\/\/|\/\/", '', url)
print(domain)
# sys.exit()

print('>>> url '  + url)
context = ssl._create_unverified_context()
ssl._create_default_https_context = ssl._create_unverified_context

agent1 = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
agent = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'

print('>>> user agent '  + agent)
headers={'User-Agent': agent}
response = Request(url, headers=headers)
html = urlopen(response).read().decode('utf8')
html_escaped = re.escape(html)
soup = BeautifulSoup(html, 'html.parser')

add_submission = '''
	INSERT INTO submissions (url, html)
	VALUES ("%s","%s")
'''


page_title = soup.title.string
add_submission2 = 'INSERT INTO submissions (title, url, html) VALUES ("'+page_title+'", "'+url+'", "'+html_escaped+'")'

print('>>> save page')
domain_id = a.execute(add_submission2)
domain_id = str(domain_id)
print(type(domain_id))
conn.commit()

# a.execute(add_submission, (url, html))
# conn.commit()






# Get Links
print('>>> get links')
links = []
for link in soup.find_all('a'):
	links.append(link.get('href'))

# print(links)
# print(links)
# 
links_to_exlcude = [
	'#',
	'#content',
	'tel:',
	'mailto:'
]

for link in links:
	domain_regex = '\/\/(?:[\w-]+\.)*([\w-]{1,63})(?:\.(?:\w{3}|\w{2}))'
	has_domain = re.search(domain_regex, link)

	# print(has_domain)
	if has_domain:
			link = re.sub(r"\/$",  '', link) # replace last slash
	else :
		link = re.sub(r"^\/",  '', link) # replace first slash
		link = url + '/' + link

	# print(link) # DEBUG

	if domain in link :
		try:
			add_link = 'INSERT INTO link_queue (`url`, `did`) VALUES ("'+link+'", "'+domain_id+'")'
			q = a.execute(add_link)
			conn.commit()
		except:
			'null'

# Get images
print('>>> get images')
images_to_exclude = [
	'facebook'
]
images = []
for image in soup.find_all('img'):
	images.append(image.get('src'))

for image_url in images:
	domain_regex = '\/\/(?:[\w-]+\.)*([\w-]{1,63})(?:\.(?:\w{3}|\w{2}))'
	has_domain = re.search(domain_regex, image_url)
	image_url = re.sub(r"^\/",  '', image_url) # replace first slash

	if not has_domain:
		image_url = url + '/' + image_url
	
	# response = Request(image_url, headers=headers)
	# imgdata = urlopen(response)
	# size = imgdata.headers.get("content-length")
	# size = float(size)/float(1000);
	size = 'unknown'

	# print(image_url)

	try:
		add_image = 'INSERT INTO images (url, size, did) VALUES ("'+image_url+'", "'+size+'", "'+domain_id+'")'
		a.execute(add_image)
		conn.commit()
	except:
		'null'

# End
extime = strftime("%a, %d %b %Y %H:%M:%S", localtime())
print('>>> Closing DB connection: ' + extime)


# print(soup.prettify())
# print(soup.title.string)
# print(soup.find('meta'))

# for link in soup.find_all('a'):
#     print(link.get('href'))
    # print(link)

# print(soup.get_text())

# file write example
## filename = 'test.html'
## target = open(filename, 'w')
## target.write('test')

