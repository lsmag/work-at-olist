Sparrow API documentation
================================

This API contains only two endpoints. It does not offer an endpoint
for interacting with a call record in particular (GET,POST, PUT, PATCH),
it only offers:
- getting a list of call records
- adding a new call record
- getting a telephone bill

/call_records/
--------------

### GET /call_records/

Returns a list of all call records. Start and end records have different formats.

#### Example of response (200):

    [
        {
            "id": 21,
            "call_id": 12,
            "type": "start",
            "timestamp": "2018-01-02T22:10:56Z",
            "source": "2111223344",
            "destination": "1111223344"
        },
        {
            "id": 25,
            "call_id": 12,
            "type": "end",
            "timestamp": "2018-01-02T23:10:56Z"
        }
    ]

### POST /call_records/

Creates a new call record. If successful, returns 201 with a representation
of the created record.

Requirements:
- `type` must be either `"start"` or `"end"`
- `call_id` must be a positive integer
- the `(type, call_id)` tuple must be new, i.e. must not exist in the
  database already
- `timestamp` must be a valid datetime
- `source` and `destination` are mandatory if `type` is `"start"`
- `source` and `destination` follow the string format `"AAXXXXXXXXX"`,
  where `AA` is the area code, and `XXXXXXXXX` is the phone number,
  with 8 or 9 characters.  All characters must be integers.

#### Example of response, START record (201):

    {
        "id": 21,
        "call_id": 12,
        "type": "start",
        "timestamp": "2018-01-02T22:10:56Z",
        "source": "2111223344",
        "destination": "1111223344"
    }

#### Example of response, END record (201):

   {
       "id": 25,
       "call_id": 12,
       "type": "end",
       "timestamp": "2018-01-02T23:10:56Z"
   }
   
#### Example of response, duplicated (type, call_id) (400):

    {"detail": "Call record already exists"}
    
#### Example of response, invalid data (400):

The response will include a mapping of faulty fields with a list
of encountered errors, for example:

    {
        "type": ["Only \"start\" or \"end\" are allowed"]
    }

/call_records/telephone_bill/
-----------------------------

### GET /call_records/telephone_bill/

Returns a telephone bill for the given reference period with _only_
call record pairs (records with both START and END). A record pair is
in _if and only if_ it ends within the reference period.

Requirements:
- `subscriber` is mandatory, it's a string in the `"AAXXXXXXXXX"`
  format mentioned above
- `reference_period` is optional. If missing, the endpoint will
  consider the last month as the reference period. If given, it MUST
  be a string in the `"YYYYMM"` format
  
#### Example of response (200):

    {
        "subscriber": "1122334455",
        "reference_period": "201801",
        "call_records": [
            {"destination": "2199997777",
             "duration": "1h",
             "price": "R$ 5,76",
             "start_date": "2018-01-01",
             "start_time": "10:00:00Z"},
            {"destination": "2199997777",
             "duration": "1h",
             "price": "R$ 5,76",
             "start_date": "2018-01-02",
             "start_time": "11:00:00Z"},
            {"destination": "2199997777",
             "duration": "2h",
             "price": "R$ 11,16",
             "start_date": "2018-01-03",
             "start_time": "12:00:00Z"}
        ]
    }
    
#### Example of response, reference period not closed (400):

If a request is made for the current month, since it's not yet closed,
the endpoint will return an error with the following body:

    {"detail": "Reference period 201802 is not closed yet"}

#### Example of response, invalid data (400):

The response will include a mapping of faulty fields with a list
of encountered errors, for example:

    {
        "reference_period": ["Reference period should be in the YYYYMM format"]
    }
