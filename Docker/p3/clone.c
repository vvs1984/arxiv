#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <sched.h>
#include <sys/wait.h>
#include <errno.h>

#define STACKSIZE (1024*1024)

static char child_stack[STACKSIZE];

struct clone_args {
	char **argv;
};


static int child_exec(void *stuff)
{
		struct clone_args *args = (struct clone_args *)stuff;
		
		
		//mounr proc		
		if (umount("/proc", 0) != 0){			
			fprintf(stderr, "filed  to mount /proc %s\n", 
			strerror(errno));
			exit(-1);
			}

		if (mount("proc", "/proc", "proc", 0, "") != 0){			
			fprintf(stderr, "filed  to mount /proc %s\n", 
			strerror(errno));
			exit(-1);
			}

/*
		//sethostname
		const char * new_hostname = "containersrule";
		if (sethostname(new_hostname, strlen(new_hostname)) != 0 ){
			fprintf(stderr, "filed  to execvp %s\n", 
			strerror(errno));
			exit(-1);			
		}
*/	
		
		if (execvp(args->argv[0], args->argv) !=0) {
			fprintf(stderr, "filed  to execvp %s\n", 
			strerror(errno));
			exit(-1);

		}
		exit(EXIT_FAILURE);
}

int main(int argc, char **argv)
{
	struct clone_args args;
	args.argv = &argv[1];
	
//	int clone_flags = CLONE_NEWUSER |CLONE_NEWPID | CLONE_NEWIPC | CLONE_NEWUTS | CLONE_NEWNET | SIGCHLD;
	int clone_flags = CLONE_NEWPID | CLONE_NEWNS | SIGCHLD;
	//result of this call is that our child_exec will be run in another process 
	pid_t pid = clone(child_exec, child_stack + STACKSIZE, clone_flags, &args);
	
	if(pid < 0) {
		fprintf(stderr, "clone filed %s\n", 
		strerror(errno));
		exit(EXIT_FAILURE);
	};
	
	if (waitpid(pid, NULL, 0) == -1) {
		fprintf(stderr, "filed to whait pid %d\n", 
		pid);
		exit(EXIT_FAILURE);
		
	}
	exit(EXIT_SUCCESS);
}





