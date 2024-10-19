# test-mail-server
A scrappy fiddles (thanks, Lu Wilson) mail server for testing.

There are many fake SMTP servers available. Some are good. Some are bad. But
I just wanted something:
- Very simple
- Easy to set up
- No fuss, no muss

Luckily, Python has a library called
[aiosmtpd](https://pypi.org/project/aiosmtpd/) which replaces the now defunct
`smtpd` library.

From the [docs](https://docs.python.org/3.11/library/smtpd.html):
> Deprecated since version 3.6, will be removed in version 3.12: The smtpd
> module is deprecated (see PEP 594 for details). The aiosmtpd package is
> a recommended replacement for this module. It is based on asyncio and provides
> a more straightforward API.

I thought that I would need to implement both a SMTP and IMAP server to be able
to test sending emails from a Django application that I've trying help out
with. The docs for aiosmtpd seems to indicate that the SMTP server part of
things would be fairly easy (ha! famous last words!). While trying to see how
difficlut it would be to implement an IMAP server using
[asimap](https://github.com/scanner/asimap), I realized that I didn't need to do
that. In the process, I learned a bit more about different mailbox types and
began to see that for my purposes I could *just* write a handler for aiosmtpd
that would deliver incoming mail to the mailboxes of the recipients.

This is SMTP server just fits my needs and will remain so. You are welcome to
use it and I hope you might find it helpful.

## Run the mail server

- Create a Python 3.12 virtual environment.
- `pip install aiosmtpd`
- Clone the repo or just download `test_mail_server.py`.
- Decide where you want to have the incoming emails delivered to.
- Run the server.
    ```
    $ python test_mail_server.py mail_dir
    ```
- To stop the server, type `Ctrl-C`.

The LOG_LEVEL environment variable can be used to change the logging level when
the program is run. The default level is *INFO*.

In this example, the environment variable is set just for the running of the
program.

    ```
     $ LOG_LEVEL=DEBUG python test_mail_server.py mail_dir
    ```

## Send some emails

The default port that the test mail server listens on is 8025 so you can connect
to `localhost:8025` without authentication. If you need authentication and/or
TLS, you'll need to figure that out yourself.

## Look at the delivered mail

To look at the email that was delivered, you can browse the mail directory and
simply print the messages because the messages are plain text. They are stored
in a hierarchy based on the mail domain and user.

Here's an example where messages were sent to ben@example.com,
donna@example.com, dale@example.net, and carrie@example.org:

```
mail_dir/
├── example.com
│   ├── ben
│   │   ├── 1
│   │   ├── 2
│   │   └── 3
│   └── donna
│       └── 1
├── example.net
│   └── dale
│       └── 1
└── example.org
    └── carrie
        ├── 1
        └── 2
```

