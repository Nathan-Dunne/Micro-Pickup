# Author: Nathan Dunne
# Date 30/04/2019
# Purpose: Program a micro:bit to play a game where you walk in cardinal directions to pick up items.
# This application is licensed under the Creative Commons Zero v1.0 Universal, public domain.
# Comments are excluded hereafter due to Micro:bit memory limitations (16KB static RAM).

from microbit import compass, accelerometer, sleep
import microbit
import math
import random

MAX_POSITION = 4
MIN_POSITION = 0
SCREEN_CENTER = 2
draw_pixel = microbit.display.set_pixel


class Position:
    x = 0
    y = 0


class GameObject:

    position = Position()
    brightness = 0


class Player(GameObject):

    def __init__(self):
        self.position.x = SCREEN_CENTER
        self.position.y = SCREEN_CENTER
        self.brightness = 9

    def reset(self):
        self.position.x = SCREEN_CENTER
        self.position.y = SCREEN_CENTER

    def move(self, direction):
        if direction == "N":
            self.position.y = self.constrainToBoundaries(self.position.y - 1)
        elif direction == "S":
            self.position.y = self.constrainToBoundaries(self.position.y + 1)
        elif direction == "W":
            self.position.x = self.constrainToBoundaries(self.position.x - 1)
        elif direction == "E":
            self.position.x = self.constrainToBoundaries(self.position.x + 1)

    def draw(self):
        draw_pixel(self.position.x, self.position.y, self.brightness)

    def constrainToBoundaries(self, value):
        if value < MIN_POSITION:
            return MIN_POSITION
        if value > MAX_POSITION:
            return MAX_POSITION

        return value


class Pickup(GameObject):

    def __init__(self):
        self.position = Position()
        self.position.x = random.randrange(MAX_POSITION + 1)
        self.position.y = random.randrange(MAX_POSITION + 1)
        self.brightness = 3


class Game:
    player = Player()
    pickups = []
    game_running = True
    acceleration_needed_to_move = 1200

    def __init__(self):
        self.setup()

    def spawnPickups(self, amount):
        self.pickups.clear()

        for x in range(amount):
            new_pickup = Pickup()

            self.pickups.append(new_pickup)

    def drawPickups(self):
        for pickup in self.pickups:
            draw_pixel(pickup.position.x, pickup.position.y, pickup.brightness)

    def findApproxFacingDirection(self):
        cardinal_direction = ""

        if compass.heading() > 315 or compass.heading() < 45:
            cardinal_direction = "N"
        elif compass.heading() > 225 and compass.heading() < 315:
            cardinal_direction = "W"
        elif compass.heading() > 135 and compass.heading() < 225:
            cardinal_direction = "S"
        elif compass.heading() > 45 and compass.heading() < 135:
            cardinal_direction = "E"

        return cardinal_direction

    def getAcceleration(self):
        x = accelerometer.get_x()
        y = accelerometer.get_y()
        z = accelerometer.get_z()

        acceleration = math.sqrt(x ** 2 + y ** 2 + z ** 2)

        return acceleration

    @staticmethod
    def setup():
        if not compass.is_calibrated():
            compass.calibrate()

    def update(self):
        for pickup in self.pickups:
            if pickup.position.x == self.player.position.x:
                if pickup.position.y == self.player.position.y:
                    self.pickups.remove(pickup)

    def startLevel(self, pickup_amount):

        self.spawnPickups(pickup_amount)
        self.player.reset()

        microbit.display.clear()

    def getInput(self):
        direction = self.findApproxFacingDirection()

        if self.getAcceleration() > self.acceleration_needed_to_move:
            self.player.move(direction)

        if microbit.button_b.was_pressed():
            scroll_delay = 100
            microbit.display.scroll(self.findApproxFacingDirection(), scroll_delay)
        elif microbit.button_a.was_pressed():
            compass.calibrate()

    def draw(self):
        microbit.display.clear()
        self.drawPickups()
        self.player.draw()

    def isGameOver(self):
        is_pickups_empty = len(self.pickups) < 1

        if is_pickups_empty:
            return True
        else:
            return False

    def playGame(self):
        microbit.display.scroll("WALK TO PICK UP ITEMS.")

        pickup_amount = 4

        while self.game_running:

            self.startLevel(pickup_amount)
            level_start_time = microbit.running_time()

            while not self.isGameOver():
                self.getInput()
                self.update()
                self.draw()

                if self.isGameOver():
                    current_time = microbit.running_time()
                    seconds_elapsed = (current_time - level_start_time) / 1000

                    microbit.display.scroll("TIME:" + str(int(seconds_elapsed)) + " SECONDS.")

                    pickup_amount += 1

                sleep(100)


def main():
    game = Game()
    game.playGame()


if __name__ == "__main__":
    main()