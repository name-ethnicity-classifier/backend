
import torch
import torch.utils.data
from torch.nn.utils.rnn import pad_sequence
import numpy as np
import string
import os
import unicodedata
import re
from dotenv import load_dotenv
from errors import InferenceError
from inference.model import ConvLSTM as Model
from utils import load_json


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


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


def classify_names(input_batch: torch.tensor, model_config: dict, classes: dict, get_distribution: bool=False) -> str:
    """ load model and predict preprocessed name

    :param torch.tensor input_batch: input-batch
    :param str model_path: path to saved model-paramters
    :param dict classes: a dictionary containing all countries with their class-number
    :param get_distribution: Wether to return the entire distribution of the predicted nationalities
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

    total_predicted_ethncitities = []

    # classify names and store results
    for batch in input_batch:
        predictions = model(batch.float()).cpu().detach().numpy()

        # get entire ethnicity confidence distribution for each name
        if get_distribution:
            prediction_result = get_ethnicity_distributions(predictions, classes=classes)
        # get the ethnicity with the highest confidence for each name
        else:
            prediction_result = get_ethnicity_predictions(predictions, classes=classes)

        total_predicted_ethncitities.extend(prediction_result)

    return total_predicted_ethncitities


def get_ethnicity_predictions(predictions: np.array, classes: list) -> list[str]:
    """
    Collects the highest confidence ethnicity for every prediction in a batch.
    For example if the model classified a batch of two names into eithher "german" or "greek":
    > [(german, 0.9), (greek, 0.8)]

    :param predictions: The output predictions of the model
    :param classes: A list containing all the classes which a model can classify
    :return: A list containing the predicted ethnicity and confidence score for each name
    """

    predicted_ethnicites = []
    for prediction in predictions:
        prediction_idx = list(prediction).index(max(prediction))
        ethnicity = classes[prediction_idx]
        predicted_ethnicites.append((ethnicity, round(100 * float(np.exp(max(prediction))), 3)))

    return predicted_ethnicites


def get_ethnicity_distributions(predictions: np.array, classes: list) -> list[dict]:
    """
    Collects the entire output distribution for every predictions in a batch
    For example if the model classified a batch of two names into eithher "german" or "greek":
    > [{german: 0.9, greek: 0.1}, {german: 0.2, greek: 0.8}]

    :param predictions: The output predictions of the model
    :param classes: A list containing all the classes which a model can classify
    :return: A list containing an output distribution for each name
    """

    predicted_ethnicites = []

    for prediction in predictions:
        ethnicity_distribution = {}
        for idx, ethnicity in enumerate(classes):
            confidence = round(100 * float(np.exp(prediction[idx])), 3)
            ethnicity_distribution[ethnicity] = confidence

        predicted_ethnicites.append(ethnicity_distribution)

    return predicted_ethnicites


def predict(model_id: str, names: list[str], get_distribution: bool=False) -> list[str]:
    """
    Preprocesses and predicts the names.
    :param model_id: The ID of the model to use
    :param names: A list of all names which are to classify
    :param get_distribution: Wether to return the entire distribution of the predicted nationalities
    :return: List of the predicted nationalities (and optionally the entire output distr.)
    """

    load_dotenv()

    MAX_NAMES = int(os.getenv("MAX_NAMES"))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE"))

    model_config = load_json(f"model_configurations/{model_id}/config.json")
    classes = load_json(f"model_configurations/{model_id}/dataset/nationalities.json")
    model_file = f"model_configurations/{model_id}/model.pt"

    if len(names) > MAX_NAMES:
        raise InferenceError(
            error_code="TOO_MANY_NAMES",
            message=f"Too many names (maximum {MAX_NAMES}.",
            status_code=422    
        )

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
    return classify_names(input_batch, model_config, classes, get_distribution)

