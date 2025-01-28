from utils import get_nationalities
import json

nationalities = get_nationalities()



api_config = json.load(open("./data/api_config.json", "r"))