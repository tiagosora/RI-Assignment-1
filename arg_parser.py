import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--f", type=str, default="", help="File name")
    return parser.parse_args()
