"""Train a CNN on the FER-2013 dataset and save the model to emotion_model.h5.

This script runs locally or on Colab. It downloads FER-2013 via tensorflow_datasets,
preprocesses images to grayscale 48x48, builds a CNN, trains with validation,
plots metrics and confusion matrix, and saves the model.
"""
import os
import numpy as np
import tensorflow as tf
import os
import tensorflow_datasets as tfds
from tensorflow.keras import layers, models
from tensorflow.keras.utils import to_categorical
from sklearn.metrics import classification_report
from utils import plot_history, plot_confusion_matrix
from tensorflow.keras.preprocessing import image



EMOTION_LABELS = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']


def load_fer2013(split='train'):
    """Load the FER-2013 dataset via tensorflow_datasets and return numpy arrays."""
    ds, info = tfds.load('fer2013', split=split, with_info=True, as_supervised=True)
    images = []
    labels = []
    for img, label in tfds.as_numpy(ds):
        # img is (48,48,1) uint8
        images.append(img)
        labels.append(label)
    images = np.array(images)
    labels = np.array(labels)
    return images, labels


def load_from_local_dirs(train_dir='train', val_dir='test', image_size=(48, 48), batch_size=64):
    """Load datasets from local folders using Keras utilities.

    Expects directory structure:
        train/<class_name>/*.jpg
        test/<class_name>/*.jpg
    Returns tf.data.Dataset objects (train_ds, val_ds) with images normalized and labels one-hot.
    """
    if not os.path.isdir(train_dir) or not os.path.isdir(val_dir):
        return None, None

    train_ds = tf.keras.utils.image_dataset_from_directory(
        train_dir,
        labels='inferred',
        label_mode='categorical',
        image_size=image_size,
        color_mode='grayscale',
        batch_size=batch_size,
        shuffle=True,
        seed=123,
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        val_dir,
        labels='inferred',
        label_mode='categorical',
        image_size=image_size,
        color_mode='grayscale',
        batch_size=batch_size,
        shuffle=False,
    )

    # normalize to [0,1]
    normalization = tf.keras.layers.Rescaling(1.0/255)
    train_ds = train_ds.map(lambda x, y: (normalization(x), y))
    val_ds = val_ds.map(lambda x, y: (normalization(x), y))

    return train_ds, val_ds


def preprocess(images):
    images = images.astype('float32') / 255.0
    # ensure shape (n,48,48,1)
    if images.ndim == 3:
        images = np.expand_dims(images, -1)
    return images


def build_model(input_shape=(48, 48, 1), num_classes=7):
    model = models.Sequential()
    model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape))
    model.add(layers.Conv2D(32, (3, 3), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Dropout(0.25))

    model.add(layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Dropout(0.25))

    model.add(layers.Flatten())
    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(num_classes, activation='softmax'))

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=30, help='Number of training epochs')
    parser.add_argument('--batch_size', type=int, default=64, help='Batch size')
    args = parser.parse_args()
    epochs = args.epochs
    batch_size = args.batch_size

    os.makedirs('models', exist_ok=True)

    # Prefer local directory datasets if present (train/ and test/)
    print('Checking for local `train/` and `test/` directories...')
    train_ds, val_ds = load_from_local_dirs(train_dir='train', val_dir='test', image_size=(48, 48), batch_size=batch_size)

    if train_ds is not None and val_ds is not None:
        print('Found local dataset folders, using them for training.')
        model = build_model(input_shape=(48, 48, 1), num_classes=7)
        model.summary()

        callbacks = [
            tf.keras.callbacks.ModelCheckpoint('emotion_model.h5', monitor='val_accuracy', save_best_only=True),
            tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-6),
        ]

        history = model.fit(train_ds, epochs=epochs, validation_data=val_ds, callbacks=callbacks)

        print('Plotting history...')
        plot_history(history, out_path='training_history.png')

        print('Loading best model and evaluating on validation set...')
        best = tf.keras.models.load_model('emotion_model.h5')
        val_loss, val_acc = best.evaluate(val_ds, verbose=1)
        print(f'Validation loss: {val_loss:.4f}, acc: {val_acc:.4f}')

        print('Predicting on validation set for confusion matrix...')
        # Collect y_true and y_pred across the validation dataset
        y_true = []
        for _, y_batch in val_ds:
            y_true.extend(np.argmax(y_batch.numpy(), axis=1).tolist())

        y_pred_probs = best.predict(val_ds)
        y_pred = np.argmax(y_pred_probs, axis=1)

        plot_confusion_matrix(y_true, y_pred, labels=EMOTION_LABELS, out_path='confusion_matrix.png')
        print('Classification report:')
        print(classification_report(y_true, y_pred, target_names=EMOTION_LABELS))
        print('Model saved to emotion_model.h5 (best by val_accuracy).')
        return

    # Fall back to tensorflow_datasets if local folders are not present
    print('Local folders not found; falling back to loading FER-2013 via tensorflow_datasets...')
    x_train, y_train = load_fer2013('train')
    x_val, y_val = load_fer2013('validation')

    x_train = preprocess(x_train)
    x_val = preprocess(x_val)

    y_train_cat = to_categorical(y_train, num_classes=7)
    y_val_cat = to_categorical(y_val, num_classes=7)

    print('Building model...')
    model = build_model(input_shape=x_train.shape[1:], num_classes=7)
    model.summary()

    callbacks = [
        tf.keras.callbacks.ModelCheckpoint('emotion_model.h5', monitor='val_accuracy', save_best_only=True),
        tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-6),
    ]

    print('Training...')
    history = model.fit(x_train, y_train_cat, epochs=epochs, batch_size=batch_size, validation_data=(x_val, y_val_cat), callbacks=callbacks)

    print('Plotting history...')
    plot_history(history, out_path='training_history.png')

    print('Loading best model and evaluating on validation set...')
    best = tf.keras.models.load_model('emotion_model.h5')
    val_loss, val_acc = best.evaluate(x_val, y_val_cat, verbose=1)
    print(f'Validation loss: {val_loss:.4f}, acc: {val_acc:.4f}')

    print('Predicting on validation set for confusion matrix...')
    y_pred = np.argmax(best.predict(x_val), axis=1)
    plot_confusion_matrix(y_val, y_pred, labels=EMOTION_LABELS, out_path='confusion_matrix.png')

    print('Classification report:')
    print(classification_report(y_val, y_pred, target_names=EMOTION_LABELS))

    print('Model saved to emotion_model.h5 (best by val_accuracy).')


if __name__ == '__main__':
    main()
