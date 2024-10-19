# test_mail_server.py - A dummy SMTP server that saves messages to mailboxes on
#                       the filesystem.
#                     - 10/18/2024, russtoku@gmail.com
#                     - License: MIT License
#
#------------------------------------------------------------
# Accepts incoming mail and delivers to MH type of mailboxes.
#
# In the directory set in the mail_dir variable, there are directories for
# email domains. Within each email domain directory, there are directories for
# each user for user@email.domain.
#
# Dependencies: aiosmtpd
#
# Usage:
#
# $ python test_mail_server.py mail_dir
#
# mail_dir will be created if it doesn't exist. Use relative or full path.
#
# Ctrl-C stops server.
#
# The LOG_LEVEL environment variable can be used to change the logging level
# when the program is run. Example:
#
# $ LOG_LEVEL=DEBUG python test_mail_server.py mail_dir
#------------------------------------------------------------
#

import asyncio
import logging
import os
import sys

from aiosmtpd.controller import Controller
from email.message import Message as Em_Message
from mailbox import MH

formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
log = logging.getLogger('smtp')
log.addHandler(ch)


# This will be overriden by main().
mail_dir = "mh-box"

def mailbox_from_email(addr):
    """Returns user and domain from email address of 'user@domain'."""
    if not "@" in addr:
        return ""
    user, domain = addr.split('@')
    return (user, domain)

def get_folder(folder, mbox):
    """Returns an opened folder in mbox creating one if it doesn't exist."""
    folders = mbox.list_folders()
    if not folder in folders:
        log.debug(f"creating {folder}")
        fl = mbox.add_folder(folder)
    else:
        fl = mbox.get_folder(folder)
    return fl

def deliver_to_mailbox(recipient, mail_dir, msg):
    """Add a message to the recipient's mailbox. Returns nothing."""
    user, domain = mailbox_from_email(recipient)

    mdir = MH(mail_dir)
    mdom = get_folder(domain, mdir)
    ubox = get_folder(user, mdom)
    ubox.add(msg)
    log.debug(f"message delivered to: {mail_dir}/{domain}/{user}")

    ubox.close()
    mdom.close()
    mdir.close()


class RoutingHandler:
    """Route incoming mail to mailboxes for recipients specified in the
       envelope.
    """
    async def handle_DATA(self, server, session, envelope):
        recipients = envelope.rcpt_tos
        msg = envelope.content.decode('utf8', errors='replace')

        for r in recipients:
            log.info(f"Delivering to: {mailbox_from_email(r)} for {r}")
            deliver_to_mailbox(r, mail_dir, msg)

        return '250 Message accepted for delivery'

def main(dir):
    mail_dir = dir

    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log.critical(f"logging level is set to {log_level}")
    log.setLevel(log_level)

    controller = Controller(RoutingHandler())

    log.info("Starting server")
    try:
        controller.start()
        while True:
            pass
    except KeyboardInterrupt as ki:
        log.info(f"Server interrupted.")
    finally:
        controller.stop()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} mail_dir", file=sys.stderr, flush=True)
        sys.exit(1)

    from pathlib import Path
    mail_dir = sys.argv[1]
    p = Path(mail_dir)
    if not p.exists():
        p.mkdir()

    main(p)
