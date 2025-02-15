from utils import get_nationalities


nationalities = get_nationalities()


with open("./VERSION", "r") as f:
    VERSION = f.read()