# Barry


## Introduction

This repository contains code to manage my Raspberry Pi (named Barry) for use as a home NAS. It has a single SSD mounted with 2 samba directories exposed (1 gets backed up to Gdrive the other doesn't). This repo is mostly glue code to perform the following actions

- Run rclone to backup contents of the SSD to gdrive
- Routinely copy my repos from GitHub.com to the SSD
- Check the health and capacity of the SSD
- Send emails to notify me of any issues



## TODO

- [ ] Re-write email code to use google API
- [ ] Setup Rclone api token
- [ ] Convert code to be command line based
- [ ] Update usage report to include health check
- [ ] Determine how to store / install the code
- [ ] Update cron job
