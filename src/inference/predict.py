
import torch
import torch.utils.data
from torch.nn.utils.rnn import pad_sequence
import numpy as np
import json
import string
import os
from dotenv import load_dotenv
from errors import InferenceError
from model import ConvLSTM as Model
import unicodedata
import re


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def load_json(file_path: str) -> dict:
    """
    Loads content from a JSON file.
    :param file_path: Path the the JSON file
    :return: JSON content as a dictionary
    """

    with open(file_path, "r") as f:
        return json.load(f)

    
def replace_special_chars(name: str) -> str:
    """
    Replaces all apostrophe letters with their base letters and removes all other special characters incl. numbers
    :param str name: name
    :return str: normalized name
    """

    name = u"{}".format(name)
    name = unicodedata.normalize("NFD", name).encode("ascii", "ignore").decode("utf-8")
    name = re.sub("[^A-Za-z -]+", "", name)

    return name


def preprocess_names(names: list=[str], batch_size: int=128) -> torch.tensor:
    """
    Creates a pytorch-usable input-batch from a list of string-names
    :param list names: list of names (strings)
    :param int batch_size: batch-size for the forward pass
    :return torch.tensor: preprocessed names (to tensors, padded, encoded)
    """

    sample_batch = []
    for name in names:
        # normalize name to only latin characters
        name = replace_special_chars(name)

        # create index-representation from string name, ie: "joe" -> [10, 15, 5], indices go from 1 ("a") to 28 ("-")
        alphabet = list(string.ascii_lowercase.strip()) + [" ", "-"]
        int_name = []
        for char in name:
            int_name.append(alphabet.index(char.lower()) + 1)
        
        name = torch.tensor(int_name)
        sample_batch.append(name)

    padded_batch = pad_sequence(sample_batch, batch_first=True)

    padded_to = list(padded_batch.size())[1]
    padded_batch = padded_batch.reshape(len(sample_batch), padded_to, 1).to(device=device)

    if padded_batch.shape[0] == 1 or batch_size == padded_batch.shape[0]:
        padded_batch = padded_batch.unsqueeze(0)
    else:
        padded_batch = torch.split(padded_batch, batch_size)

    return padded_batch


def predict(input_batch: torch.tensor, model_config: dict, classes: dict, with_distribution: bool=False) -> str:
    """ load model and predict preprocessed name

    :param torch.tensor input_batch: input-batch
    :param str model_path: path to saved model-paramters
    :param dict classes: a dictionary containing all countries with their class-number
    :param with_distribution: Wether to return the entire distribution of the predicted nationalities
    :return str: predicted ethnicities
    """

    # prepare model (map model-file content from gpu to cpu if necessary)
    model = Model(
        class_amount=model_config["amount-classes"], 
        embedding_size=model_config["embedding-size"],
        hidden_size=model_config["hidden-size"],
        layers=model_config["rnn-layers"],
        kernel_size=model_config["cnn-parameters"][1],
        channels=model_config["cnn-parameters"][2]
    ).to(device=device)


    model_path = model_config["model-file"]

    if device != "cuda:0":
        model.load_state_dict(torch.load(model_path, map_location={"cuda:0": "cpu"}))
    else:
        model.load_state_dict(torch.load(model_path))

    model = model.eval()

    # classify names    
    total_predicted_ethncitities = []

    for batch in input_batch:
        predictions = model(batch.float())

        # convert numerics to country name
        predicted_ethnicites = []
        for idx in range(len(predictions)):
            prediction = predictions.cpu().detach().numpy()[idx]
            prediction_idx = list(prediction).index(max(prediction))
            ethnicity = list(classes.keys())[list(classes.values()).index(prediction_idx)]
            predicted_ethnicites.append([ethnicity, round(100 * float(np.exp(max(prediction))), 3)])

        total_predicted_ethncitities += predicted_ethnicites

    return total_predicted_ethncitities


def run_inference(model_id: str, names: list[str], with_distribution: bool=False) -> list[str]:
    """
    Preprocesses and predicts the names.
    :param model_id: The ID of the model to use
    :param names: A list of all names which are to classify
    :param with_distribution: Wether to return the entire distribution of the predicted nationalities
    :return: List of the predicted nationalities (and optionally the entire output distr.)
    """

    load_dotenv()

    MAX_NAMES = int(os.getenv("MAX_NAMES"))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE"))

    model_config = load_json(f"nec-classification/nec_user_models/{model_id}/config.json")
    classes = load_json(f"nec-classification/nec_user_models/{model_id}/dataset/nationalities.json")
    model_file = f"nec-classification/nec_user_models/{model_id}/model.pt"

    if len(names) > MAX_NAMES:
        raise InferenceError(
            error_code="TOO_MANY_NAMES",
            message=f"Too many names (maximum {MAX_NAMES}.")

    # preprocess inputs
    input_batch = preprocess_names(names=names, batch_size=BATCH_SIZE)

    model_config = {
        "model-file": model_file,
        "amount-classes": len(classes),
        "embedding-size": model_config["embedding-size"],
        "hidden-size": model_config["hidden-size"],
        "rnn-layers": model_config["rnn-layers"],
        "cnn-parameters": model_config["cnn-parameters"]
    }

    # predict ethnicities
    return predict(input_batch, model_config, classes)
