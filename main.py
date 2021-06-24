from pprint import pprint

from utils.date_detector import DateDetector

detector = DateDetector()

while True:
    x = input(">")
    if x == 'stop':
        break

    pprint(detector.find_all(x))
