import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('strings', nargs='+')

args = parser.parse_args()
print(len(args.strings))
print(args.strings)
print(args.strings[1])

