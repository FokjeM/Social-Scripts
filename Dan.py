# Dan's view on the Person class made for Dan
class Person():
    def __init__(self, name: str):
        self.name = name
        self.malding = False
        self._stop_mald = False

    def mald():
        if self._stop_mald: return False
        self.malding = True
        return True

Dan = Person("Dan")
def main():
    if Dan.malding:
        Dan._stop_mald = True
        while not Dan._stop_mald:
            Dan.mald()

import asyncio
asyncio.run(main)