# Author: Nathan Dunne
# Date 30/04/2019
# Purpose: Program a micro:bit to play a game where you walk in cardinal directions to pick up items.
# This application is licensed under the Creative Commons Zero v1.0 Universal, public domain.

# Import the libraries needed for the application to function.
from microbit import compass, accelerometer, sleep
import microbit  # MicroPython API.
import math  # Need this to use a square root function in finding acceleration.
import random  # Used to randomly place the pickups.

# Define the max and minimum x and y values that can be used.
MAX_POSITION = 4
MIN_POSITION = 0
SCREEN_CENTER = 2  # (2,2:x,y) is the center of the screen
draw_pixel = microbit.display.set_pixel  # A quick macro to reduce statement size needed to turn on an LED.


class Position:  # Position of a GameObject.
    x = 0
    y = 0


class GameObject:  # The GameObject parent class of Player and Pickup.

    position = Position()
    brightness = 0


class Player(GameObject):

    completion_time = 0  # The time to complete the level.

    # Initiate the class with the following definitions.
    def __init__(self):
        self.position.x = SCREEN_CENTER  # Place them at the centre of the screen.
        self.position.y = SCREEN_CENTER
        self.brightness = 9  # The maximum brightness of an LED is 9.

    # Reset the player, for use when staring a new level.
    def reset(self):
        self.completion_time = 0
        self.position.x = SCREEN_CENTER
        self.position.y = SCREEN_CENTER

    # Given a cardinal direction, move the player based on that direction.
    def move(self, direction):
        if direction == "N":
            self.position.y = self.constrainToBoundaries(self.position.y - 1)  # Move up on the display.
        elif direction == "S":
            self.position.y = self.constrainToBoundaries(self.position.y + 1)  # Move down.
        elif direction == "W":
            self.position.x = self.constrainToBoundaries(self.position.x - 1)  # Move left.
        elif direction == "E":
            self.position.x = self.constrainToBoundaries(self.position.x + 1)  # Move right.

    # Turn on the player LED at their x and y position, using their brightness.
    def draw(self):
        draw_pixel(self.position.x, self.position.y, self.brightness)

    # When the player wants to move, check if that movement would put them outside the boundaries.
    @staticmethod
    def constrainToBoundaries(value):
        if value < MIN_POSITION:
            return MIN_POSITION
        if value > MAX_POSITION:
            return MAX_POSITION

        return value


# The pick-up object that players need to move over.
class Pickup(GameObject):

    def __init__(self):
        self.position = Position()
        self.position.x = random.randrange(MAX_POSITION + 1)  # Set their x to a random value between 0 and 4.
        self.position.y = random.randrange(MAX_POSITION + 1)  # Set their y to a random value between 0 and 4.
        self.brightness = 3  # Set the pickup brightness a bit lower to help the player see which LED they are on.

# The main controller class.
class Game:
    player = Player()  # Instantiate a player object.
    pickups = []  # Instantiate a container for the pickups to be stored in.
    game_running = True  # Start the game running. (Will always be true, no functionality is provided to quit.)
    acceleration_needed_to_move = 1200  # The acceleration that the user must reach to move the player.

    def __init__(self):
        self.setup()  # Run essential setup.

    # Spawn the pickups around the display.
    def spawnPickups(self, amount):
        self.pickups.clear()  # Make sure the pickup container is empty before spawning new ones.

        for x in range(amount):  # Do this operation the amount of times passed in to the function.
            new_pickup = Pickup()  # Instantiate a new pickup.

            self.pickups.append(new_pickup)  # Add it to the pickup container for storage and later processing.

    # Display the pickups on the screen.
    def drawPickups(self):
        for pickup in self.pickups:  # For each pickup stored in the pickup container.
            draw_pixel(pickup.position.x, pickup.position.y, pickup.brightness) # Turn on the LED at their position.

    # Get the approximate facing direction of the user.
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

    # Get the current acceleration of the user. Resting acceleration is a value of 1000 milli-g, acceleration due to gravity.
    def getAcceleration(self):
        x = accelerometer.get_x()
        y = accelerometer.get_y()
        z = accelerometer.get_z()

        acceleration = math.sqrt(x ** 2 + y ** 2 + z ** 2)  # ** means make this a power of.

        return acceleration

    @staticmethod
    def setup():
        if not compass.is_calibrated():  # The compass must be calibrated for the application to function correctly.
            compass.calibrate()

    # Check if the player is on top of a pickup.
    def update(self):
        for pickup in self.pickups:
            if pickup.position.x == self.player.position.x:
                if pickup.position.y == self.player.position.y:
                    self.pickups.remove(pickup)

    # Start the level.
    def startLevel(self, pickup_amount):

        self.spawnPickups(pickup_amount)
        self.player.reset()

        microbit.display.clear()  # Turn off all LEDs.

    def getInput(self):
        direction = self.findApproxFacingDirection()  # Get the direction the user is facing.

        if self.getAcceleration() > self.acceleration_needed_to_move:  # If they are moving fast enough.
            self.player.move(direction)   # Move them in that direction.

        if microbit.button_b.was_pressed():
            scroll_delay = 100
            microbit.display.scroll(self.findApproxFacingDirection(), scroll_delay)  # Show "N" for example.
        elif microbit.button_a.was_pressed():
            compass.calibrate()

    def draw(self):
        microbit.display.clear()
        self.drawPickups()
        self.player.draw()

    def isGameOver(self):
        is_pickups_empty = len(self.pickups) < 1  # Check if the pickup container is empty.

        if is_pickups_empty:
            return True
        else:
            return False

    def playGame(self):
        microbit.display.scroll("WALK TO PICK UP ITEMS.")

        pickup_amount = 4

        while self.game_running:

            self.startLevel(pickup_amount)
            level_start_time = microbit.running_time()  # Store the time when the user starts a level.

            # Execute a traditional game loop.
            while not self.isGameOver():
                self.getInput()
                self.update()
                self.draw()

                if self.isGameOver():
                    current_time = microbit.running_time()  # Get the time at gameover.
                    seconds_elapsed = (current_time - level_start_time) / 1000  # Convert milliseconds to seconds.

                    # Display the time it took to complete the level, cut off any decimal places from the print-out.
                    microbit.display.scroll("TIME:" + str(int(seconds_elapsed)) + " SECONDS.")

                    pickup_amount += 1

                sleep(100)


def main():
    game = Game()  # Instantiate the game.
    game.playGame()  # Play the game!

# Find the main function, run it.
if __name__ == "__main__":
    main()