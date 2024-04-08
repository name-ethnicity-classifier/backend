"""import os
from inference.inference import replace_special_chars, preprocess_names, predict


def test_replace_special_chars():
    assert replace_special_chars("test") == "test"
    assert replace_special_chars("tést") == "test"
    assert replace_special_chars("2") == ""
    assert replace_special_chars("Tê123#öäüµ") == "Teoau"


def test_predict():
    model_id = "test_model"
    names = ["Peter Schmidt", "Cixin Liu"]

    os.environ["BATCH_SIZE"] = "3"
    os.environ["MAX_NAMES"] = "1000"

    result_distributions = predict(model_id, names, get_distribution=True)

    assert ["else", "chinese"] == list(result_distributions[0].keys())
    assert sum(result_distributions[0].values()) == 100.0
    assert sum(result_distributions[1].values()) == 100.0

"""
