from throttle_controller import ThrottleController
import time

print("Hello AutoThrottle")

the_throttle_controller = ThrottleController(
    port_string="/dev/ttyUSB0",
    config_file="./cfg/throttle_config.json",
    servo_number=1,
)
start = time.time()
while True:
    current = time.time() - start
    ThrottleController.logger.info(f"Sim Time: {current}")
    if not the_throttle_controller.run():
        break
