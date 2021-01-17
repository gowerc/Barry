# Raspberry Pi Backup Repo


## Introduction

This repository contains my notes and code used on my raspbery pi (known as Barry) to backup my personal data.

Barry has two hardrives mounted of which 1 is exposed as a Samba file server for all computers on the network to access. The code in this repository then routinely copies the data to the second harddrive via `rsync` making backups of any files deleted. It also routinely copies the data to a GoogleDrive folder via `rclone`.

Project requires python 3.7 using a venv and requirements.txt

```
python3.7 -m venv venv   # create virtual environment
./venv/bin/python -m pip install -r requirements.txt  # install required 
```

## Misc Pi stuff

```
dmesg  ## Print kernal level messages (useful for power supply issues)
```

```
sudo shutdown -h now  ## Shutdown
sudo shutdown -r now  ## Restart
```

## Samba 

Start / stop / restart the samba server
```
sudo /etc/init.d/smbd start
sudo /etc/init.d/smbd stop
sudo /etc/init.d/smbd restart
```

Configuration file

```
sudo vim /etc/samba/smb.conf
```

Description of what all the [share] options do:  
https://www.samba.org/samba/docs/current/man-html/smb.conf.5.html#CREATEMASK



Connecting to Samba:

First find the server name. I am with BT so we access the router via `http://192.168.1.254`.   Ensure that the raspberry pi has  a static IP and is named. In this case I named it `mypi`

### Mac

Press cmd + k  ,  server = `smb://mypi.local/share` ,  username = pi , password = pi user password  

### Windows

Map network drive or add network location , server = `\\mypi.local\share` , username = pi , password = pi user password


## Permissions

```
chmod  abcd   <object>
```

| Reference | Purpose | 
|---|---|
|a | The first octal digit sets the setuid, setgid and sticky bits
|b | Sets the USER permission |
|c | Sets the GROUP permission |
|d | Sets the WORLD permission |


|#|	Permission	|rwx|	
|---|---|---|
|7|	read, write and execute|	rwx	|
|6|	read and write|	rw-|	
|5|	read and execute|	r-x|	
|4|	read only	|r--	|
|3|	write and execute|	-wx	|
|2|	write only|	-w-	|
|1|	execute only	|--x	|
|0|	none	|---	|

```
umask abcd
```

When you create a new file it starts with permissions 0666 or 0777 if it is a directory. The umask function determines which permissions to remove from any newly created files.
Thus a umask of 0033 would remove the write and execute permission from GROUP and WORLD thus leaving a new file with 0644

**IMPORTANT**

Within Samba mask is used as a "maximium" permission level; from the manual:

> Any bit not set here will be removed from the modes set on a file when it is created.

In a practical sense create mask is used to set the permission level of newly created files 


## All things hard drive related


### Auto mounting hard drives 
Drives will be automatically mounted on boot if there is a record for them in `etc/fstab`. Details:   
https://help.ubuntu.com/community/Fstab  
https://wiki.debian.org/fstab  

```
UUID=<drive identifier> <path to mount at>  <file format>  <options>  <not sure>  <not sure>
```
e.g.
```
UUID=2e3ece57-6526-4acd-aba3-79f0937ecad0 /hdd ext4 noatime,nofail 0 0
```

**IMPORTANT** 

After mounting a drive for the first time you will need to change ownership of the drive to that of the user
```
sudo mount /dev/sda  /media/hdd
sudo chown <user>:<group>  /media/hdd
```

### Disk checking commands

```
sudo lsblk -f  ## list all drives + info
sudo blkid     ## List all drives + info 
lsusb          ## List all usb devices
du -sh         ## Disk usages (-s = summary, -h = readable units)
df -h          ## Disk total size + total available  (mounted drives only)
```


### Drive formating + Labeling 

First find the drive device file using one of the above commands, should be something like `/dev/sdb1`. Then use one of the following depending on what file format you want:
```
sudo mkfs.ext4 /dev/sdb1
sudo mkfs.ntfs /dev/sdb1
sudo mkfs.vfat /dev/sdb1
```

It is worth setting a drive label to make drive identification easier:

```
sudo e2label <device file>  <label>
```

i.e.

```
sudo e2label /dev/sda HomeBackup
```


### Manual Moiunting

```
sudo mount /dev/sdb1 /media/hdd2
sudo umount /media/hdd2
```

Checking health of a drive:
```
sudo smartctl  -a /dev/sda
```

Interpretting the table:    
https://ma.juii.net/blog/interpret-smart-attributes  
(need more info still though)  




## Rsync

### Options

-n  =  Dry run,  do not sync any files  
-v = verbose  
-h = human readable numbers  
-a  = recursive syncing + preseve lots of propertys of the file including modification times and permissions)  
-P  = combines the flags --progress and --partial. The former gives you a progress bar for the transfers and the latter allows you to resume interrupted transfers  
--delete = By default rsync will not delete files this flag will remove files from the target directory that aren't in the source directory  
--exclude = used to exclude specific files (pattern based) or sub directory, include the flag multiple times for multiple exclusions  
--backup-dir = directory to put any files that are deleted or overwritten  
--suffix = a Suffix to give to files placed into backup (i.e. date or some indicator)  
--bwlimit = file transfer limit in KB/s


### Misc notes

- always use trailing /  !!!   i.e.  rsync  dir1/  dir2/   If you don't it will attempt to put dir1 itself inside of dir2  i.e.   dir2/dir1/
- When transfering full speed the disk IO gets consumed and the samba access fails (best to set backup rysnc to be overnight) 

### Examples

```
rsync -ahP  --delete --backup  --backup-dir="/media/hdd2/backup/backup_$(date +\%Y-\%m-\%d)"  /media/hdd/content/ /media/hdd2/content/ |& tee /tmp/logfile_$(date +\%Y-\%m-\%d).txt
```


## Auto runninng - cron

The cron tool allows us to schedule code to be executed on a scheduled basis

https://www.ostechnix.com/a-beginners-guide-to-cron-jobs/

```
crontab -e   ## Open cron tab to edit
```
Each line represents a new cron task to be scheduled.  Each line is formated as:

```
<minute>  <hour>   <day of month>  <month>  <day of week>   <command>  
```

i.e.

```
5  *   *   *   *   echo hello world
```
The `<command>` will be executed when the system time matches the pattern of the time/date parameters
  
minute  = 0-60  
hour =  0-23  
day of month = 1-31  
month = 1-12  
day of week = 1-7  

### Misc

* Use `*` to represent "any" I.e. `5 * * * *` would mean run on the 5th minute of every hour, every day, every month, etc   
* Use `*/x` to represent "any that is divisible by x" I.E `*/5 * * * *` would mean run on every 5th minute (5, 10 , 15)  
* Use `5,10,12,13` i.e. comma separated to run the command at specific points i.e. the 5th 10th 12th minute   
* Use `5-10` to specify a span of units  


## rclone - Remote Syncing

Use the utility rclone to sync files between our local drive and a cloud drive (in this case hdd2 -> gdrive) 

Best explained via the online documentation:
https://rclone.org/commands/


Typical usage for syncing:
```
rclone sync /local/path/to/sync/  REMOTE_TAG:<directory>
```

In our case
```
rclone sync /media/hdd2/content/  RPI_backup:
```



