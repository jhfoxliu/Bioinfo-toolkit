import sjm_tools
import sys,argparse,time

def main():
	Usage = \
"""qsjm - running a sjm job in a single cmd
Usage: qsjm [options] <cmd>
	"""
	parser = argparse.ArgumentParser(prog="qsjm",usage=Usage) #,fromfile_prefix_chars='@',formatter_class=argparse.RawTextHelpFormatter
	options = parser.add_argument_group("Optional")
	options.add_argument("-n","--name",dest="job_name",type=str,default="qsjm",help="job name")
	options.add_argument("-m",dest="memory",type=str,default="10G",help="Memory size, default=10G")
	options.add_argument("-l",dest="log_dir",type=str,default="./",help="Log directory, default=./")
	options.add_argument("--no-submit",dest="no_submit",default=False,action="store_true",help="Do not submit the job")
	# args = parser.parse_args()
	opt,args = parser.parse_known_args()
	if len(args) > 0:
		cmd = " ".join(args)
		sys.stderr.write("CMD: %s\n" % cmd)
		
		SJM = str(time.time()) + ".sjm"
		workpath = "./"
		JOB = sjm_tools.job(workpath,SJM)
		JOB.step_start(step_name=opt.job_name,memory=opt.memory)
		JOB.add_process(cmd)
		JOB.step_end()
		if opt.log_dir:
			JOB.job_finish(log_dir=opt.log_dir)
		else:
			JOB.job_finish(log_dir="./")
		if opt.no_submit == False:
			JOB.submit()
	else:
		sys.stderr.write(Usage+"\n")
	
if __name__ == "__main__":
	main()
