from throttle_controller import ThrottleController
import time
import json

print("Hello AutoThrottle")

the_throttle_controller = ThrottleController(
    port_string="/dev/ttyUSB0",
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
    if not the_throttle_controller.run():
        break
    the_throttle_controller.logger.debug(f"Sim Time: {current}")
    if 2.0 < current < 4.0:
        the_throttle_controller.full_position = -1
    else:
        the_throttle_controller.full_position = params["full_position"]
    if current < 2.0 or current > 4.0:
        print(
            "Current Servo Position is %d",
            the_throttle_controller.message_dict["servo_position"],
        )
    # if keyboard.is_pressed("t"):
    #     the_throttle_controller.logger.warn(f"Sim Time: {current}")
