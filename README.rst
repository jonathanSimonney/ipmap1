==============
J2ELA - A server status monitor
==============


to use this repository as a non developer user, please download it, create a venv
(check https://docs.python.org/3/library/venv.html to create it, it is really easy...), activate this venv (same link),
and then, go with the same cmd, move to the folder containing this project (the one with requirements.txt in it),
and launch the command : "pip install -r requirements.txt".

Once this is done, run python server.py --host=your_host --port=port_number.
This will start a web server on the host and port specified, and if you go to
your_server_host:your_server_port/nrange_param, you'll see the json for the
Nmap -sV of the parameter you gave. (it is a list of the data taken port by port, or null if the port didn't respond.)