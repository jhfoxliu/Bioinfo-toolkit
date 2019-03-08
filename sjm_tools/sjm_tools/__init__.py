__all__ = ["sjm_tools"]

__name__ = "sjm_tools"

__doc__ = """
A module for quick deploy SJM submission.

Tutorial:

#import
from sjm_tools.sjm_tools import job

class job:
JOB = job(workpath,SJM) #workpath = which directory the files will in; SJM = SJM file name

Add job cycles:
JOB.step_start(step_name="QC")
JOB.add_process([Your cmd, string])
JOB.step_end()

When finished:
JOB.job_finish()

Submit:
JOB.submit()

Delay a step:
JOB.delay(time=[how long?]) #e.g. 10s 100min 1h 1hr

Add a delay process:
JOB.step_start(step_name="test")
JOB.delay_process(time=[how long?]) #e.g. 10s 100min 1h 1hr
JOB.step_end()
"""

__version__ = "0.0.2"

__author__ = "Jianheng Liu"

__time__ = "20180709"


import os,sys
import re
import sjm_tools
import random

class job(object):
	def __init__(self,workpath=None,SJM=None,abspath=True,SJM_path="sjm",bashrc="~/.bashrc"):
		if abspath == True:
			workpath = os.path.abspath(workpath)
		if workpath is None:
			raise Warning("Please give a [workpath]!")
		if SJM is None:
			raise Warning("Please give a [SJM]!")
		if workpath.endswith("/") == False:
			workpath = workpath + "/"
		self.workpath = re.sub("/+","/",workpath)
		self.bashrc = bashrc
		self.SJM_name = SJM
		self.SJM_path = SJM_path
		self.SJM = open(SJM,'w') #file name
		self.steps = []
		self.orders = []
		self.step_number = 0
		self.delays = 0
		self.step = None
		
		self.__doc__ = """ 
##The job class for job generation.

#To import this module:
import sjm_tools
#or
from sjm_tools import job

##To create a job:
JOB = job(workpath=workpath,SJM=SJM)

##To add a step:
JOB.step_start(step_name=step_name,directory=directory) #If no directory specified, use current directory
#Add prefix
JOB.add_prefix()
#Add a process
JOB.add_process()
#Add an end
JOB.add_end()

#When finish
JOB.job_finish()

#Submit
JOB.submit()

#A function used to validate environment is also provided, the function just return the input value
from sjm_tools import check_env 
env = check_env(env) #default: check if is a file
env = check_env(env, is_path=True) #check if is a path
env = check_env(env, is_prefix=True) #check if is a prefix
env = check_env(env, is_prefix=True,suffix=".txt") #check if files with the prefix and suffix
env = check_env(env, unknown=True) #check if is a file/path/prefix
"""
	def step_start(self,step_name=None,directory=None,memory="10G",abspath=True,your_bashrc=True,**kwargs):
		''' define a current job, if no directory given, use current directory '''
		if step_name is None:
			raise Warning("Please give a [step_name]!")
		if step_name in self.steps:
			raise Warning("\"%s\" repeated in [%s]" % (step_name, ",".join(self.steps)) )
		if directory is not None:
			self.step = step(self,step_name,self.SJM,directory,memory=memory,abspath=abspath,your_bashrc=your_bashrc,kwargs=kwargs)
		elif self.workpath is not None:
			self.step = step(self,step_name,self.SJM,self.workpath,memory=memory,abspath=abspath,your_bashrc=your_bashrc,kwargs=kwargs)
		else:
			sys.stderr.write("Step [%s] without directory specified, use current directory." % step_name)
			self.step = step(self,step_name,self.SJM,os.getcwd()+"/",memory=memory,abspath=abspath,your_bashrc=your_bashrc,kwargs=kwargs)
		
		self.step.add_prefix()
		self.orders.append(step_name)
		
	def add_process(self,string=None):
		if string is None:
			raise Warning("Please give a [string]!")
		self.step.add_process(string)
	
	def step_end(self):
		if self.step is not None:
			self.step.add_suffix()
			self.step_number += 1
			self.steps.append(self.step.step_name)
			self.step = None
		else:
			raise Warning("You have used step_end twice!!")
		
	def job_finish(self,log_dir=None,abspath=True):
		''' add orders, and log directory'''
		if len(self.steps) != self.step_number:
			raise Warning("Step number != steps buffer, some thing wrong!")
		if self.step_number == 0:
			raise Warning("No step within your file.")
		if self.step_number > 1:
			self.SJM.write("\n")
			for i in range(self.step_number-1):
				self.SJM.write("order %s before %s\n" % (self.steps[i],self.steps[i+1]))
		if log_dir is None:
			log_dir = self.workpath+"/logs/"
		if abspath == True:
			log_dir = os.path.abspath(log_dir)
		if os.path.isdir(log_dir) == False:
			os.mkdir(log_dir)
		self.SJM.write("\nlog_dir %s\n" % log_dir)
		self.SJM.close()
		
	def submit(self,sjm=None):
		''' submit the SJM file '''
		if sjm is None:
			sjm = self.SJM_path
		os.system("%s %s" % (sjm,self.SJM_name))
		sys.stderr.write("Job [%s] submitted.\n" % self.SJM_name)
	
	def delay(self,time="1min",rand=False,min_rand=10,max_rand=100):
		''' add a delay step to make resourse distrbution reasonable '''
		if rand == True:
			rand_time = random.randint(10,max_rand)
			time = str(rand_time)
		self.step_start(step_name="delay_"+str(self.delays+1))
		script_path = os.path.dirname(sjm_tools.__file__) + "/utils/sleep.py"
		self.SJM.write("python {sleep_script} {delay_time} ;\n".format(sleep_script=script_path,delay_time=time))
		self.step_end()
		self.delays += 1

	
	def delay_process(self,time=None,rand=False,min_rand=10,max_rand=100):
		''' add a delay process into a step '''
		if rand == True:
			rand_time = random.randint(10,max_rand)
			time = str(rand_time)
		if time is None:
			raise Warning("When using delay(), please provide a certain time.")
		script_path = os.path.dirname(sjm_tools.__file__) + "/utils/sleep.py"
		self.SJM.write("python {sleep_script} {delay_time} ;\n".format(sleep_script=script_path,delay_time=time))
	
