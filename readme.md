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
