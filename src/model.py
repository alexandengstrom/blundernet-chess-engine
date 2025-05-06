import tensorflow as tf
from tensorflow.keras import layers, models
import json
import os
import utils
from chess import pgn
from datetime import datetime
from live_plot import LivePlot
from infinite_dataset import InfiniteDataset

tf.config.set_visible_devices([], 'GPU')


class Model:
    def __init__(self, move_dict, model):
        self.move_dict = move_dict
        self.model = model

    @staticmethod
    def _build_model(output_size):
        inputs = layers.Input(shape=(8, 8, 17))

        x = layers.Conv2D(128, kernel_size=3, padding='same', activation='relu')(inputs)
        x = layers.BatchNormalization()(x)

        for _ in range(10):
            shortcut = x
            x = layers.Conv2D(128, kernel_size=3, padding='same', activation='relu')(x)
            x = layers.BatchNormalization()(x)
            x = layers.Conv2D(128, kernel_size=3, padding='same')(x)
            x = layers.BatchNormalization()(x)
            x = layers.Add()([x, shortcut])
            x = layers.ReLU()(x)

        se = layers.GlobalAveragePooling2D()(x)
        se = layers.Dense(8, activation='relu')(se)
        se = layers.Dense(128, activation='sigmoid')(se)
        se = layers.Reshape((1, 1, 128))(se)
        x = layers.Multiply()([x, se])

        p = layers.Conv2D(2, kernel_size=1, activation='relu')(x)
        p = layers.BatchNormalization()(p)
        p = layers.Flatten()(p)
        p = layers.Dense(1024, activation="gelu")(p)
        p = layers.Dense(output_size)(p)

        model = models.Model(inputs=inputs, outputs=p)

        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.0003),
            loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            metrics=['accuracy']
        )

        return model
    
    def evaluate(self, data, labels, batch_size=64):
        results = self.model.evaluate(data, labels, batch_size=batch_size, verbose=1)
        loss, accuracy = results[0], results[1]
        print(f"Evaluation - Loss: {loss:.4f}, Accuracy: {accuracy:.4f}")
        return loss, accuracy


    @staticmethod
    def train(dataset, model_name=None):
        move_dict = utils.generate_full_uci_move_dict()
        
        if model_name and os.path.exists(f"models/{model_name}.keras"):
            model = models.load_model(f"models/{model_name}.keras")
        elif not model_name:
            model_name = datetime.now().strftime("model_%Y%m%d_%H%M%S")
            print(f"No model name given, creating new model with name {model_name}")
            model = Model._build_model(len(move_dict))
        else:
            print(f"No model found named {model_name}, creating a new model...")
            model = Model._build_model(len(move_dict))
        
        instance = Model(move_dict, model)
        positions_processed = 0
        game_chunk = 1
        live_plot = LivePlot()
        
        try:
            for board_positions, gold_standard in dataset:

                if len(board_positions) == len(gold_standard):
                    history = model.fit(board_positions, gold_standard, epochs=1, batch_size=64)
                    if "accuracy" in history.history and "loss" in history.history:
                        acc = history.history["accuracy"][-1]
                        loss = history.history["loss"][-1]
                        live_plot.update(acc, loss)

                    positions_processed += len(board_positions)
                    instance.save(f"models/{model_name}.keras")
                    
                    print(f"\033[92m\nGame chunk {game_chunk} completed! Total position processed is {positions_processed}\033[0m")
                    print("\033[33mPress CTRL+C to stop the training process, the model will be saved\n\033[0m")
                    game_chunk += 1
                    
            return instance
        except KeyboardInterrupt:
            print("\033[92mModel saved!\033[0m")

    @staticmethod
    def load(path):
        model = models.load_model(path)
        move_dict = utils.generate_full_uci_move_dict()
        return Model(move_dict, model)

    def fit(self, data, targets, epochs=10, batch_size=64):
        self.model.fit(data, targets, epochs=epochs, batch_size=batch_size)

    def save(self, path):
        self.model.save(path)
            
