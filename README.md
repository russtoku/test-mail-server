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

This is SMTP server just fits my needs and will remain so. You are welcome to
use it and I hope you might find it helpful.

*TODO:* The IMAP server part is coming. It may take the form of a website to read and send
messsages.

## Run the mail server

- Create a Python 3.13 virtual environment. See the section below on [creating a virtual environment](#virtual_env).
- `pip install aiosmtpd`
- Clone the repo or just download `test_mail_server.py`.
- Decide where you want to have the incoming emails delivered to. This is a directory where all
  emails will be delivered to. The directory will be structured with email domain at the top level
  followed by users in each domain. Finally, the emails are stored MH style as separate files in the
  user directory. See the [delivered mail section](#delivered_mail).

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
│   ├── bart   <-- bart@example.com
│   │   ├── 1
│   │   └── 2
│   └── homer   <-- homer@example.com
│       └── 1
└── uipa.org
    └── admin   <-- admin@uipa.org
        └── 1
```

<a id="virtual_env"></a>
## Creating a virtual environment

You can do it your way but I suggest using [`uv`](https://docs.astral.sh/uv/).

Use `uv` to install the version of Python you want to use. Configure it to use the Python package
that Astral builds to avoid the quirks and idosyncracies of Python packages from other package
managers (Homebrew on macOS, Linux package managers, etc.).

After wasting a couple of days trying figure out why this code no longer worked, I discovered that
the virtual environment created from another package manager's Python package was the
problem. Changing to a virtual environment using Astral's Python package solved it.

Create a virtual environment for a project in the working directory where you'll be doing your
coding and testing. Activate it and go.

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
  $ uv sync
  ```

Now, go have fun.

