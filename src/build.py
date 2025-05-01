import sys
from model import Model

if __name__ == "__main__":
    name = sys.argv[1]
    if name == "null":
        Model.train()
    else:
        Model.train(sys.argv[1])