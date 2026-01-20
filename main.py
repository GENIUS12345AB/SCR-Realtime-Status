import time
import requests
import src.web as web
import src.setup as setup
import pypresence
from src.logger import log
from src.prettyprint import startup
from pathlib import Path
import json
import sys

HUBSITE_VERSION = "v2.3.0.230"
SCRRTS_VERSION = "v1.0.0"
START_TIME = time.time()
BUTTONS = [{"label": "Get SCR Realtime Status", "url": "https://github.com/GENIUS12345AB/SCR-Realtime-Status"}]
GAME_ICON = requests.get(url=f"https://thumbnails.roblox.com/v1/games/icons?universeIds=300039023&returnPolicy=PlaceHolder&size=150x150&format=Png&isCircular=false").json()['data'][0]['imageUrl']

startup(HUBSITE_VERSION, SCRRTS_VERSION)

while not Path("config.json").exists():
	log.warning("Configuration file does not exist.")
	setup.create_configuration()

with open('config.json') as f:
    config = json.load(f)

try:
	SCRHubSite = web.SCRScraper()
	log.info("Connecting to discord")
	client = pypresence.Client(config['settings']['clientid'])
	client.start()
except Exception as e:
	log.fatal(e)
	sys.exit(1)

log.info("SCR Realtime Status Active! Press Ctrl+C to exit...")

try:
	while True:
		SCRHubSite.UpdateLiveActivity()
		
		# Driving Status
		if SCRHubSite.activity_type == 'Driving':
			client.set_activity(
				name=f"Driving to {SCRHubSite.destinaton}",
				state=f"{SCRHubSite.current_status} [{SCRHubSite.headcode}]",
				details=f"Service to {SCRHubSite.destinaton}",
				large_image=GAME_ICON,
				buttons=BUTTONS,
				start=START_TIME
			)
		
		# Dispatching Status
		elif SCRHubSite.activity_type == "Dispatching":
			if SCRHubSite.current_status == "Selecting a station":
				client.set_activity(
					details="Selecting a station to dispatch",
					large_image=GAME_ICON,
					buttons=BUTTONS,
					start=START_TIME
				)
			else:
				client.set_activity(
					name=f"Dispatching at {SCRHubSite.station}",
					details=f"Platforms {SCRHubSite.platforms} (Group {SCRHubSite.group})",
					state=f"{SCRHubSite.trains_dispatched} trains dispatched",
					large_image=GAME_ICON,
					buttons=BUTTONS,
					start=START_TIME
				)
		
		# Guarding Status
		elif SCRHubSite.activity_type == "Guarding":
			if SCRHubSite.current_status == "Selecting a train":
				client.set_activity(
					details="Selecting a train to guard",
					large_image=GAME_ICON,
					buttons=BUTTONS,
					start=START_TIME
				)
			else:
				client.set_activity(
					name=f"Guarding [{SCRHubSite.headcode}]",
					details=f"Service to {SCRHubSite.destinaton}",
					state=SCRHubSite.current_status,
					large_image=GAME_ICON,
					buttons=BUTTONS,
					start=START_TIME
				)
		
		# Misc Status
		elif SCRHubSite.activity_type == "Signalling":
			client.set_activity(
				name="Signalling in SCR",
				details="Operating a signalling desk",
				large_image=GAME_ICON,
				buttons=BUTTONS,
				start=START_TIME
			)
		else:
			client.set_activity(
				details="In the main menu",
				large_image=GAME_ICON,
				buttons=BUTTONS,
				start=START_TIME
			)
		time.sleep(1)
except KeyboardInterrupt:
    log.info("Closing connection...")
    client.clear_activity()
    client.close()
    log.info("Disconnected from Discord.")