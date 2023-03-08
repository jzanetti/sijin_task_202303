from darts.models import TCNModel, RNNModel, LinearRegressionModel, RandomForest


def use_randomforest(lags: int = 10, n_estimators: int = 150):
    """Return a RNN model

    Returns:
        _type_: a RNN model
    """
    return RandomForest(lags=lags, n_estimators=n_estimators)

def use_linear(lags: int = 10):
    """Return a RNN model

    Returns:
        _type_: a RNN model
    """
    return LinearRegressionModel(lags=lags)


def use_tcn():
    """Return a RNN model

    Returns:
        _type_: a RNN model
    """
    return TCNModel(
        input_chunk_length=13,
        output_chunk_length=12,
        n_epochs=500,
        dropout=0.1,
        dilation_base=2,
        weight_norm=True,
        kernel_size=5,
        num_filters=3,
        random_state=0,
    )