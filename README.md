# ZDP: real-time data synchronization over zerorpc

## Overview

ZDP is an experimental implementation of real-time data synchronization, using zerorpc as a transport. It is inspired by RacerJS, Meteor, and by patterns developed internally at dotCloud to build modern distributed systems.

For a video demonstration see http://goo.gl/hGU4z .

## Status

This is alpha software. ZDP was developed during a dotCloud hack day, and should only be used as a proof-of-concept.


## Author

Solomon Hykes <solomon@dotcloud.com>


## Usage

    # Install dependencies:
    $ pip install gevent gevent-websocket http://github.com/dotcloud/zerorpc-python

    # Run zeroservice
    $ python users.py

    # Run websocket bridge
    $ python ws.py tcp://127.0.0.1:4242 9999

    # Open web interface
    ${BROWSER} file://test.html

    # Note that you can make out-of-band calls to the zeroservice: they will be synced to the browser
    zerorpc tcp://127.0.0.1:4242 add_user zed zed@dotcloud.com
