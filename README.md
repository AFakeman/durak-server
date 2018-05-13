# A custom game server for the game Durak.

## Requirements

* `Docker` and `docker-compose` supporting config version 3

## Usage

* Edit `static_server/static/durak/servers.json` to point to the IP of your
  machine  

* If you want to use a local server, replace `mitm` in  `durak/Dockerfile` with
  `durak`

* Edit `dns/dnsmasq.hosts` to point to the same IP  

* Set up your phone to use your computer as a primary DNS server  

* `docker-compose up --build`  

* Start the app on your device

* Pick the `Custom Server` in the game

* Enjoy!
