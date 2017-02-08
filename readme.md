# toycache.py [![Build Status](https://travis-ci.org/GedRap/toycache.py.svg?branch=master)](https://travis-ci.org/GedRap/toycache.py)

Memcached server implemented in python for educational purposes, wanted to learn more about the memcached protocol.

## Compatibility with memcached

[[https://github.com/GedRap/toycache.py/blob/master/screenshots/toycache.png|alt=octocat]]

I tried to achieve high compatibility but made some decisions to limit
the scope of the project to keep it at the 'weekend project' level and thus excluded some features.

Most of the minor things missing are marked as @todo in the code but major missing features are as follows:

- Binary protocol support;

- `stats` output is very minimal.

### Running it locally

```
git clone https://github.com/GedRap/toycache.py.git
cd toycache.py
pip install -r requirements.txt
./run.sh
```

### Running it in production

Don't do that.