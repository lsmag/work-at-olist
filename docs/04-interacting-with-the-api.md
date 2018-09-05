Interacting with the API
===============================

To run sparrow, simply call `make run`, which is a shortcut for `docker-compose up`.
This won't daemonize the process so you'll need another term window to interact
with it.

I'm using [httpie][1] here to show some examples but any command-line tool would
work (like the usually prevalent `curl`).

Some examples:

    $ http POST localhost:8000/call_records/ type=end call_id=21 timestamp=2018-03-01T22:10:56Z
    $ http POST localhost:8000/call_records/ type=start call_id=21 timestamp=2018-03-01T22:03:01Z \
        source=2133445566 \
        destination=1133224433
    $ http GET localhost:8000/call_records/
    $ http GET localhost:8000/call_records/telephone_bill/?subscriber=2133445566
    $ http GET localhost:8000/call_records/telephone_bill/?subscriber=2133445566&reference_period=201803
    
The full API is documented in the next chapter.

[1]: https://httpie.org/
