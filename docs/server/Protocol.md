## HTTP API

    /api/v1/

Params:

* location
* tool
* badge\_id
* state=initial,extend,cancel
* auth\_minutes (number)

Requests should also authenticated, for example with an `api_key` param, or by
ssl client cert.

The server can make assumptions about the total authorized time, for example if
requests like this happen:

* `auth_minutes=30,state=initial` at t=0
* `auth_minutes=30,state=extend` at t=22

That the total authorized time for usage stats is only 22+30 minutes.

This API requires the client to only store minimal state -- the `badge_id`
(which must be re-sent), and whether a session is in progress to differentiate
`initial` vs `extend`.
