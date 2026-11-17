import re
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
        library_entrance.leave_condition = Leave_condition('use_key_bookshelf_south', 'south', 'locked')

        library_entrance_east = room('library entrance east', 'library_entrance_east', ['enter_password'])
        library_entrance_east.leave_condition = Leave_condition('PAIN - LESS', 'east', 'padlock')

        library_entrance_east_bookshelf = room('library entrance east bookshelf', 'library_entrance_east_bookshelf', [''])
        library_entrance_east_bookshelf.container = Container('bookshelf', ['map_library_entrance_east', 'dictionarys'])

        library_entrance_north = room('library entrance north', 'library_entrance_north', [''])
        library_entrance_north.container = Container('bookshelf',['plant_library_entrance_north', 'key_bookshelf', 'clock_library_entrance_north', 'newspaper_library_entrance_north'])

        stairway = room('stairway','stairway',[''])

        library_second_floor_entrance = room('library upstairs', 'library_second_floor_entrance', [''])
        library_second_floor_entrance.container = Container('desk_upstairs',['paper_desk'])

        library_second_floor_north = room('second floor northern wall', 'library_second_floor_north', [''] )
        library_second_floor_north.container = Container('drawer',['key_upstairs_desk'])

        thired_floor_stairway = room('thired floor stairway', 'thired_floor_stairway')



        # adding naighbors
        coffin.add_neighbor('up',graveyard)

        graveyard.add_neighbor('down',coffin)
        graveyard.add_neighbor('east',path)

        path.add_neighbor('west',graveyard)
        path.add_neighbor('east',library_entrance)

        library_entrance.add_neighbor('west',path)
        library_entrance.add_neighbor('east', library_entrance_east)
        library_entrance.add_neighbor('north', library_entrance_north)
        library_entrance.add_neighbor('south', stairway)

        library_entrance_east.add_neighbor('west', library_entrance)
        library_entrance_east.add_neighbor('east', library_entrance_east_bookshelf)

        library_entrance_east_bookshelf.add_neighbor('west', library_entrance_east)

        library_entrance_north.add_neighbor('south', library_entrance)

        stairway.add_neighbor('up', library_second_floor_entrance)
        stairway.add_neighbor('down', library_entrance)

        library_second_floor_entrance.add_neighbor('south', stairway)
        library_second_floor_entrance.add_neighbor('west', thired_floor_stairway)
        library_second_floor_entrance.add_neighbor('north', library_second_floor_north)

        library_second_floor_north.add_neighbor('south', library_second_floor_entrance)

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
                self.play_sound('sounds/chimesfx.ogg')
            elif command[0] == 'look':
                second = command[1] if len(command) > 1 else None
                self.look(second)
            elif command[0] == 'go':
                if len(command) > 1:
                    if self.go(command[1]):
                        self.play_sound('sounds/chimesfx.ogg')
                    else:
                        self.play_sound('sounds/errordurmbSFX.ogg')
                else:
                    self.write('Go where?')
                    self.play_sound('sounds/errordurmbSFX.ogg')
            elif command[0] == 'punch':
                self.write('You punch with all your might')
                if self.location.name == 'coffin':          
                    self.location.discription = 'coffin_punch'
            elif command[0] == 'take':
                if len(command) > 1:
                    self.take(command[1])
                    self.play_sound('sounds/chimesfx.ogg')
                else:
                    self.write('Take what?')
                    self.play_sound('sounds/errordurmbSFX.ogg')
            elif command[0] == 'open' and len(command) >1 and command[1] == 'inventory':
                self.open_inventory()
            elif command[0] == 'enter_password':
                if len(command) > 1:
                    self.enter_password(' '.join(command[1:]))
                else:
                    self.write('Enter the password.')
            elif command[0] == 'use':
                self.write('that is an inventory command pleas open inventory to use it')
            else:
                self.write('ERROR 1')
                self.play_sound('sounds/errordurmbSFX.ogg')
        else:
            self.write(command[0] + ' is not somthing you can do here')

    def enter_password(self, password):
        if password.replace('-', '').replace(' ', '').lower() == 'painless':
            self.location.text_entered.append('PAIN - LESS')
            self.write('The padlock clicks open!')
        else:
            self.write('Incorrect password.')

    # inventory commands
    # inventory functions
    def open_inventory(self):
        self.inventory_open = True
        #self.inven_look()

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
        elif command[0] == 'use' :
            if len(command) > 2:
                self.inven_use(command[1], command[2])
            else:
                self.write('the format for the use command is use (item name) (direction to use item in)')
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
        self.write('inventory commands:')
        for line in ['help', 'close inventory', 'use (item) (direction)', 'inspect (item)']:
            self.write('- ' + line)
   
    ###
   
    def take(self,item):
        nacheral_name = item
        if self.location.container:
            if item in self.location.container.in_items:
                self.location.container.in_items.remove(item)
                self.inventory.append(item)
                self.write('You take the ' + nacheral_name)
            else:
                self.write("there is no " + nacheral_name + ' here' )
        else:
            self.write('there is nothing to take here')

    def help(self):
        self.write('You can:')
        for action in ['look, if you whant to look at an object enter: look (object name)', 'go', 'take', 'open inventory', 'object names are exact and include underscours'] + self.location.poss_actions:
            if action:
                self.write('- ' + action)

    def go(self, heading):
        destination = self.location.get_destination(heading)
        if destination:
            if self.location.leave_condition is None or self.check_leave_condition(heading):
                self.location = destination
                self.look()
                if self.location.name == 'thired floor stairway':
                    self.game_over = True
                return True
            self.say('go_fail leave condition')
            return False
        self.say('go_fail no destination')
        return False

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
        if second and self.location.container and second == self.location.container.name:
            if self.location.container:
                words = (str(self.location.discription)+ '_' + str(self.location.container.name))

                self.say(words)

                for item in self.location.container.in_items:
                    self.write('- ' + item + '\n')
                
        
        else: 
            self.say(self.location.discription)
            exits = self.get_exits()
            if exits == []:
                self.write('there are no exits')
            else:
                self.write('there are exits to the ' + ', '.join(exits))

    def get_exits(self):
        exits = list(self.location.neighbors.keys())
        if self.location.leave_condition is None:
            return exits

        condition = self.location.leave_condition.have_to_be_done
        heading = self.location.leave_condition.heding


        if condition not in self.location.text_entered:
            if heading in exits:
                exits.remove(heading)
            if self.location.leave_condition.reason == 'locked':
                exits.append('the door to the ' + str(heading) + ' is locked')
            if self.location.leave_condition.reason == 'padlock':
                exits.append('enter the password to the padlock to acces the bookshelf')

        return exits



    # text handaling fuctions    
    # creating a list of printable items in the game from 1 txt fiel.         
    
            
    def txtParser(self):
        in_file = open('2.3.txt', 'r', encoding='utf-8')
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

                self.write(text)

            else:
                thing = ('No text found for key:', key[x])
                self.write(thing)

    async def say_title_card(self):
        self.play_sound('sounds/slowjingle(birth).ogg')
        for i in range(6):
            self.say('title_card_' + str(i))
            await asyncio.sleep(.5)

    async def intro(self):
        await self.say_title_card()
        self.look()

    async def run(self):
                #Read keyboard events and draw the game without blocking.
            pygame.init()
            screen = pygame.display.set_mode((1420, 780))
            mini_map = pygame.Surface((300, 50), pygame.SRCALPHA)
            pygame.draw.rect(mini_map, (194, 194, 194), (0, 0, 300, 50), border_radius=12)
            pygame.display.set_caption("Dungeon Adventure")
            # The built-in font needs no separate font file.
            font = pygame.font.Font("SpecialElite-Regular.ttf", 18)
            font_small =pygame.font.Font("Dongle-Light.ttf", 30)
            clock = pygame.time.Clock()
            command = ""
            running = True

            self.txtParser()
            self.intro_task = asyncio.create_task(self.intro())

            # Keep drawing after a win/loss so the final message stays visible.
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            if self.inventory_open:
                                self.inventory_open = False
                        elif not self.game_over:
                            if event.key == pygame.K_RETURN:
                                self.write("> " + command)
                                if self.inventory_open:
                                    self.inven_handel_command(command)
                                else:
                                    self.handle_command(command)
                                command = ""
                                #if not self.game_over:
                                    #self.write(
                                    #    f"You are in the {self.location.name}." # !!!!!!!!!!!!!!!!! could chang o upda to creat location surface
                                    #)

                            elif event.key == pygame.K_BACKSPACE:
                                command = command[:-1]
                            elif event.unicode.isprintable():
                                command = (command + event.unicode)[:101]

                self.update()

                screen.fill((20, 24, 32))

                # --- draw agselery gui ---
                screen.blit(mini_map, (650, 20))

                # Wrap messages and show only the most recent lines.
                lines = []
                for message in self.messages:
                    lines.extend(textwrap.wrap(message, width=101) or [""])
                    lines.append("")  # Add a blank line after each message.
                for index, line in enumerate(lines[-17:]):
                    surface = font.render(line, True, (235, 235, 235))
                    screen.blit(surface, (24, 90 + index * 30))

                pygame.draw.line(screen, (80, 85, 100), (975, 0), (975, 780), 2)

                inventory_text = ["--- INVENTORY ---"]
                for item in self.inventory[:20]:
                    inventory_text.append("- " + item)

                for i, line in enumerate(inventory_text):
                    surface = font.render(line, True, (255, 115, 28))
                    screen.blit(surface, (995, 20 + i * 30))

                # command hint pinned to the bottom of the panel
                for i, line in enumerate(["Commands: you must first open the inventory", "with open inventory", "help, inspect, use,", "close inventory = esc key or writen command"]):
                    surface = font.render(line, True, (255, 115, 28))
                    screen.blit(surface, (995, 660 + i * 30))

                if not self.game_over:
                    mini_map.fill((0, 0, 0, 0))
                    pygame.draw.rect(mini_map, (194, 194, 194), (0, 0, 300, 50), border_radius=12)
                    location_surface = font_small.render('Location:' + str(self.location.name), True, (255, 117, 7))
                    mini_map.blit(location_surface, (10, 6))

                if self.game_over:
                    prompt = "Congratulations, you have escaped Purgastory! Use this second chance wisely… the original plane was for the game to be longer but we ran out of time"

                else:
                    if self.inventory_open:
                        prompt = "(inventory command)> " + command + "_"
                    else:
                        prompt="> " + command + "_"
                if self.inventory_open:
                    surface = font.render(prompt, True, (255, 115, 28))
                else:
                    surface = font.render(prompt, True, (150, 220, 180))
                screen.blit(surface, (24, 750))
                pygame.display.flip()
                clock.tick(30)
                # Give the browser a turn on every frame.
                await asyncio.sleep(0)

            pygame.quit()

game = MainGame()
asyncio.run(game.run())