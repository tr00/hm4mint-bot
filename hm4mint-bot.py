import discord
from io import StringIO
import sys
from itertools import product

client = discord.Client()

generator = lambda l: product([1,0], repeat=l)


class Vars:
    pass


def draw(expr):
    vars = []
    for ex in expr:
        if ';' in ex:
            print('no code injection my friend...')
            return
        for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if c in ex and not c in vars:
                vars.append(c)
    vobj = Vars()
    [print(f'| {v} ', end='') for v in vars]
    print(end='|')
    [print(f' {ex} |', end='') for ex in expr]
    print('\n')
    ls = [len(ex) for ex in expr]
    for i in range(len(vars)):
        for j in range(len(expr)):
            expr[j] = expr[j].replace(vars[i], f'getattr(vobj, vars[{i}])')
    [drawLine(vobj, expr, vars, perm, ls) for perm in generator(len(vars))]

def drawLine(vobj, expr, vars, perm, ls):
    [setattr(vobj, vars[i], perm[i]) for i in range(len(vars))]
    [print(f'| {getattr(vobj, v)} ', end='') for v in vars]
    print(end='| ')
    [exec(f'print(int({ex}), end=\'\'); [print(\' \', end=\'\') for _ in range(l)]; print(end=\'| \')', {'l':l, 'vobj':vobj, 'vars':vars}) for ex, l in zip(expr, ls)]
    print()

@client.event
async def on_ready():
    print('ready!')
    
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('/booltable'):
        print()
        sys.stdout = mout = StringIO()
        print('```Elixir')
        draw([s.strip() for s in message.content[11:].split(',')])
        print(end='```')
        sys.stdout = sys.__stdout__
        await message.channel.send(mout.getvalue())
