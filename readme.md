# Manufacturing data collection and analysis project 
## Technologies:
- Postgres 15
- Grafana 9.2.6
- Python 3.11
- Flask
- Telegram API
- OPC UA

## Quick start: <P>
Set properties in .env file <P>
Build project <P>
`./build.sh` <P>
Run project <P>
`./run.sh` <P>
Stop project <P>
`./stop.sh` <P>
View logs <P>
`docker compose logs -f` <P>


## Flask API
### add `?token=yourtoken` into your reqsuests to auth

### GET /health
Health check
+ Response 200 (text/plain)

        ok

### GET /start-simulation
Start simulation of boilers in OPC UA server
+ Response 200 (text/plain)

        Simulation started

### GET /start-collecting-devices
Collect devices data into DB
+ Response 200 (text/plain)

        Devices collected

### GET /start-collecting-mesurements
Collect measurements data into DB (N samples)
+ Response 200 (text/plain)

        Measurements collected

### GET /start-collect-cnc
Start collect cnc measurements data into DB
+ Response 200 (text/plain)

        CNC collecting started

### GET /stop-collect-cnc
Stop collect cnc measurements data into DB
+ Response 200 (text/plain)

        CNC collecting stoped

### GET /start-collect-milling
Start collect milling measurements data into DB
+ Response 200 (text/plain)

        milling collecting started

### GET /stop-collect-milling
Stop collect milling measurements data into DB
+ Response 200 (text/plain)

        milling collecting stoped