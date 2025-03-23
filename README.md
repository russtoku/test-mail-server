# test-mail-server
A scrappy fiddles (thanks, [Lu Wilson](https://www.youtube.com/watch?v=MJzV0CX0q8o)) mail server for
testing.

There are many fake SMTP servers. Some are good. Some are bad. But I just wanted something:
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

I thought that I would need to implement both SMTP and IMAP servers to be able to test sending and
reading emails from a Django application. The docs for aiosmtpd seems to indicate that the SMTP
server part of things would be fairly easy (Ha! Famous last words!).

While trying to see how difficult it would be to implement an IMAP server using
[asimap](https://github.com/scanner/asimap), I realized that I didn't need to do that. It can serve
mail from MH-style mailboxes. In the process, I learned more about different mailbox types and began
to see that for my purposes all I would need to do is have the SMTP sever deliver messages to
MH-style mailboxes. So I just needed to write a handler for `aiosmtpd` that would do that and
`asimap` will serve the messages for each user via IMAP.

This SMTP server just fits my needs and will remain so. You are welcome to use it and I hope you
find it helpful.

*TODO:* The IMAP server part is coming. It may take the form of a website to read and send
messsages.

## Run the mail server

- Clone the repo or just download `test_mail_server.py`.
- Create a Python 3.13 virtual environment and install the dependencies. See the section below on
  [creating a virtual environment](#virtual_env).
- Activate the virtual environment.
    ``` console
    $ source .venv/bin/activate
    ```
- Decide where you want to have the incoming emails delivered to. This is a directory where all
  emails will be delivered to. The directory will be structured with email domain at the top level
  followed by users in each domain. Finally, the emails are stored MH style as separate files in the
  user's mailbox directory. See the [delivered mail section](#delivered_mail).
- Run the server.
    ``` console
    $ python test_mail_server.py mail-boxes
    ```
- To stop the server, type `Ctrl-C`.

The mailbox directory (`mail-boxes` in the above command line) will be automatically created if it
doesn't exist.

The `LOG_LEVEL` environment variable can be used to change the logging level when
the program is run. The default level is *INFO*.

In this example, the environment variable is set just for the running of the
program.

    ``` console
     $ LOG_LEVEL=DEBUG python test_mail_server.py mail-boxes
    ```

## Send some emails

The default port that the test mail server listens on is 8025 so you can connect
to `localhost:8025` without authentication.

If you need authentication and/or TLS, you'll need to figure that out yourself.

For quick testing of SMTP functionality, you can use `nc` as an email client to talk to the SMTP
server and send it a message. Here, you can see the responses from the server interleaved with the
client's requests.

``` console
$ nc -c localhost 8025
220 1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.ip6.arpa Python SMTP 1.4.6
HELO uipa.org
250 1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.ip6.arpa
MAIL FROM: <alice@uipa.org>
250 OK
RCPT TO: <bob@doh.hi.gov>
250 OK
DATA
354 End data with <CR><LF>.<CR><LF>
Hi, Bob!

Look forward to seeing you at the luncheon on Tuesday.

Alice
.
250 Message accepted for delivery.
QUIT
221 Bye
```

The client sends this line-by-line:

``` console
HELO uipa.org
MAIL FROM: <alice@uipa.org>
RCPT TO: <bob@doh.hi.gov>
DATA
Hi, Bob!

Look forward to seeing you at the luncheon on Tuesday.

Alice
.
QUIT
```

When you do this, the SMTP server's side look like this:

``` console
$ python test_mail_server.py mail-boxes
2025-03-22 09:28:48,745 smtp CRITICAL logging level is set to INFO
2025-03-22 09:28:48,745 smtp INFO Starting server
2025-03-22 09:30:12,558 smtp INFO Attempting delivery to: mail-boxes/doh.hi.gov/bob for bob@doh.hi.gov
```

And when you type `Ctl-C` to stop the SMTP server, it looks like this:

``` console
^C2025-03-22 09:31:03,270 smtp INFO KeyboardInterrupt
2025-03-22 09:31:03,270 smtp INFO Server stopping.
```

<a id="delivered_mail"></a>
## Look at the delivered mail

To look at the email that was delivered, you can browse the mail directory and
simply print the messages because the messages are plain text. They are stored
in a hierarchy based on the mail domain and user.

Here's an example where messages were sent to bart@example.com,
homer@example.com, and admin@uipa.org:

``` console
mail-boxes
├── example.com
│   ├── bart   <-- mailbox for bart@example.com
│   │   ├── 1
│   │   └── 2
│   └── homer   <-- mailbox for homer@example.com
│       └── 1
└── uipa.org
    └── admin   <-- mailbox for admin@uipa.org
        └── 1
```

<a id="virtual_env"></a>
## Creating a virtual environment

I suggest using [`uv`](https://docs.astral.sh/uv/) but you can do it your own way.

Use `uv` to install the version of Python you want to use by configuring it to use the Python
package that Astral builds. This avoids the quirks and idosyncracies of Python packages from other
package managers (Homebrew on macOS, Linux package managers, etc.).

After wasting a couple of days trying figure out why this code no longer worked, I discovered that
the virtual environment created from another package manager's Python package was the
problem. Changing the virtual environment to one created using Astral's Python package solved it.

Create a virtual environment for a project in the working directory where you'll be doing your
coding and testing. Activate it and go.

### The steps
- Install `uv`.
- Create a `uv.toml` file in the `~/.config/uv/` directory.

  Put this in it.
  ```
  python-preference = "only-managed"
  ```
  This will make sure that the Astral Python packages will be used. See
  https://docs.astral.sh/uv/configuration/files/#configuration-files.
- Clone the repo and change into the working directory.
- Create the virtual environment by running:
  ``` console
  $ uv venv
  ```
- Install the dependencies.
    - Take advantage of existing `uv.lock` file.
  ``` console
  $ uv sync
  ```
    - Use `pyproject.toml` file.
  ``` console
  $ uv pip install -r pyproject.toml
  ```

Now, go have fun.

