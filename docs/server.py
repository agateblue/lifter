#!/usr/bin/env python
"""
Build and serve the documentation,
Will livereload the documentation on any rst change
also open a webbrowser
"""
from livereload import Server, shell
import sys
import os
import webbrowser


def main():

    build_project_path = '_build'
    if not os.path.exists(build_project_path):
        os.system('make html')

    server = Server()
    server.watch('*.rst', shell('make html'))
    webbrowser.open_new_tab('http://127.0.0.1:5500')
    server.serve(root='_build/html')

main()
