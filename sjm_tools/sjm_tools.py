import os,sys
import re
import sjm_tools

class job(object):
	def __init__(self,workpath=None,SJM=None,abspath=True):
		if abspath == True:
			workpath = os.path.abspath(workpath)
		if workpath is None:
			raise Warning("Please give a [workpath]!")
		if SJM is None:
			raise Warning("Please give a [SJM]!")
		if workpath.endswith("/") == False:
			workpath = workpath + "/"
		self.workpath = re.sub("/+","/",workpath)
		self.SJM_name = SJM
		self.SJM = open(SJM,'w') #file name
		self.steps = []
		self.orders = []
		self.step_number = 0
		self.step = None
		self.__doc__ = """ 
##The job class for job generation.
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
"""
	def step_start(self,step_name=None,directory=None,memory="10G",abspath=True,**kwargs):
		''' define a current job, if no directory given, use current directory '''
		if step_name is None:
			raise Warning("Please give a [step_name]!")
		if directory is not None:
			self.step = step(step_name,self.SJM,directory,memory=memory,abspath=abspath,kwargs=kwargs)
		elif self.workpath is not None:
			self.step = step(step_name,self.SJM,self.workpath,memory=memory,abspath=abspath,kwargs=kwargs)
		else:
			sys.stderr.write("Step [%s] without directory specified, use current directory." % step_name)
			self.step = step(step_name,self.SJM,os.getcwd()+"/",memory=memory,abspath=abspath,kwargs=kwargs)
			
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
		
	def submit(self,sjm="sjm"):
		''' submit the SJM file '''
		os.system("%s %s" % (sjm,self.SJM_name))
		sys.stderr.write("Job [%s] submitted.\n" % self.SJM_name)
		
	def delay(self,time=None):
		''' add a delay step into a step '''
		if time is None:
			raise Warning("When using delay(), please provide a certain time.")
		script_path = os.path.dirname(sjm_tools.__file__) + "/utils/sleep.py"
		self.SJM.write("python {sleep_script} {delay_time} ;\n".format(sleep_script=script_path,delay_time=time))
	
class step(object):
	def __init__(self,step_name,SJM,directory,memory=None,time=None,slots=None,exports=[],abspath=True,kwargs=None):
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