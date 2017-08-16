create a service file (eg. battery1.service) in '/home/services/'

```
[Unit]
Description=Battery 1 test
After=network.target

[Service]
User=sander
WorkingDirectory=<script location>
ExecStart=<venv folder>/bin/python <script location>/start.py --config="config.json"

[Install]
WantedBy=multi-user.target
```

add this service to systemd.


`sudo systemctl enable /home/services/<service>`

`sudo systemctl daemon-reload`

`sudo systemctl start battery1`

`sudo journalctl -f u battery1`

```
+-----------------+                 +-----------------+                      +-----------+                          +-----------+
| SensorConnector |                 | IncomingParser  |                      | BaseTest  |                          | Database  |
+-----------------+                 +-----------------+                      +-----------+                          +-----------+
        |                                  |                                     |                                      |
        | Acquire raw sensor data          |                                     |                                      |
        |------------------------          |                                     |                                      |
        |                       |          |                                     |                                      |
        |<-----------------------          |                                     |                                      |
        |                                  |                                     |                                      |
        | Clean raw incoming data          |                                     |                                      |
        |--------------------------------->|                                     |                                      |
        |                                  |                                     |                                      |
        |                                  | Allow basetest to take action       |                                      |
        |                                  |------------------------------------>|                                      |
        |                                  |                                     |                                      |
        |                                  |                                     | Interpret data and use in test       |
        |                                  |                                     |-------------------------------       |
        |                                  |                                     |                              |       |
        |                                  |                                     |<------------------------------       |
        |                                  |                                     |                                      |
        |                                  |                                     | Store sensor data                    |
        |                                  |                                     |------------------------------------->|
        |                                  |                                     |                                      |
        |                                  |                                     | Perform test                         |
        |                                  |                                     |-------------                         |
        |                                  |                                     |            |                         |
        |                                  |                                     |<------------                         |
        |                                  |                                     |                                      |
        |                                  |                                     | Store test data                      |
        |                                  |                                     |------------------------------------->|
        |                                  |                                     |                                      |

```

Entry point is creating a `main_test` 

Example:
