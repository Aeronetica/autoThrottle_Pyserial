from src.throttle_controller import ThrottleController
import time
import json

print("Hello AutoThrottle")

the_throttle_controller = ThrottleController(
    port_string="/dev/tty-coupler-autothrottle",
    config_file="./cfg/throttle_config.json",
    servo_number=1,
)
start = time.time()
with open("./cfg/throttle_config.json", encoding="utf_8") as fp:
    params = json.load(fp)
"To print the current servo position press 'p'"
"To print the current simulation time press 't'"
"To move the servo to the command position specified in the throttle_config.json file press 'c'"
while True:
    current = time.time() - start
    the_throttle_controller.logger.debug(f"Sim Time: {current}")
    the_throttle_controller.full_position = -1
    if not the_throttle_controller.run():
        break
    print(
        f"Current Servo Position is {the_throttle_controller.return_dict['position']}"
    )