class step(object):
	def __init__(self,parent,step_name,SJM,directory,memory=None,time=None,slots=None,exports=[],abspath=True,your_bashrc=True,kwargs=None):
		self.step_name = step_name
		self.memory = memory
		if abspath == True:
			directory = os.path.abspath(directory)
		if directory.endswith("/") == False:
			directory = directory + "/"
		self.directory = re.sub("/+","/",directory)
		self.SJM = SJM # file handle
		self.time = time
		self.slots = slots
		self.kwargs = kwargs
		self.exports = exports #a list of "A=B"
		if your_bashrc == True:
			self.bashrc = parent.bashrc
		else:
			self.bashrc = None
		
	def add_prefix(self):
		if os.path.isdir(self.directory) == False:
			os.mkdir(self.directory)
		self.SJM.write("job_begin\n")
		if self.step_name is not None:
			self.SJM.write(" name %s\n" % self.step_name)
		else:
			raise Warning("A step should have a name!")
		if self.time is not None:
			self.SJM.write(" time %s\n" % self.time)
		if self.memory is not None:
			self.SJM.write(" memory %s\n" % self.memory)
		if self.slots is not None:
			self.SJM.write(" slots %s\n" % self.slots)
		if self.exports:
			for item in exports:
				if re.search("^ export\s+",item):
					self.SJM.write(self.exports)
				elif re.search("^ export\s+",item):
					self.SJM.write(" "+self.exports)
				else:
					self.SJM.write(" export " + self.exports)
				if not re.search("\n\s+$",item) and not re.search("\n$",item):
					self.SJM.write("\n")
		if self.kwargs:
			for key,value in self.kwargs.items():
				self.SJM.write(" %s %s\n" % (str(key),str(value)))
		self.SJM.write(" directory %s\n" % self.directory)
		self.SJM.write(" cmd_begin\n")
		
		if self.bashrc is not None:
			self.SJM.write("source %s;\n" % self.bashrc)
	
	def add_suffix(self):
		self.SJM.write("cmd_end\njob_end\n\n")
		
	def add_process(self,string,auto_end=True):
		if auto_end == True:
			if re.search(";\s+\n$",string) or re.search(";\n$",string) or re.search(";\n\s+$",string) or re.search(";\s+\n\s+$",string):
				self.SJM.write(string)
			else:
				self.SJM.write(string+";\n")
		else:
			self.SJM.write(string)

def check_env(fn,is_prefix=False,is_path=False,unknown=False,exit=True,quiet=False,suffix=""):
	''' check if file/files exist '''
	if unknown == True:
		prefix = fn.split("/")[-1]
		path = "/".join(fn.split("/")[:-1])+"/"

		num_files = 0
		is_file = False
		is_path = False
		is_dir = False
		try:
			for files in os.listdir(path):
				if not suffix:
					if re.search("^%s" % prefix,files):
						num_files += 1
				else:
					if re.search("^%s[\s\S]*%s$" % (prefix,suffix),files):
						num_files += 1
		except OSError:
			pass
		if os.path.isfile(fn) == True:
			is_file = True
		if os.path.isdir(fn) == True:
			is_dir = True
		if is_file == True or is_dir == True:
			if fn.endswith("/"):
				if quiet == False:
					sys.stderr.write("\"%s\" validated. A folder named this found.\n" % fn)
			else:
				if quiet == False:
					sys.stderr.write("\"%s\" validated. A file named this found.\n" % fn)
		elif num_files > 0:
			if quiet == False:
				sys.stderr.write("\"%s\" validated. Files with this prefix found (%d).\n" % (fn,num_files))
		else:
			if exit:
				raise Warning("\"%s\" is not a file/folder/prefix!" % fn)
			else:
				sys.stderr.write("\"%s\" is neither a file/folder/prefix!\n" % fn)
	else:
		if is_prefix == True:
			prefix = fn.split("/")[-1]
			path = "/".join(fn.split("/")[:-1])+"/"
			num_files = 0
			for files in os.listdir(path):
				if not suffix:
					if re.search("^%s" % prefix,files):
						num_files += 1
				else:
					if re.search("^%s[\s\S]*%s$" % (prefix,suffix),files):
						num_files += 1
			if num_files == 0:
				if exit:
					raise Warning("\"%s\": no file with this prefix found!" % fn)
				else:
					sys.stderr.write("\"%s\": no file with this prefix found!" % fn)
			else:
				sys.stderr.write("\"%s\": passed. %d files with this prefix.\n" % (fn,num_files))
		elif is_path == True:
			if os.path.isdir(fn) == True:
				if quiet == False:
					sys.stderr.write("\"%s\" validated.\n" % fn)
			else:
				if exit:
					raise Warning("\"%s\" not exist!" % fn)
				else:
					sys.stderr.write("\"%s\" not exist!\n" % fn)
		else:
			if os.path.isfile(fn) == True:
				if quiet == False:
					sys.stderr.write("\"%s\" validated.\n" % fn)
			else:
				if exit:
					raise Warning("\"%s\" not exist!" % fn)
				else:
					sys.stderr.write("\"%s\" not exist!\n" % fn)
	return fn