import discord # discordpy library | windows: py -3 -m pip install -U discord.py
from io import StringIO
import sys
from itertools import product

client = discord.Client()
# mini methode die alle permutationen von 1 und 0 erstellt für die notwendigen variablen
generator = lambda l: product([1,0], repeat=l)

#test
# diese klasse wird später das objekt dass alle variablen erhält
# die variablen werden während runtime erstellt 
class Vars:
    pass


def draw(expr): # expr = liste von strings zb: ['A or B', 'not (A or B)']
    vars = [] # diese liste beinhaltet alle variablen der tabelle
    for ex in expr:
        if ';' in ex: 
            # da der input string weiter unten in eine exec() methode rein gesteckt wird
            # will ich nicht das man mehrere zeilen injecten kann deswegen ist das ; verboten
            print('no code injection my friend...')
            return
        # hier wird geguckt welche variablen verwendet werden in den ausdrücken
        for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if c in ex and not c in vars:
                vars.append(c)
    # die instanz die die variablen bekommen wird
    vobj = Vars()
    # hier werden zuerst alle variablen geprintet 
    # zb: | A | B 
    [print(f'| {v} ', end='') for v in vars]
    # zb: | A | B |
    print(end='|')
    # hier nun alle expressions
    # zb: # | A | B | A or B | not (A or B) |
    [print(f' {ex} |', end='') for ex in expr]
    print('\n')
    # ls ist eine liste mit den längen des strings der expressions
    # um später die absstände richtig zu machen
    ls = [len(ex) for ex in expr]
    for i in range(len(vars)):
        for j in range(len(expr)):
            # dynamisch erstellte variablen können nur mit getattr erhalten werden
            # deswegen wird jedes A mit einem "getattr(vobj, vars[0])" ausgetauscht
            expr[j] = expr[j].replace(vars[i], f'getattr(vobj, vars[{i}])')
    # hier werden iterativ die restlichen zeilen geprintet
    # vobei perm immer eine permutation ist also zb: (1, 1)
    [drawLine(vobj, expr, vars, perm, ls) for perm in generator(len(vars))]

def drawLine(vobj, expr, vars, perm, ls):
    # hier erhalten alle variablen ihren wert der in perm generiert wurde
    [setattr(vobj, vars[i], perm[i]) for i in range(len(vars))]
    # jetzt werden die werte geprintet
    # zb: | 1 | 1  
    [print(f'| {getattr(vobj, v)} ', end='') for v in vars]
    print(end='| ')
    # und hier werden die expressions ausgeführt und dann auch geprintet
    [exec(f'print(int({ex}), end=\'\'); [print(\' \', end=\'\') for _ in range({l})]; print(end=\'| \')', {'vobj':vobj, 'vars':vars}) for ex, l in zip(expr, ls)]
    print()

@client.event
async def on_ready():
    print('ready!')
    
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('/booltable'):
        msg = message.content[11:]
        print(f'$bot: receiving request: "bt>{msg[:(min(len(msg), 15))]}"')
        sys.stdout = mout = StringIO()
        print('```Elixir')
        draw([s.strip() for s in msg.split(',')])
        print(end='```')
        sys.stdout = sys.__stdout__
        print('$bot: successfully parsed a request by', str(message.author)[:-5])
        await message.channel.send(mout.getvalue())
    # so kann man checken ob der bot online ist
    elif message.content.startswith('/test'):
        await message.channel.send('```Elixir\ntest```')
