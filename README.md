# Parser for Purdy pedigrees

This program expects a csv with two fields, line name and pedigree

# Usage

Here is a simple example:

```python3 parsePed.py -f ped.csv -o test -r "\s*F1" \"```

- the `-f` specifies the file to be parsed
- the `-o` specifies the output file name
- the `-r` specifies patterns that should be removed before parsing
	. in this case, remove `, F1` or `,F1`, as well as any double quotes, `"`

## to see optional arguments

```python3 parsePed.py --help```