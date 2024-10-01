"""color related methods"""
import random


def generate_random_color():
    """Generates a random hexadecimal color code"""
    color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
    return color
