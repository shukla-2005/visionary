"""
LSTM model — gracefully handles environments where TensorFlow is not installed
(e.g. Render free tier). Falls back to a stub that raises a clear error.
"""

import numpy as np
import os

# Try to import TensorFlow; if unavailable, provide stubs
try:
    from tensorflow.keras.models import Sequential, load_model as _keras_load
    from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    Sequential = None


def _require_tf():
    if not TENSORFLOW_AVAILABLE:
        raise RuntimeError(
            "TensorFlow is not installed in this environment. "
            "LSTM predictions are unavailable. Use 'linear', 'rf', or 'xgb' models instead."
        )


def create_lstm_model(input_shape: tuple, units: int = 50, dropout_rate: float = 0.2):
    _require_tf()
    model = Sequential()
    model.add(LSTM(units=units, return_sequences=True, input_shape=input_shape))
    model.add(Dropout(dropout_rate))
    model.add(LSTM(units=units, return_sequences=False))
    model.add(Dropout(dropout_rate))
    model.add(Dense(units=25))
    model.add(Dense(units=1))
    model.compile(optimizer=Adam(learning_rate=0.001), loss="mean_squared_error")
    return model


def create_bidirectional_lstm_model(input_shape: tuple, units: int = 50, dropout_rate: float = 0.2):
    _require_tf()
    model = Sequential()
    model.add(Bidirectional(LSTM(units=units, return_sequences=True), input_shape=input_shape))
    model.add(Dropout(dropout_rate))
    model.add(Bidirectional(LSTM(units=units, return_sequences=False)))
    model.add(Dropout(dropout_rate))
    model.add(Dense(units=25))
    model.add(Dense(units=1))
    model.compile(optimizer=Adam(learning_rate=0.001), loss="mean_squared_error")
    return model


def train_lstm_model(model, X_train, y_train, X_val=None, y_val=None,
                     epochs=100, batch_size=32, save_path=None):
    _require_tf()
    callbacks = [EarlyStopping(
        monitor="val_loss" if X_val is not None else "loss",
        patience=10,
        restore_best_weights=True,
    )]
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        callbacks.append(ModelCheckpoint(
            save_path,
            monitor="val_loss" if X_val is not None else "loss",
            save_best_only=True,
        ))
    if X_val is not None and y_val is not None:
        model.fit(X_train, y_train, validation_data=(X_val, y_val),
                  epochs=epochs, batch_size=batch_size, callbacks=callbacks, verbose=1)
    else:
        model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size,
                  callbacks=callbacks, verbose=1)
    return model


def predict_with_lstm(model, X: np.ndarray) -> np.ndarray:
    _require_tf()
    return model.predict(X).flatten()


def save_lstm_model(model, filepath: str):
    _require_tf()
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    model.save(filepath)
    print(f"LSTM model saved to {filepath}")


def load_lstm_model(filepath: str):
    _require_tf()
    return _keras_load(filepath)
