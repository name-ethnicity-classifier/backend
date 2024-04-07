from inference.predict import replace_special_chars


def test_replace_special_chars():
    assert replace_special_chars("test") == "test"
    assert replace_special_chars("tést") == "test"
    assert replace_special_chars("2") == ""
    assert replace_special_chars("Tê123#öäüµ") == "teoau"


def test_preprocess_names():
    names = ["isáác newton", "albêrt einstein123", "Anders-Jonas Ångström"]
    batch_size = 2

