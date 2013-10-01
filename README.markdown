# FakeSSH

FakeSSH is an SSH server which denies all login requests sent its way. It's the result of literally minutes of work.

## Requirements

* python
* paramiko

# Use

1. Create an RSA key using `ssh_keygen`. Save it to data/rsa.
1. Copy data/config.sample.json to data/config.json
1. Edit if desired.
1. Run `server.py` with python.

If you're on Ubuntu, you could create an upstart script at `/etc/init/fakessh.conf`:

    # fakessh
    description "A fake SSH server"
    author "Tyler Menezes <tylermenezes@gmail.com>"
    start on runlevel [2345]
    stop on runlevel [016]
    respawn
    exec python /opt/fakessh/server.py

# Future Plans

In the previous version of this (which was written in C++, but full of memory leaks), statistics about attempted logins were tracked. This made for an awesome MOTD on the real SSH port. At some point, it would be cool to re-add that functionality.

This should also *really* be dropping root permissions after opening the port if running as root.