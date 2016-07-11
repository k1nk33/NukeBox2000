# -*- coding: utf-8 -*-

import click
from NukeBox import main as nb_main

@click.command()
def main(args=None):
    """Console script for nukebox2000"""
    click.echo("NukeBox 2000 Server Up!")
    #click.echo("See click documentation at http://click.pocoo.org/")
    nb_main()


if __name__ == "__main__":
    main()
