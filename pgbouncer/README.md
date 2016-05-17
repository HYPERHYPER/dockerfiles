# PGBouncer

This is primarily from [mbentley/ubuntu-pgbouncer](https://hub.docker.com/r/mbentley/ubuntu-pgbouncer/), with some added tweaks to the ini file.  If you've stumbled upon this from some other search, I recommend using that version over this one.

## Changes from original source

- Explicitly uses trusty version of Ubuntu
- Uses `md5` instead of `trust` for auth, since `trust` doesn't validate the password (which is fine if your security group / vpc prevents connections from outside sources, but I prefer it to still auth)
- Added admin_users, stats_users
- pool_mode is now `transaction`
- default default_pool_size now 475

## General Info

based off of ubuntu:14.04

To pull this image:
`docker pull phhhoto/ubuntu-pgbouncer`

Example usage:
`docker run -i -t -d -p 6432:6432 --link postgres:pg phhhoto/ubuntu-pgbouncer`

This requires a link (named pg) to a postgres container or manually configured environment variables as follows:

`PG_PORT_5432_TCP_ADDR` (default: <empty>)

`PG_PORT_5432_TCP_PORT` (default: <empty>)

`PG_ENV_POSTGRESQL_USER` (default: <empty>)

`PG_ENV_POSTGRESQL_PASS` (default: <empty>)

`PG_ENV_POSTGRESQL_MAX_CLIENT_CONN` (default: 10000)

`PG_ENV_POSTGRESQL_DEFAULT_POOL_SIZE` (default: 475)

`PG_ENV_POSTGRESQL_SERVER_IDLE_TIMEOUT` (default: 240)
