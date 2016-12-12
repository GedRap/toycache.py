# toycache.py [![Build Status](https://travis-ci.org/GedRap/toycache.py.svg?branch=master)](https://travis-ci.org/GedRap/toycache.py)

Memcached server implemented in python for educational purposes.

## Compatibility with memcached

I tried to achieve high compatibility but made some decisions to limit
the scope of the project to keep it at the 'weekend project' level and thus excluded some features.

I did my best to mention all the features that are excluded below:

- Binary protocol support;

- Delayed flush_all;

- `stats` output is very different (actually there is no `stats` support
at the time of writing but planning to do it eventually).

### Running it locally

```
git clone https://github.com/GedRap/toycache.py.git
cd toycache.py
pip install -r requirements.txt
python run.py
```

### Running it in production

Don't do that.