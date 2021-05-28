#!/usr/bin/env python3

import sys
import os

# How to use (OpenSMTPD >= 6.6.0 only):
#
# Copy the python file (to /etc/mail for example).
# Add the following line inside /etc/smtpd.conf:
#
#     filter stripagent proc-exec "/etc/mail/opensmtpd-filter-agent.py"
#
# Modify configuration to use this filter:
#
#     listen on ... port ... ... filter stripagent

def recv(stdin):
    return stdin.readline().rstrip('\r\n')

def send(stdout, line):
    print(line, file=stdout)

if __name__ == "__main__":
    _stdin  = os.fdopen(sys.stdin.fileno(),  'r', encoding='latin-1', buffering=1)
    _stdout = os.fdopen(sys.stdout.fileno(), 'w', encoding='latin-1', buffering=1)
    _stderr = os.fdopen(sys.stderr.fileno(), 'w', encoding='latin-1', buffering=1)

    filter_headers = (
        "User-Agent",
        "X-User-Agent",
        "X-Mailer"
    )

    # See smtpd-filters(7) for protocol documentation
    # https://man7.org/linux/man-pages/man7/smtpd-filters.7.html

    while recv(_stdin) != 'config|ready':
        pass

    send(_stdout, "register|filter|smtp-in|data-line")
    send(_stdout, "register|ready")

    while True:
        line = recv(_stdin)

        if line.count("|") != 7:
            continue

        *stuff, session, token, data = line.split("|")

        if not any(data[:len(header)].lower() == header.lower() for header in filter_headers):
            send(_stdout, f"filter-dataline|{session}|{token}|{data}")
