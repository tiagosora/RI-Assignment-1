import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--a", type=str, default="", help="Argument A")
    parser.add_argument("-b", "--b", type=int, default=0, help="Argument B")
    return parser.parse_args()
