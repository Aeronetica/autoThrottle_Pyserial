from throttle_controller import ThrottleController

print("Hello AutoThrottle")

the_throttle_controller = ThrottleController(
    port_string="/dev/tty-coupler-autothrottle",
    config_file="./cfg/throttle_config.json",
    servo_number=1,
)

while True:
    if not the_throttle_controller.run():
        break
