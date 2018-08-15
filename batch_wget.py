import argparse
import multiprocessing
import sys
import subprocess
import time
import signal
from time import gmtime, strftime

def download_files(fn,url):
	log = url.split("/")[-1] + ".wget.log"
	if fn is None:
		child = subprocess.Popen("wget -c -o {log} -t 0 {url}".format(url=url,log=log),shell = True)
	else:
		child = subprocess.Popen("wget -c -o {log} -t 0 -O {fn} {url}".format(fn=fn,url=url,log=log),shell = True)
	sys.stderr.write("[%s] target: [%s], wget pid [%s]\n" % (strftime("%Y-%m-%d %H:%M:%S", time.localtime()),url,str(child.pid)))
	child.wait()

def parse_sra(sra):
	url = "ftp://ftp.ncbi.nlm.nih.gov/sra/sra-instant/reads/ByRun/sra/SRR/{SRR_3}/{SRR}/{SRR}.sra".format(SRR=sra,SRR_3=sra[0:6])
	return url
	
def signal_handler(sig,frame):
	pool.terminate()
	sys.exit()
	
if __name__ == "__main__":
	description = """Used to download files with wget
Input type:
list - name[tab]url
sra - sra_id
url - url
geo - [GEO query list]
"""
	parser = argparse.ArgumentParser(prog="m5C_caller_multiple",fromfile_prefix_chars='@',description=description,formatter_class=argparse.RawTextHelpFormatter)
	#Require
	group_required = parser.add_argument_group("Required")
	group_required.add_argument("-i","--input",dest="input",required=True,help="A list: name[tab]url")
	group_optional = parser.add_argument_group("Optional")
	group_optional.add_argument("-P","--processors",dest="processors",default=1,type=int,help="Processor number, default=1")
	group_optional.add_argument("--type",dest="type",default="list",choices=["list","sra","url","geo"],help="Input type")
	# group_optional.add_argument("--sra",dest="sra_ids",default=False,action="store_true",help="Lines are sra ids")
	# group_optional.add_argument("--sra",dest="sra_ids",default=False,action="store_true",help="Lines are sra ids")
	# group_optional.add_argument("-u","--url-only",dest="url_only",default=False,action="store_true",help="Lines only contains url")
	# group_optional.add_argument("--rename",dest="rename",default=False,action="store_true",help="Rename files")
	options = parser.parse_args()
	sys.stderr.write("[%s] Mission starts. CMD: %s\n" % (strftime("%Y-%m-%d %H:%M:%S", time.localtime())," ".join(sys.argv)))
	
	signal.signal(signal.SIGINT,signal_handler)
	pool = multiprocessing.Pool(options.processors)
	
	try:
		with open(options.input,'r') as input_list:
			if options.type != "geo":
				for line in input_list:
					if options.type == "list":
						line = line.strip().split("\t")
						fn, url = line
					elif options.type == "url":
						url = line.strip()
						fn = None
					elif options.type == "sra":
						url = parse_sra(line.strip())
						fn = None
					pool.apply_async(download_files,args=(fn,url,))
			else:
				line = input_list.readline() #header
				line = line.split("\t")
				idx = line.index("Run")
				fn = None
				for line in input_list.readlines():
					line = line.strip().split("\t")
					sra = line[idx]
					url = parse_sra(sra)
					pool.apply_async(download_files,args=(fn,url,))
		pool.close()
		pool.join()
	finally:
		pool.terminate()
	sys.stderr.write("[%s] All finished.\n" % strftime("%Y-%m-%d %H:%M:%S", time.localtime()))