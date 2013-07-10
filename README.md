# shellstream
> Version 0.0.1

# What

shellstream is a python client that pipes your terminal IO to the web:

# installing

## pip makes it easy

    pip install shellstream

# running

To run StreamShell, you will need to receive an API Token from http://obscure-wave-3305.herokuapp.com/account/signup/.  Just sign up and go to this page http://obscure-wave-3305.herokuapp.com/how/it/works/cli/.

Add this token to your `.bash_profile`:

```bash
STREAM_SHELL_TOKEN = [your token]
```

# limitations

This initial version is naive.  It is not cross-platform at this point, depending on a number of unix commands. That will come with time.

# Motivation

When you've got an issue at the command line and need help online, copy and pasting your session on an ongoing basis is a pain and it makes you switch mental context.  So, I created shellstream along with the companion website to make debugging smoother.
