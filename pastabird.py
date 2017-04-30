#!/usr/bin/python3

import os
import subprocess
import argparse
import textwrap
import re
import requests
import pyperclip
import magic
import webbrowser

def bpastePrint(url):
    bpasteRegex = re.compile('/show/')
    url = bpasteRegex.sub('/raw/', url)
    print(requests.get(url).text)

def isText(path):
    mime, enc, name = magic.detect_from_filename(os.path.abspath(path))
    return True if 'text' in name else False

def pasteBuilder(paths, paste='', recursive=False):
    for p in paths:
        if os.path.exists(p):
            if os.path.isfile(p):
                if os.path.basename(p)[0] != '.' and isText(p):
                    paste = paste + "\n\n" + p.center(70) + "\n" + open(p).read()
            elif recursive is True:
                if not os.path.basename(p) or os.path.basename(p)[0] != '.':
                    paste = paste + pasteBuilder([os.path.join(p,x) for x in os.listdir(p)], paste, True)
            else:
                print(p + ' is a directory.  Use -r (--recursive) flag to paste recursively.')
        else:
            print(p + ': No such file or directory.')
    return paste

parser = argparse.ArgumentParser(description='multiservice paste uploader', prog='pastabird')
parser.add_argument('-b', '--browser', action="store_true",
                    help='open paste in browser')
parser.add_argument('-c', '--clipboard', action='store_true',
                    help='paste from clipboard')
parser.add_argument('-l', '--lexer', default='text',
                    help='set lexer (defaults to plaintext)')
parser.add_argument('-r', '--recursive', action='store_true',
                    help='paste directories recursively')
parser.add_argument('-s', '--service', default='bpaste',
                    help='service to upload paste')
parser.add_argument('-u', '--url-to-clipboard', action='store_true',
                    help='copy resulting paste url to clipboard')
parser.add_argument('-x', '--expires', default='1day',
                   help='set expiration')
parser.add_argument('path', metavar='PATH', nargs='*',
                    help='path to paste(s)')
parser.add_argument('-p', '--print-from-url', nargs='*',
                    help='print paste(s) from url(s)')


args = parser.parse_args()

services = {'bpaste': 'https://bpaste.net/'}

service = services[vars(args)['service']]

clip_paste = pyperclip.paste() if vars(args)['clipboard'] else ''

clip_paste = "\n".join(textwrap.wrap(clip_paste, width=70))

paste = pasteBuilder(vars(args)['path'], recursive=vars(args)['recursive'])

paste = clip_paste + paste

if paste is '' and len(vars(args)['print_from_url']) == 0:
    print('empty paste')
    quit()

if vars(args)['expires'] != '1day' and vars(args)['expires'] in ['1day', '1week', '1month', 'never']:
    expiry = vars(args)['expires']
else:
    expiry = '1day'

lexer = vars(args)['lexer']

r = requests.post(service, data={'code': paste, 'lexer': lexer, 'expiry': expiry})

if r.ok:
    print(r.url)
    if vars(args)['url_to_clipboard']:
        pyperclip.copy(r.url)
    if vars(args)['browser']:
        webbrowser.open(r.url)
else:
    print('something went wrong ;~;')

if vars(args)['print_from_url']:
    for url in vars(args)['print_from_url']:
        bpastePrint(url)
