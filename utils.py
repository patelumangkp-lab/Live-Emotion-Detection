"""Utility functions for loading data, preprocessing, and plotting.

This file provides helpers used by training and live-detection scripts.
"""
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import seaborn as sns


def plot_history(history, out_path=None):
    """Plot training & validation accuracy and loss."""
    acc = history.history.get('accuracy') or history.history.get('acc')
    val_acc = history.history.get('val_accuracy') or history.history.get('val_acc')
    loss = history.history['loss']
    val_loss = history.history['val_loss']

    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(acc, label='train_acc')
    plt.plot(val_acc, label='val_acc')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.title('Training and Validation Accuracy')

    plt.subplot(1, 2, 2)
    plt.plot(loss, label='train_loss')
    plt.plot(val_loss, label='val_loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.title('Training and Validation Loss')

    plt.tight_layout()
    if out_path:
        plt.savefig(out_path)
    plt.show()


def plot_confusion_matrix(y_true, y_pred, labels, out_path=None):
    cm = confusion_matrix(y_true, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    fig, ax = plt.subplots(figsize=(8, 8))
    disp.plot(ax=ax, cmap='Blues', colorbar=False)
    plt.xticks(rotation=45)
    plt.title('Confusion Matrix')
    plt.tight_layout()
    if out_path:
        plt.savefig(out_path)
    plt.show()


def preprocess_image(image):
    """Ensure image is float32 normalized to [0,1] and resized to (48,48).

    Assumes image is a numpy array.
    """
    # image expected in shape (h, w) or (h, w, 1)
    if image.ndim == 3 and image.shape[2] == 3:
        # convert to grayscale average
        image = np.mean(image, axis=2)
    image = image.astype('float32') / 255.0
    image = np.expand_dims(image, -1)
    return image
