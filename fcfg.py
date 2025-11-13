#!/usr/bin/env python3
import json

import click

from parse_lib import fcfg_to_value, value_to_fcfg


@click.group()
def cli():
    """fcfg conversion utilities."""


@cli.command()
@click.argument("infile", type=click.File())
@click.argument("outfile", type=click.File("w"))
def fcfg2json(infile, outfile):
    """Convert an .fcfg file to JSON.

    infile: input .fcfg file
    outfile: output JSON file
    """
    cfg = {}
    stanza = None
    for line in infile:
        line = line.strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            stanza = line[1:-1]
            cfg.setdefault(stanza, {})
            continue

        key, val = fcfg_to_value(line)
        cfg[stanza][key] = val

    json_output = json.dumps(cfg, indent=2)
    outfile.write(json_output)


@cli.command()
@click.argument("infile", type=click.File())
@click.argument("outfile", type=click.File("w"))
def json2fcfg(infile, outfile):
    """Convert a JSON file to .fcfg.

    INFILE: input JSON file
    OUTFILE: output .fcfg file
    """
    cfg = json.load(infile)

    for stanza, items in cfg.items():
        outfile.write(f"[{stanza}]\n")
        for key, val in items.items():
            rhs = value_to_fcfg(val)
            outfile.write(f"{key}={rhs}\n")
        outfile.write("\n")


if __name__ == "__main__":
    cli()
