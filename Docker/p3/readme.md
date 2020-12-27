
##Упражнение 3


Создайте свой собственный контейнер, который может запускать процессы через командную строку. Установите сетевое соединение между родительским пространством имен и дочерним пространством имен. Подключитесь к контейнеру через ssh и выполните команды ps -ax, pstree, top, ls и другие, чтобы выяснить, что происходит внутри. Результат (программу на С) загрузите на github.



##Отчёт о выполнении

Данное решение нельзя считать полным, так как не было произведено подключение по ssh, однако помогло получить представления о происходящих процессах внутри контейнера

###Изоляция сети
Запрос информации `ip a` о сетевых подключениях на опытном ПК даёт следующие результаты 
```
(base) vvs@vvs-System-Product-Name:~/1$ ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
2: enp3s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 20:cf:30:7f:89:9f brd ff:ff:ff:ff:ff:ff
    inet 192.168.1.64/24 brd 192.168.1.255 scope global dynamic noprefixroute enp3s0
       valid_lft 85660sec preferred_lft 85660sec
    inet6 fe80::2d0f:4bb8:8a24:11f2/64 scope link noprefixroute 
       valid_lft forever preferred_lft forever
3: docker0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default 
    link/ether 02:42:6a:7b:41:3d brd ff:ff:ff:ff:ff:ff
    inet 172.17.0.1/16 brd 172.17.255.255 scope global docker0
       valid_lft forever preferred_lft forever
    inet6 fe80::42:6aff:fe7b:413d/64 scope link 
       valid_lft forever preferred_lft forever
4: wlxd037455a586e: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
    link/ether d0:37:45:5a:58:6e brd ff:ff:ff:ff:ff:ff
42: veth7d50c36@if41: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master docker0 state UP group default 
    link/ether 1e:2f:69:1b:2c:6a brd ff:ff:ff:ff:ff:ff link-netnsid 0
    inet6 fe80::1c2f:69ff:fe1b:2c6a/64 scope link 
       valid_lft forever preferred_lft forever
(base) vvs@vvs-System-Product-Name:~/1$ 

```

Для исследования свойств изоляции сети была применена программа 

```
//код net CLONE_NEWNET


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
	
	int clone_flags = CLONE_NEWNET |SIGCHLD;
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

```

Результат выполения програмы для запроса о сетевых адаптерах внутри склонированного объекта  с флагом `CLONE_NEWNET`
```
(base) vvs@vvs-System-Product-Name:~/1$ sudo ./net ip a
[sudo] password for vvs: 
1: lo: <LOOPBACK> mtu 65536 qdisc noop state DOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
```

**Внутри клонированного объекта был создан свой сетевой адрес. Так как не осуществлялся проброс портов, то сетевые интерфесы ПК , на котором  запущенна программа, не видны.**




##Пространсотво имён (Linux)


