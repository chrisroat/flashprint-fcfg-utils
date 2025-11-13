# flashforge-fcfg-utils

Convert FlashPrint fcfg config files to/from JSON.

You may want to use this because the fcfg files are not human-readable, and the
JSON format will allow you to easily make small tweaks and understandable diffs.

## Setup

```sh
pipenv install
pipenv shell  # Start shell within python env
```

## Convert exported fcfg file to JSON

```sh
python fcfg.py fcfg2json Standard.fcfg Standard.json
```

## Convert JSON to fcfg file

```sh
python fcfg.py json2fcfg Standard.json Standard_roundtrip.fcfg
```

## Notes

A roundtrip conversion will not produce identical files, since the
FlashPrint exporter is not consistent with out it encodes/decodes
bytes.  A best effort was made to replicate the most consistent
behavior.  A few quick tests indicate the fcfg files created with
this file are still readable by FlashPrint.
