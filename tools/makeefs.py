#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
import argparse
import os.path


def print8(*args):
    print " ".join(unicode(x).encode(u"utf-8") for x in args)


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument(u"-v", u"--verbose", action=u"store_true",
                   help=u"Verbose output.")
    p.add_argument(u"longshort", choices=[u"long", u"short"])
    p.add_argument(u"output")
    p.add_argument(u"files", nargs=u"+")
    args = p.parse_args([x.decode(u"utf-8") for x in argv[1:]])
    
    lengths = list()
    files = list()
    for filename in args.files:
        with open(filename, "rb") as f:
            files.append(f.read())
            lengths.append(len(files[-1]))
    
    if len(files) < 256:
        files.extend([""] * (256 - len(files)))
        lengths.extend([0] * (256 - len(lengths)))
    
    banks = list()
    offsets = list()
    bank = 0
    offset = 0x8000 + len(files) * 4
    if args.longshort == u"long":
        offset += len(files)
    for i, length in enumerate(lengths):
        banks.append(bank)
        offsets.append(offset)
        offset += length
        while offset >= 0xa000:
            offset -= 0x2000
            bank += 1
    
    output = [
        "".join(chr(x) for x in banks),
        "".join(chr(x & 0xff) for x in offsets),
        "".join(chr(x >> 8) for x in offsets),
        "".join(chr(x & 0xff) for x in lengths),
    ]
    if args.longshort == u"long":
        output.append("".join(chr(x >> 8) for x in lengths))
    
    output.extend(files)
    data = "".join(output)
    pad = "\xff"
    padded_data = data + pad * 0x2000
    with open(args.output, "wb") as f:
        for offset in xrange(0, len(data), 0x2000):
            f.write(padded_data[offset:offset + 0x2000])
            f.write(pad * 0x2000)
    
    return 0
    

if __name__ == '__main__':
    sys.exit(main(sys.argv))
    
