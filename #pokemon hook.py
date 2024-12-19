#pokemon hook
from pymem import Pymem
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from icecream import ic
from pokedata import Pokedata
import csv
import time
import pokegui

pokemon_info: dict = {}
interval: float = 1 / 2 #Pokemon RBY run at 30fps, but doesn't need to be updated this quickly
poke_team = []
active_player_pokemon = {}

with open('PokemonIndex.csv', 'r', encoding='utf-8-sig') as pokeinfo:
    reader = csv.DictReader(pokeinfo)
    for row in reader:
        pokemon_info[row['Hex'].lower()] = {
            'Name' : row['Pokemon'], 
            'Pokedex #' : row['Pokedex'], 
            'Type 1' : row['Type 1'],
            'Type 2' : row['Type 2']
            }

try:
    pokehook = Pymem('VisualBoyAdvance.exe')
    print('Process id: %s' % pokehook.process_id)
except Exception as e:
    print(e)
    eg.msgbox(msg='VisualBoyAdvance process not found. Exiting.', title='Error', ok_button='Okay')
    exit()

pattern = bytes.fromhex('C35001CEED6666CC0D') #bytes that are located at the beginning of Pokemon R/B's ROM

pokerom_start = pokehook.pattern_scan_all(pattern, return_multiple = False) - 0x101
    
    #search byte data in known locations in memory where the version name appears and set version accordingly
if 'RED' in pokehook.read_bytes(pokerom_start + 0x134, 12).decode('utf-8'):
    version = 'Pokemon Red'
if 'BLUE' in pokehook.read_bytes(pokerom_start + 0x134, 12).decode('utf-8'):
    version = 'Pokemon Blue'

if 'Red' in version or 'Blue' in version:
    pattern_d_area = bytes.fromhex('A1A727AF27') #bytes that are located at the beginning of Pokemon R/B's WRAM
    pokewram_start = pokehook.pattern_scan_all(pattern_d_area, return_multiple = False) - 0x00B0 #set starting address to 0x0000

ic(pokehook.read_bytes(pokerom_start + 0x0134, 12).decode('utf-8'))
first_poke = str(pokehook.read_bytes((pokewram_start + 0X16B), 1).hex())
ic(pokemon_info[first_poke]['Name'])


