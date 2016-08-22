create a service file in '/home/services/'

'''
[Unit]
Description=Battery 1 test
After=network.target

[Service]
User=sander
WorkingDirectory=<script location>
ExecStart=<venv folder>/bin/python <script location>/start.py --config="config.json"

[Install]
WantedBy=multi-user.target
'''


sudo systemctl enable /home/services/<service>

