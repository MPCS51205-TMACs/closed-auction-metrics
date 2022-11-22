# closed-auction-metrics

## to run tests 

use pytest with verbose and print-to-std-out flags. E.g., cd to `domain/` and run
```
$ pytest tests/ -vs
```

Due to imports some tests might have to be run like so

```
$ python3 -m pytest domain/tests/test_auction.py  -vs
```

fire up with
```
$ docker-compose -f docker-compose-inmem.yml up -d
```

turn down with
```
$ docker-compose -f docker-compose-inmem.yml down
```