#!/usr/bin/env python
import os
import re
import sys
import subprocess
sys.dont_write_bytecode = True

def main():
    # registry of commands
    g = globals()
    cmds = dict([(i[4:],g[i]) for i in g if i.startswith('cmd_')])
    # if curl URL | python2 then use command setup
    if len(sys.argv) == 1 and __file__ == '<stdin>':
        cmd_setup()
    elif len(sys.argv) == 2 and sys.argv[1] in cmds:
        cmds[sys.argv[1]]()
    else:
        import manager
        manager.cli.main()

if __name__ == "__main__":
    main()
