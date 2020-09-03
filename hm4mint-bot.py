import discord # discordpy library | windows: py -3 -m pip install -U discord.py
from io import StringIO
import sys
from itertools import product

mout = StringIO()
client = discord.Client()
# mini methode die alle permutationen von 1 und 0 erstellt für die notwendigen variablen
generator = lambda l: product([1,0], repeat=l)

# diese klasse wird später das objekt dass alle variablen erhält
# die variablen werden während runtime erstellt 
class Vars:
    def __init__(self):
        self._r=1
    
    
def interpret(ex, vars):
    for i in range(len(vars)):
        # dynamisch erstellte variablen können nur mit getattr erhalten werden
        # deswegen wird jedes A mit einem "getattr(vobj, vars[0])" ausgetauscht
        ex = ex.replace(vars[i], f'getattr(vobj, vars[{i}])')
    # backslashes werden rausgefiltert damit man discords formatting escapen kann
    return ex.replace('\\', '')

def draw(expr): # expr = liste von strings zb: ['A or B', 'not (A or B)']
    vars = [] # diese liste beinhaltet alle variablen der tabelle
    for ex in expr:
        if ';' in ex or 'exit' in ex: 
            # da der input string weiter unten in eine exec() methode rein gesteckt wird
            # will ich nicht das man mehrere zeilen injecten kann deswegen ist das ; verboten
            print('no code injection my friend...')
            return
        # hier wird geguckt welche variablen verwendet werden in den ausdrücken
        [vars.append(c) for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if c in ex and not c in vars]
    # die instanz die die variablen bekommen wird
    vobj = Vars()
    # hier werden zuerst alle variablen geprintet 
    # zb: A | B |
    [print(end=f' {v} |') for v in vars]
    # hier nun alle expressions
    # zb: #  A | B || A or B | not (A or B) |
    [print(end=f'| {ex} ') for ex in expr]
    print('\n')
    # ls ist eine liste mit den längen des strings der expressions
    # um später die absstände richtig zu machen
    ls = [len(ex) for ex in expr]
    for i in range(len(expr)):
        # hier wird jede expression einmal durchleuchtet um fehler zu vermeiden
        expr[i] = interpret(expr[i], vars)  # expr[j].replace(vars[i], f'getattr(vobj, vars[{i}])')
        print('expr: ', expr[i], file=sys.stderr)
    # hier werden iterativ die restlichen zeilen geprintet
    # vobei perm immer eine permutation ist also zb: (1, 1)
    [drawLine(vobj, expr, vars, perm, ls) for perm in generator(len(vars))]

def drawLine(vobj, expr, vars, perm, ls):
    # hier erhalten alle variablen ihren wert der in perm generiert wurde
    [setattr(vobj, vars[i], perm[i]) for i in range(len(vars))]
    # jetzt werden die werte geprintet
    # zb: | 1 | 1  
    [print(end=f' {getattr(vobj, v)} |') for v in vars]
    # und hier werden die expressions ausgeführt und dann auch geprintet
    for ex, l in zip(expr, ls):
        exec(f'setattr(vobj, \'_r\', str(int({ex})))', {'vobj':vobj, 'vars':vars})
        print(end='| {} {}'.format(vobj._r, ''.join([' ' for _ in range(l - len(vobj._r))])))
    #[exec(f'print(\'|\', int({ex}), end=\'\'); [print(end=\' \') for _ in range({l})]', {'vobj':vobj, 'vars':vars}) for ex, l in zip(expr, ls)]
    print()

@client.event
async def on_ready():
    print('ready!')
    sys.stdout = mout
    
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('/booltable'):
        msg = message.content[11:]
        mout.truncate(0)
        print(f'$bot: receiving request: "{msg[:(min(len(msg), 15))].strip()}..."', file=sys.__stdout__)
        print('```Elixir')
        try:
            draw([s.strip() for s in msg.split(',')])
        except:
            mout.truncate(10)
            print('invalid input:', msg)
            raise            
        else:
            print('$bot: successfully parsed a request by', str(message.author)[:-5], file=sys.__stdout__)
        finally:
            print(end='```')
            await message.channel.send(mout.getvalue())
    # so kann man checken ob der bot online ist
    elif message.content.startswith('/test'):
        await message.channel.send('```Elixir\ntest```')