[Пространство имён](https://ru.wikipedia.org/wiki/%D0%9F%D1%80%D0%BE%D1%81%D1%82%D1%80%D0%B0%D0%BD%D1%81%D1%82%D0%B2%D0%BE_%D0%B8%D0%BC%D1%91%D0%BD_(Linux)) (от англ. namespaces) — это функция ядра Linux, позволяющая изолировать и виртуализировать глобальные системные ресурсы множества процессов. Примеры ресурсов, которые можно виртуализировать: ID процессов, имена хостов, ID пользователей, доступ к сетям, межпроцессное взаимодействие и файловые системы. Одной из общих целей пространств имён является поддержка реализации контейнеров — инструмента для виртуализации на уровне операционной системы (а также других целей), обеспечивающего группу процессов иллюзией того, что они являются единственными процессами в системе. Поэтому одной из главных целей пространства имён является поддержка контейнеризации в Linux


### Изоляция в пространсотве  имён UTS (Unix Time Sharing) 	

Запрос информации `hostname`  о utsname тестового ПК 


```
(base) vvs@vvs-System-Product-Name:~/1$ hostname
vvs-System-Product-Name
```

Для исследования свойств изоляции сети была применена программа 



```
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

		//sethostname
		const char * new_hostname = "containersrule";
		if (sethostname(new_hostname, strlen(new_hostname)) != 0 ){
			fprintf(stderr, "filed  to execvp %s\n", 
			strerror(errno));
			exit(-1);			
		}
	
		
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
	
	int clone_flags = CLONE_NEWUTS |SIGCHLD;
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
```


Результат выполения програмы для запроса информации `hostname`  о utsname  внутри склонированного объекта  с флагом `CLONE_NEWUTS`


```
(base) vvs@vvs-System-Product-Name:~/1$ sudo ./utc hostname
containersrule
(base) vvs@vvs-System-Product-Name:~/1$ sudo unshare --uts -- /bin/bash -c 'hostname thing && hostname'
thing
(base) vvs@vvs-System-Product-Name:~/1$ hostname
vvs-System-Product-Name
```

**Внутри клонированного объекта был создано свое  utsname (в первом случае по умолчанию - `containersrule`, во втором, при использовании запроса unshare - `thing`) - пространство имён UTC на данный клонированный объект не  распространяется. И наоборот - пространство имён внутри клонированного объекта не распространяется наружу.**



### Изоляция в пространсотве  имён IPC (inter-process communication)

[Межпроцессное взаимодействие](https://ru.wikipedia.org/wiki/%D0%9C%D0%B5%D0%B6%D0%BF%D1%80%D0%BE%D1%86%D0%B5%D1%81%D1%81%D0%BD%D0%BE%D0%B5_%D0%B2%D0%B7%D0%B0%D0%B8%D0%BC%D0%BE%D0%B4%D0%B5%D0%B9%D1%81%D1%82%D0%B2%D0%B8%D0%B5) (англ. inter-process communication, IPC) — обмен данными между потоками одного или разных процессов. Реализуется посредством механизмов, предоставляемых ядром ОС или процессом, использующим механизмы ОС и реализующим новые возможности IPC. Может осуществляться как на одном компьютере, так и между несколькими компьютерами сети. 

Код программы для создания клонированного процесса без выделения своего простарнства имён IPC


```
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
	
	int clone_flags = SIGCHLD;
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
```

 
 
Запрос информации `ipcs -q`  на тестовом ПК при выполнении программы


```
(base) vvs@vvs-System-Product-Name:~/1$ gcc -o ipc -w clone.c
(base) vvs@vvs-System-Product-Name:~/1$ ./ipc ipcs -q

------ Message Queues --------
key        msqid      owner      perms      used-bytes   messages    
0x570bf831 0          root       644        0            0           

(base) vvs@vvs-System-Product-Name:~/1$ 
```

При выполнении тестовой программы установлен 1 поток обмена данными.


Код программы для создания клонированного процесса с выделением своего простарнства имён IPC


```
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
	
//	int clone_flags = CLONE_NEWPID | CLONE_NEWIPC | CLONE_NEWUTS | CLONE_NEWNET | SIGCHLD;
	int clone_flags = CLONE_NEWIPC | SIGCHLD;
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
```


Результат выполения програмы внутри склонированного объекта  с флагом `CLONE_NEWIPC`


```
(base) vvs@vvs-System-Product-Name:~/1$ sudo ./ipc ipcs -q
[sudo] password for vvs: 

------ Message Queues --------
key        msqid      owner      perms      used-bytes   messages    

(base) vvs@vvs-System-Product-Name:~/1$ 
```

**Внутри изолиорванного объекта не виден поток обмена, который был установлен снаружи.** 


### Изоляция пространства пользовательских имён


Запрос информации `ls -la` в пространстве имён тестового ПК

```
(base) vvs@vvs-System-Product-Name:~/1$ ls -la
total 212
drwxrwxr-x  2 vvs  vvs   4096 ноя 19 02:27 .
drwxr-xr-x 67 vvs  vvs   4096 ноя 19 02:33 ..
-rw-r--r--  1 root root     0 ноя 18 19:10 1.ann
-rw-r--r--  1 root root    29 ноя 18 19:10 1.txt
-rwxrwxr-x  1 vvs  vvs  17248 ноя 18 23:35 clone
-rw-rw-r--  1 vvs  vvs   1641 ноя 19 01:45 clone.c
-rwxrwxr-x  1 vvs  vvs  17088 ноя 19 00:30 ipc
-rw-rw-r--  1 vvs  vvs  21118 ноя 19 02:27 log
-rwxrwxr-x  1 vvs  vvs  17088 ноя 18 23:45 net
-rwxrwxr-x  1 vvs  vvs  16944 ноя 19 02:24 pid
-rw-rw-r--  1 vvs  vvs    476 ноя 19 02:23 pid.c
-rwxr-xr-x  1 root root 17160 ноя 19 01:44 pidn
-rwxrwxr-x  1 vvs  vvs  17160 ноя 19 01:38 pidnames
-rw-r--r--  1 root root    34 ноя 18 19:10 .stats_cache
-rw-r--r--  1 root root     0 ноя 18 18:41 swdwsf.ann
-rw-r--r--  1 root root    28 ноя 18 18:41 swdwsf.txt
-rwxrwxr-x  1 vvs  vvs  17088 ноя 19 00:41 unames
-rwxrwxr-x  1 vvs  vvs  17184 ноя 18 23:54 utc
```

Код программы для создания клонированного процесса с выделением своего простарнства пользовательских имён.

```
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
		
/*		
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
*/
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
	
//	int clone_flags = CLONE_NEWPID | CLONE_NEWIPC | CLONE_NEWUTS | CLONE_NEWNET | SIGCHLD;
	int clone_flags = CLONE_NEWUSER |SIGCHLD;
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
```


Результат выполения програмы с флагом `CLONE_NEWUSER`


```
(base) vvs@vvs-System-Product-Name:~/1$ gcc -o unames -w clone.c
(base) vvs@vvs-System-Product-Name:~/1$ sudo ./unames ls -la
total 124
drwxrwxr-x  2 nobody nogroup  4096 ноя 19 00:41 .
drwxr-xr-x 67 nobody nogroup  4096 ноя 18 20:11 ..
-rw-r--r--  1 nobody nogroup     0 ноя 18 19:10 1.ann
-rw-r--r--  1 nobody nogroup    29 ноя 18 19:10 1.txt
-rwxrwxr-x  1 nobody nogroup 17248 ноя 18 23:35 clone
-rw-rw-r--  1 nobody nogroup  1616 ноя 19 00:41 clone.c
-rwxrwxr-x  1 nobody nogroup 17088 ноя 19 00:30 ipc
-rwxrwxr-x  1 nobody nogroup 17088 ноя 18 23:45 net
-rw-r--r--  1 nobody nogroup    34 ноя 18 19:10 .stats_cache
-rw-r--r--  1 nobody nogroup     0 ноя 18 18:41 swdwsf.ann
-rw-r--r--  1 nobody nogroup    28 ноя 18 18:41 swdwsf.txt
-rwxrwxr-x  1 nobody nogroup 17088 ноя 19 00:41 unames
-rwxrwxr-x  1 nobody nogroup 17184 ноя 18 23:54 utc
(base) vvs@vvs-System-Product-Name:~/1$ 
```

**Так как внутри клониорванного объекта было создано своё пространство пользовательских имён, то при запросе информации о владельцах файлов и рабочих групп изнутри программы  получен результат `nobody nogroup` - внитри клонированного обьекта нет доступа к этой информации**


### Изоляция пространства процессов (PID)


Для исследования свойств пространства процессов была применена программа 

```
#define _GNU_SOURCE
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <unistd.h>

static char child_stack[1048576];

static int child_fn() {
  printf("PID: %ld\n", (long)getpid());
  printf("Parent PID: %ld\n", (long)getppid());
  return 0;
}

int main() {
  pid_t child_pid = clone(child_fn, child_stack+1048576, CLONE_NEWPID | SIGCHLD, NULL);
  printf("clone() = %ld\n", (long)child_pid);

  waitpid(child_pid, NULL, 0);
  return 0;
}
```

Результат работы программы


```
(base) vvs@vvs-System-Product-Name:~/1$ gcc -o pid -w pid.c
(base) vvs@vvs-System-Product-Name:~/1$ sudo ./pid
clone() = 61832
PID: 1
Parent PID: 0
```


**Внутри клонированного процесса с фалогом `CLONE_NEWPID` нет информации о дереве процессов снаружи.**
 

