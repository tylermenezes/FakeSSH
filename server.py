#!/usr/bin/env python

import base64
from binascii import hexlify
import os
import socket
import sys
import threading
import traceback
import paramiko
import json
import time

raw_config=open('data/config.json').read()
config = json.loads(raw_config)

if (config['log'] is not False):
    paramiko.util.log_to_file(config['log'])

class Server (paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
        self.host_key = paramiko.RSAKey(filename=config['key'])
        self.has_authenticated_before = False

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_interactive(self, username, submethods):
        if self.has_authenticated_before:
            return paramiko.AUTH_FAILED
        else:
            self.has_authenticated_before = True
            return paramiko.InteractiveQuery('', config['banner'])

    def check_auth_password(self, username, password):
        time.sleep(3)
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        time.sleep(3)
        return paramiko.AUTH_FAILED

    def check_auth_interactive_response(self, responses):
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return 'keyboard-interactive,publickey,password'

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth,
                                  pixelheight, modes):
        return True

def incoming_connection(client):
    try:
        t = paramiko.Transport(client)

        # Try to load server moduli for gex
        try:
            t.load_server_moduli()
        except:
            print 'Failed to load moduli -- gex will be unsupported.'
            raise

        # Start the server & negotiate with the client
        server = Server()
        t.add_server_key(server.host_key)
        try:
            t.start_server(server=server)
        except paramiko.SSHException, x:
            print 'SSH negotiation failed.'
            try:
                t.close()
            except:
                pass
            return

        # Wait for auth
        t.accept(20)
        try:
            t.close()
        except:
            pass
        return

    except Exception, e:
        print 'Caught exception: ' + str(e.__class__) + ': ' + str(e)
        traceback.print_exc()
        try:
            t.close()
        except:
            pass
        return

# Bind to the port
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', config['port']))
except Exception, e:
    print 'Could not bind to port: ' + str(e)
    traceback.print_exc()

# Start listening for connections
server_listening = True
while server_listening:
    try:
        sock.listen(100)
        print 'Waiting for connection.'
        client, addr = sock.accept()

        print 'Client connected!'
        threading.Thread(target=incoming_connection, args=[client]).start()
    except Exception, e:
        print "Couldn't wait for connection: " + str(e)
        traceback.print_exc()

sock.close()
