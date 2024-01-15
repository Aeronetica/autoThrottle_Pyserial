from throttle_controller import ThrottleController
print("Hello AutoThrottle")

the_throttle_controller = ThrottleController(port_string="COM6", config_file="throttle_config.json", servo_number=1)

while True:
    if (not the_throttle_controller.run())

