import re
import time
import pygame
import asyncio
import textwrap

class room:
    def __init__(self, name, discription, poss_actions=None, leave_condition=None, container=None):
        self.name = name
        self.poss_actions = poss_actions if poss_actions is not None else []
        self.leave_condition = leave_condition
        self.container = container
        self.discription = discription

        self.neighbors = {}
        self.text_entered = []

    def add_neighbor(self, heding, destination):
        self.neighbors[heding] = destination

    def get_destination(self, heading):
        return self.neighbors.get(heading)

class Leave_condition:
    def __init__(self, have_to_be_done, heding, reason=None):
        self.have_to_be_done = have_to_be_done
        self.heding = heding
        self.reason = reason

class Container:
    def __init__(self, name, in_items):
        self.name = name 
        self.in_items = in_items if in_items is not None else []

class MainGame:
    def __init__(self):

        coffin = room('coffin', 'coffin', ['punch'])
        coffin.leave_condition = Leave_condition('punch', 'up')

        graveyard = room('graveyard', 'graveyard', [''])
        graveyard.container = Container('tree', ['paper_graveyard','key_graveyard'])

        path = room('path', 'path',[''])
        path.leave_condition = Leave_condition('use_key_graveyard_east', 'east' , 'locked')

        library_entrance = room('library', 'library', [''])

        library_entrance_east = room('library_entrance_east', 'library_entrance_east', [''])
        library_entrance_east.container = Container('bookshelf', ['map_library_entrance_east'])

        library_entrance_north = room('library_entrance_north', 'library_entrance_north', [''])
        library_entrance_north.container = Container('bookshelf',['plant_library_entrance_north', 'clock_library_entrance_north', 'newspaper_library_entrance_north'])

        stairway = room('stairway','stairway',[''])

        library_second_floor_entrance = room('library_second_floor_entrance', 'library_second_floor_entrance', [''])



        # adding naighbors
        coffin.add_neighbor('up',graveyard)
        graveyard.add_neighbor('down',coffin)
        graveyard.add_neighbor('east',path)
        path.add_neighbor('west',graveyard)
        path.add_neighbor('east',library_entrance)
        library_entrance.add_neighbor('west',path)
        library_entrance.add_neighbor('east', library_entrance_east)
        library_entrance.add_neighbor('north', library_entrance_north)
        library_entrance.add_neighbor('north west', stairway)
        library_entrance_east.add_neighbor('west', library_entrance)
        library_entrance_north.add_neighbor('south', library_entrance)
        stairway.add_neighbor('up', library_second_floor_entrance)
        stairway.add_neighbor('down', library_entrance)
        library_second_floor_entrance.add_neighbor('north west', stairway)

        # dictionarys

        self.text = {}
        
        # player veriable
        self.location = coffin
        self.game_runing = True
        self.inventory = []
        self.game_over = False
        self.inventory_open = False

        self.messages = []

    def play_sound(self, sound_file):
        """Play a sound effect."""
        try:
            pygame.mixer.init()
            sound = pygame.mixer.Sound(sound_file)
            sound.play()
        except Exception as e:
            self.write(f"Error playing sound: {e}")

    def write(self, message=""):
        """Add text to the game window's message log."""
        self.messages.append(str(message))

        # all prints must becom ^^^

    def update(self):
        if self.location.leave_condition:
            condition = self.location.leave_condition.have_to_be_done

            if condition in self.location.text_entered:
                if not self.location.discription.endswith('_' + condition):
                    self.location.discription += '_' + condition
    
    def caveman_parse(self, words):
        words = words.lower()
        words = re.sub(r'\b(?:door|in|a|at|the|and|on|[|])\b', '', str(words)).strip()
        return words.split()

    def handle_command(self, words):
        command = self.caveman_parse(words)

        if not command:
            return

        universal_commands = ['help', 'look', 'go', 'take', 'open']

        if command[0] in self.location.poss_actions or command[0] in universal_commands:
            self.location.text_entered.append(command[0])
            if command[0] == 'help':
                self.help()
                self.play_sound('/Users/elliotghall/Desktop/CSCI 157 Advent semester/Purgastory_web_deployed/web/game/sounds/chimessf.oog')
            elif command[0] == 'look':
                second = command[1] if len(command) > 1 else None
                self.look(second)
            elif command[0] == 'go':
                if len(command) > 1:
                    self.go(command[1])
                    self.play_sound('/Users/elliotghall/Desktop/CSCI 157 Advent semester/Purgastory_web_deployed/web/game/sounds/chimesfx.oog')
                else:
                    self.write('Go where?')
                    self.play_sound('/Users/elliotghall/Desktop/CSCI 157 Advent semester/Purgastory_web_deployed/web/game/sounds/errordurmbSFX.oog')
            elif command[0] == 'punch':
                self.write('You punch with all your might')
            elif command[0] == 'take':
                if len(command) > 1:
                    self.take(command[1])
                    self.play_sound('/Users/elliotghall/Desktop/CSCI 157 Advent semester/Purgastory_web_deployed/web/game/sounds/chimesfx.oog')
                else:
                    self.write('Take what?')
                    self.play_sound('/Users/elliotghall/Desktop/CSCI 157 Advent semester/Purgastory_web_deployed/web/game/sounds/errordurmbSFX.oog')
            elif command[0] == 'open' and len(command) >1 and command[1] == 'inventory':
                self.open_inventory()
            else:
                self.write('ERROR 1')
                self.play_sound('/Users/elliotghall/Desktop/CSCI 157 Advent semester/Purgastory_web_deployed/web/game/sounds/errordurmbSFX.oog')
        else:
            self.write(command[0] + 'is not a command in posibal actions')


    # inventory commands
    # inventory functions
    def open_inventory(self):
        self.inventory_open = True
        self.inven_look()

    def inven_look(self):
        self.write('You have')
        for item in self.inventory:
            self.write('- ' + item)
        self.write('in your inventory')

    def inven_handel_command(self, command):
        command = self.caveman_parse(command)

        if not command:
            return
        if command[0] == 'help':
            self.inven_help()
        elif command[0] == 'close' and len(command) > 1 and command[1] == 'inventory':
            self.inventory_open = False
            self.write('You close your inventory.')
        elif command[0] == 'inspect' and len(command) == 2:
            self.inven_inspect(command[1])
        elif command[0] == 'use' and len(command) > 2:
            self.inven_use(command[1], command[2])
        else:
            self.write('Unknown inventory command.')

    def inven_use(self, item, heading):
        text = 'use_' + item + '_' + heading

        if item not in self.inventory and item + '_' + self.location.name not in self.inventory:
            self.write("You don't have that item.")
            return

        if not self.location.leave_condition:
            self.write("You can't use that here.")
            return

        if text == self.location.leave_condition.have_to_be_done:
            self.location.text_entered.append(text)
            self.say(text)
        else:
            self.write('You cannot use the ' + item + ' here.')
            
    def inven_inspect(self,item):
        self.say(item + '_inspect')      

    def inven_help(self):
        self.write('inventory commands: \n - help \n - close inventory \n - use (item) \n - inspect (item)')
   
    ###
   
    def take(self,item):
        nacheral_name = item
        # item = item + '_' + self.location.name
        if self.location.container:
            if item in self.location.container.in_items:
                self.location.container.in_items.remove(item)
                self.inventory.append(item)
                self.write('You take the ' + nacheral_name)
        else:
            self.write("there is no " + nacheral_name + ' hear' )

    def help(self):
        self.write('You can:')
        for action in self.location.poss_actions:
            self.write('- ' + action)

    def go(self, heading):
            destination = self.location.get_destination(heading)
            if destination:
                if self.location.leave_condition != None:
                    if self.check_leave_condition(heading):
                        self.location = destination
                        self.actions = []
                    else:
                        self.say('go_fail leave condition')
                else:
                    self.location = destination
                    self.actions = []
            else:
                self.say('go_fail no destination')

    def check_leave_condition(self,heding):
        if not self.location.leave_condition:
            return True
        
        condition = self.location.leave_condition.have_to_be_done
        if condition in self.location.text_entered or heding != self.location.leave_condition.heding:
            return True
        else:
            return False

    # look functions

    def look(self,second=None):
        if second and second == self.location.container.name:
            if self.location.container:
                words = (str(self.location.discription)+ '_' + str(self.location.container.name))

                for item in self.location.container.in_items:
                    words += ' ' + item

                self.write('inside there is' + words)
        
        else: 
            self.say(self.location.discription)
            exits = self.get_exits()
            if exits == []:
                self.write('there are no exits')
            else:
                self.write('there are exits to the' + str(exits))

    def get_exits(self):
        exits = list(self.location.neighbors.keys())

        if self.location.leave_condition:
            if self.location.leave_condition.have_to_be_done not in self.location.text_entered:
                heading = self.location.leave_condition.heding

                if heading in exits:
                    exits.remove(heading)
            if self.location.leave_condition.reason:
                if self.location.leave_condition.reason == 'locked':
                    exits.append('the door to the ' + str(self.location.leave_condition.heding) + ' is locked')


        return exits



    # text handaling fuctions    
    # creating a list of printable items in the game from 1 txt fiel.         
    
            
    def txtParser(self):
        in_file = open('/Users/elliotghall/Desktop/CSCI 157 Advent semester/Purgastory_web_deployed/web/game/2.3.txt', 'r')
        cline = in_file.readline().strip('\n')
        if cline == 'START':
            self.write('.txt captured')
        while cline != 'END':
            cline = in_file.readline().strip('\n')
            if cline == '[':
                dictionary_name = in_file.readline().strip('\n')
                cline = in_file.readline().strip('\n')
                self.text[dictionary_name] = []
                while cline != ']':               
                    self.text[dictionary_name].append(cline.strip(']'))
                    cline = in_file.readline().strip('\n')
        in_file.close()

    def say(self, key):
        key = key.lower().split('__')

        for x in range(len(key)):
            if key[x] in self.text:
                text = '\n'.join(self.text[key[x]])

                words = text.split(maxsplit=2)

                if words[0] == 'typewriter':
                    for character in words[2]:
                        self.write(character, end='', flush=True)
                        time.sleep(float(words[1]))

                    self.write()
                    self.write()

                else:
                    self.write(text)

            else:
                thing = ('No text found for key:', key[x])
                self.write(thing)

    def say_title_card(self):
        self.play_sound('/Users/elliotghall/Desktop/CSCI 157 Advent semester/Purgastory_web_deployed/web/game/sounds/slowjingle(birth).oog')
        self.say('title_card_1')
        self.say('title_card_2')
        self.say('title_card_3')

    async def run(self):
            """Read keyboard events and draw the game without blocking."""
            pygame.init()
            screen = pygame.display.set_mode((960, 640))
            pygame.display.set_caption("Dungeon Adventure")
            # The built-in font needs no separate font file.
            font = pygame.font.Font(None, 28)
            clock = pygame.time.Clock()
            command = ""
            running = True

            self.txtParser()
            self.say_title_card()
            self.look()

            # Keep drawing after a win/loss so the final message stays visible.
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            if self.inventory_open:
                                self.inventory_open = False
                            else:
                                running = False
                        elif not self.game_over:
                            if event.key == pygame.K_RETURN:
                                self.write("> " + command)
                                if self.inventory_open:
                                    self.inven_handel_command(command)
                                else:
                                    self.handle_command(command)
                                command = ""
                                if not self.game_over:
                                    self.write(
                                        f"You are in the {self.location.name}." # !!!!!!!!!!!!!!!!! could chang o upda to creat location surface
                                    )
                            elif event.key == pygame.K_BACKSPACE:
                                command = command[:-1]
                            elif event.unicode.isprintable():
                                command = (command + event.unicode)[:60]

                screen.fill((20, 24, 32))

                # Wrap messages and show only the most recent lines.
                lines = []
                for message in self.messages:
                    lines.extend(textwrap.wrap(message, width=65) or [""])
                for index, line in enumerate(lines[-17:]):
                    surface = font.render(line, True, (235, 235, 235))
                    screen.blit(surface, (24, 20 + index * 30))

                if self.inventory_open:
                    inventory_text = ["--- INVENTORY ---"]

                    for item in self.inventory:
                        inventory_text.append("- " + item)

                    inventory_text.append("Commands: help, inspect, use, close inventory")

                    for i, line in enumerate(inventory_text):
                        surface = font.render(line, True, (180, 220, 180))
                        screen.blit(surface, (650, 100 + i * 30))

                if self.game_over:
                    prompt = "Game ended. Refresh to restart; Esc closes the game."
                else:
                    prompt = "> " + command + "_"
                surface = font.render(prompt, True, (150, 220, 180))
                screen.blit(surface, (24, 590))
                pygame.display.flip()
                clock.tick(30)
                # Give the browser a turn on every frame.
                await asyncio.sleep(0)

            pygame.quit()

game = MainGame()
asyncio.run(game.run())
