from apa102_pi.driver.apa102 import APA102
strip = APA102(num_led=3, global_brightness=15)
for i in range(3):
    strip.set_pixel(i, 0, 255, 0)
strip.show()
