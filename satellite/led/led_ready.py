from apa102_pi.driver.apa102 import APA102
strip = APA102(num_led=3, global_brightness=10)
for i in range(3):
    strip.set_pixel(i, 0, 200, 200)  # cyan
strip.show()
