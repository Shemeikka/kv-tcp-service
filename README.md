# Key-Value TCP Service

Simple TCP server running Key-Value service. Supports multiple clients. Uses single global state for all clients.

Not recommend for production use!

Service saves state into disk on every PUT command.

Supports three commands:

- GET
  - get key's value
  - e.q. get\ntick\n
- PUT
  - command overwrites key
  - e.q. put\ntick\n{"count": 1}\n
- EXIT
  - server closes client's connection
  - e.q. exit\n

Commands must be ASCII encoded and end into '\n'.

Each response is JSON encoded and ends in '\n'. Response has status-field which can be either "success" or "error". In case of an error, there is an another field called "value" which contains information about the error.

Example using telnet:

    put
    cars
    [{"audi": "A4"}, {"bmw": "X5"}]
    {"status": "success"}
    get
    cars
    {"status": "success", "value": [{"audi": "A4"}, {"bmw": "X5"}]}
    exit
    Connection closed by foreign host.

## Starting the service

Service requires two arguments

- Address: IP address to bind
- Port: TCP port to use

Example:

    python server.py -a localhost -p 5000

## Client

Simple client is included in this project. It increments Tick-key's value every 10 seconds. Client queries this value every 5 seconds.

Client cannot handle multiple responses in single message.