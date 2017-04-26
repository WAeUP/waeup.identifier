#!/bin/bash
# This script starts a reverse SSH tunnel on $REMOTE_HOST
# Running it enables users on $REMOTE_HOST to ssh into
# localhost:$REVERSE_PORT and being connected with the local
# machine. Handle with care. Running this script enables
# remote users to log into the machine where this script runs!
#
# Please use different REVERSE_PORTs for different devices.
#

# The remote host, from where we want to access. IP or DNS name.
REMOTE_HOST=192.168.23.23
# The remote user we become on the remote host.
REMOTE_USER=reverse
# The port on the remote host we connect the local SSH server to.
REVERSE_PORT=22001

echo "STARTING REVERSE SSH ON "$REMOTE_HOST":"$PORT ;
echo "TO ABORT PRESS CTRL-C OR CLOSE TERMINAL WINDOW" ;

ssh -fN -R $REVERSE_PORT:127.0.0.1:22 $REMOTE_USER@$REMOTE_HOST ;

read DUMMY ;
