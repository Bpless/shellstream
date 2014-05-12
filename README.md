# shellstream
> Version 0.0.1

# What is it?

shellstream is a Python client that pipes your terminal IO to the web.  Previously, there was a hosted endpoint for receiving your stream.  I have taken down that server, so this app will not work at present.  I plan to package a Flask or Tornado server into this app so that it can be self-hosted.

# To Install

## pip makes it easy

    pip install shellstream

# To Run

To run StreamShell, you will need to receive an API Token from [coming soon].  To retrieve a token, first sign up for the service (it's free) and then head to this page [coming soon].

Add this token to your `.bash_profile`:

```bash
STREAM_SHELL_TOKEN = [your token]
```

# Motivation

When you've got an issue at the command line and need help online, copy and pasting your session on an ongoing basis is a pain and it makes you switch mental context.  So, I created shellstream along with the companion website to make debugging smoother.


# Limitations

This initial version is naive.  It is not cross-platform at this point, dependent on a number of unix commands. There are also zero tests at present -- I plan to add them shortly.
