# -*- coding: utf-8 -*-

import click
from nukebox2000 import main as nb_main

@click.command()
def main(args=None):
    """Console script for nukebox2000"""
    click.echo("Replace this message by putting your code into "
                "nukebox2000.cli.main")
    click.echo("See click documentation at http://click.pocoo.org/")


if __name__ == "__main__":
    nb_main()