class Pokeparty:
    
    active_player_pokemon = {}
    POKE_OFFSETS: list[hex] = [0x16B, 0x197, 0x1C3, 0x1EF, 0x21B, 0x247]

    statuses = ['Asleep', 'Asleep', 'Asleep', 'Poisoned', 'Burned', 'Frozen', 'Paralyzed']

    stat_offets: list[dict[str: hex, int]] = [
        #stat,   [offset, read length]
        #these are your first pokemon's stats WHILE IN THE OVERWORLD / NOT IN BATTLE
        {'pokemon' : [0x16B, 1],
         'current_hp' : [0x16C, 2], #length 2 bytes
         'status' : [0x16F, 1],
         'move_1' : [0x173, 1],
         'pp_1' : [0x188, 1],
         'move_2' : [0x174, 1],
         'pp_2' : [0x189, 1],
         'move_3' : [0x175, 1],
         'pp_3' : [0x18A, 1],
         'move_4' : [0x176, 1],
         'pp_4' : [0x18B, 1],
         'attack' : [0x18F, 2], #length 2 bytes
         'defense' : [0x191, 2], #length 2 bytes
         'speed' : [0x193, 2], #length 2 bytes
         'special' : [0x195, 2] #length 2 bytes
    }
    ]                              

    battle_offsets: list[dict[str: hex, int]] = [
        { #these are where your active pokemon's stats are located WHILE IN BATTLE
         'name' : [0x009, 10], #length 10 bytes
         'pokemon' : [0x014, 1], #internal ID of pokemon
         'max_hp' : [0x023, 2], #length 2 bytes
         'current_hp' : [0x015, 2], #length 2 bytes
         'status' : [0x018, 1], #this value gets put through check_status to figure out the actual status
         'move_1' : [0x01C, 1],
         'pp_1' : [0x02D, 1],
         'move_2' : [0x01D, 1],
         'pp_2' : [0x02E, 1],
         'move_3' : [0x01E, 1],
         'pp_3' : [0x02F, 1],
         'move_4' : [0x01F, 1],
         'pp_4' : [0x030, 1],
         'attack' : [0x025, 2], #length 2 bytes
         'defense' : [0x027, 2], #length 2 bytes
         'speed' : [0x029, 2], #length 2 bytes
         'special' : [0x02B, 2], #length 2 bytes
         'level' : [0x022, 1]
        }
    ]

    def check_player_poke_status(status):
        status_string = format(status[0], '08b')
        reversed_string = status_string[::-1]
        ic(status_string)
        #pokemon can only have 1 status at a time. bits 0-2 are sleep counter, all others are statuses.
        if '1' in reversed_string:
            status_index = reversed_string.index('1')
            if status_index <= 2:
                Pokeparty.active_player_pokemon['status'] = f'Asleep for {status_index} more turn(s).'
            else:
                Pokeparty.active_player_pokemon['status'] = Pokeparty.statuses[status_index]
        else:
            Pokeparty.active_player_pokemon['status'] = 'Normal'

    def get_team_info(): #used to get stats out of battle
        for i in range(6):
            if str(pokehook.read_bytes((pokewram_start + Pokeparty.POKE_OFFSETS[i]), 1).hex()) in pokemon_info:
                if not poke_team:
                    poke_team.append(pokemon_info[str(pokehook.read_bytes((pokewram_start + Pokeparty.POKE_OFFSETS[i]), 1).hex())])
                else:
                    poke_team[i] = pokemon_info[str(pokehook.read_bytes((pokewram_start + Pokeparty.POKE_OFFSETS[i]), 1).hex())]
                for x, y in Pokeparty.stat_offets[i].items():
                    ic(x, y)
                    poke_team[i][x] = int.from_bytes((pokehook.read_bytes((pokewram_start + y[0]), y[1])) , byteorder= 'big')

    def get_battle_info():
        if str(pokehook.read_bytes((pokewram_start + Pokeparty.battle_offsets[0]['pokemon'][0]), 1).hex()) in pokemon_info:
               # if not active_player_pokemon:
                #    active_player_pokemon = (pokemon_info[str(pokehook.read_bytes((pokewram_start + Pokeparty.battle_offsets[0]['pokemon'][0]), 1).hex())])
                #else:
                Pokeparty.active_player_pokemon['pokemon'] = pokemon_info[str(pokehook.read_bytes((pokewram_start + Pokeparty.battle_offsets[0]['pokemon'][0]), 1).hex())]
                for x, y in Pokeparty.battle_offsets[0].items():
                    ic(x, y)
                    if x != 'status' and x != 'name':
                        Pokeparty.active_player_pokemon[x] = int.from_bytes((pokehook.read_bytes((pokewram_start + y[0]), y[1])) , byteorder= 'big')
                    elif x == 'status':
                        ic(pokehook.read_bytes((pokewram_start + y[0]), y[1]))
                        Pokeparty.check_player_poke_status(pokehook.read_bytes((pokewram_start + y[0]), y[1]))
                    elif x == 'name':
                        #Pokeparty.active_player_pokemon['name'] = str(pokehook.read_bytes(pokewram_start + y[0], y[1]).hex())
                        Pokeparty.active_player_pokemon['name'] = pokemon_info[first_poke]['Name']
        ic(Pokeparty.active_player_pokemon)


if __name__ == '__main__':
    root = pokegui.start_root()
    root.withdraw()
    pokeparty = Pokeparty
    pokegui = pokegui.PokeGUI(root, pokeparty)
    
    root.mainloop()