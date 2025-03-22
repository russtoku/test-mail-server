# File: test_mail_server.py
# Desc: A dummy SMTP server that saves messages to mailboxes on the filesystem.
# Date: 03/21/2025, russtoku@gmail.com
#
# SPDX-FileType: SOURCE
# SPDX-FileCopyrightText: Copyright 2025 Russ Tokuyama <russtoku@gmail.com>
# SPDX-License-Identifier: MIT
#
#------------------------------------------------------------
# Accepts incoming mail on port 8025 and delivers to MH type of mailboxes.
#
# In the directory set in the MAIL_BOXES_DIR variable, there are directories for
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
# Ctrl-C stops the server.
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
import time

from aiosmtpd.controller import Controller
from email.message import Message
from mailbox import MH
from pathlib import Path


formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
log = logging.getLogger('smtp')
log.addHandler(ch)

def mailbox_from(email_addr: str, mail_dir: Path) -> Path:
    """Returns a path to the user's mail box. It has the form,
       f"{mail_dir}/${domain}/${user}", where an email address has the form,
       f"${user}@${domain}".
    """
    if not "@" in email_addr:
        return ("bad user", "bad domain")
    user, domain = email_addr.split('@')

    # FIXME: Add a simple check for reasonably valid user and domain.
    mbox_path = f"{mail_dir}/{domain}/{user}"
    return Path(mbox_path)

def open_mbox(mbox: Path) -> MH:
    """Returns an opened MH mail box; creating one if it doesn't exist."""
    if not mbox.exists():
        mbox.mkdir(mode=0o750, parents=True, exist_ok=True)

    mh_box = MH(mbox)
    return mh_box

class RoutingHandler:
    """Route incoming mail to mailboxes for recipients specified in the
       envelope.
       Takes a mail_path pointing to the location of the MH mail boxes.
    """
    def __init__(self, mail_path: Path = Path("")):
        self.mail_path: Path = mail_path

    async def handle_DATA(self, server, session, envelope) -> list[str]:
        """Deliver message to recipients' mail boxes. Returns a list of email
           addresses that couldn't be delivered to.
        """
        recipients = envelope.rcpt_tos
        msg = envelope.content.decode('utf8', errors='replace')
        log.debug(f"recipients: {recipients}")

        # FIXME: Prepend the current date to the msg.

        failed_delivery = []

        for r in recipients:
            mbox_path = mailbox_from(r, self.mail_path)
            log.info(f"Attempting delivery to: {mbox_path} for {r}")

            mh_box = open_mbox(mbox_path)
            mh_box.lock()
            key = mh_box.add(msg)
            if int(key) < 1:
                failed_delivery.append(r)
            mh_box.close()

        error_msg = f" But not to {failed_delivery.join(', ')}" if len(failed_delivery) > 0 else ""
        server_reply = f"250 Message accepted for delivery.{error_msg}"

        return server_reply

def main(mail_dir: str):
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log.critical(f"logging level is set to {log_level}")
    log.setLevel(log_level)

    mail_path = Path(mail_dir)
    if not mail_path.exists():
        mail_path.mkdir(mode=0o750, parents=True, exist_ok=True)
        log.info(f"Creating mail box directory, {mail_dir}")

    handler = RoutingHandler(mail_path)
    controller = Controller(handler)

    log.info("Starting server")
    controller.start()

    while True:
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            log.info("KeyboardInterrupt")
            break
        pass

    log.info(f"Server stopping.")
    controller.stop()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} mail_dir", file=sys.stderr, flush=True)
        sys.exit(1)

    main(sys.argv[1])
