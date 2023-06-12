"""
Conditional autoencoder to reproduce 2d plasma profiles from a pair of V, P

* Train autoencoder
* Take encoder and encode labeled profiles (square images)
* 
"""

import os
import time
from pathlib import Path

import matplotlib.pyplot as plt

import cv2
import numpy as np
import pandas as pd
import xarray as xr
from tqdm import tqdm

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
from torchvision.transforms.functional import crop
from torch.utils.data import TensorDataset, DataLoader
from torchinfo import summary

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

from data_helpers import ImageDataset
from plot import plot_comparison_ae, save_history_graph

class SquareAE(nn.Module):
    """Autoencoder using square images as inputs.
    
    Input sizes are (5, 64, 64).
    """
    def __init__(self) -> None:
        super(SquareAE, self).__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(5, 10, kernel_size=3, stride=2, padding=1),
            nn.ReLU(),

            nn.Conv2d(10, 20, kernel_size=3, stride=2, padding=1),
            nn.ReLU(),

            nn.Conv2d(20, 20, kernel_size=3, stride=2, padding=1),
            nn.ReLU(),
        )

        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(20, 20, kernel_size=2, stride=2),
            nn.ReLU(),

            nn.ConvTranspose2d(20, 10, kernel_size=2, stride=2),
            nn.ReLU(),

            nn.ConvTranspose2d(10, 5, kernel_size=2, stride=2),
            nn.ReLU()
        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        # decoded = torchvision.transforms.functional.crop(
        #     decoded, 0, 0, 64, 64)
        return decoded
    

class MLP(nn.Module):
    """MLP to recreate encodings from a pair of V and P.
    """
    def __init__(self, input_size, output_size, dropout_prob) -> None:
        super(MLP, self).__init__()
        self.input_size = input_size
        self.output_size = output_size
        self.fc1 = nn.Linear(input_size, 256)
        self.fc2 = nn.Linear(256, 512)
        self.fc3 = nn.Linear(512, 1024)
        self.fc4 = nn.Linear(1024, output_size)
        self.dropout = nn.Dropout(dropout_prob)

    def forward(self, x):
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout(x)

        x = self.fc2(x)
        x = F.relu(x)
        x = self.dropout(x)

        x = self.fc3(x)
        x = F.relu(x)
        x = self.dropout(x)

        x = self.fc4(x)

        output = F.relu(x)
        return output


def resize(data: np.ndarray, scale=64) -> np.ndarray:
    """Resize square images to 64x64 resolution by downscaling.

    Args:
        data (np.ndarray): Input data.

    Returns:
        np.ndarray: Downscaled input data.
    """

    data = np.stack([cv2.resize((np.moveaxis(image, 0, -1)), (scale, scale)) for image in data])
    data = np.moveaxis(data, -1, 1)
    return data

def write_metadata_ae(out_dir):  # TODO: move to data module
    # if is_square:
    #     in_size = (1, 5, 200, 200)
    # else:
    #     in_size = (1, 5, 707, 200)

    in_size = batch_data[0].size()  # testing

    # save model structure
    file = out_dir/'train_log.txt'
    with open(file, 'w') as f:
        f.write(f'Model {name}\n')
        print(summary(model, input_size=in_size), file=f)
        print("\n", file=f)
        print(model, file=f)
        print(summary(mlp, input_size=(1, 2)), file=f)
        print("\n")
        f.write(f'\nEpochs: {epochs}\n')
        f.write(f'Learning rate: {learning_rate}\n')
        f.write(f'Resolution: {resolution}\n')
        f.write(f'Train time: {(train_end-train_start):.2f} s\n')
        # f.write(
        #     f'Average time per epoch: {np.array(epoch_times).mean():.2f} s\n')
        f.write(f'Evaluation time: {(eval_time):.2f} s\n')
        f.write(f'Scores (MSE): {scores}\n')
        f.write('\n***** end of file *****')


def mse(image1, image2):
    squared_diff = np.square(image1 - image2)
    mse = np.mean(squared_diff)
    return mse


if __name__ == '__main__':
    # set metal backend (apple socs)
    device = torch.device(
        'mps' if torch.backends.mps.is_available() else 'cpu')
    
    name = input("Model name: ") or "CAE_test"
    root = Path.cwd()
    
    # get data and important metadata
    image_ds = ImageDataset(root/'data'/'interpolation_datasets', True)
    train_features, train_labels = image_ds.train
    test_features, test_labels = image_ds.test
    v_used = np.array(list(image_ds.v_used))
    p_used = np.array(list(image_ds.p_used))

    # downscale train images
    resolution = 32
    train_res = resize(train_features, resolution)
    test_res = resize(test_features, resolution)

    # scale the inputs to the MLP
    scaler = MinMaxScaler()
    scaled_labels = scaler.fit_transform(train_labels)
    scaled_labels_test = scaler.transform(test_labels.reshape(1, -1))  # ValueError: reshape(1, -1) if it contains a single sample

    # split validation set
    # train_res, val = train_test_split(train_res, test_size=1, train_size=30)
    # val = torch.tensor(val, device=device)

    model_dir = Path(root/'created_models'/'autoencoder'/'A212'/'A212')

    out_dir = root/'created_models'/'conditional_autoencoder'/name
    if not out_dir.exists():
        out_dir.mkdir(parents=True)

    dataset = TensorDataset(torch.tensor(train_res, device=device), 
                            torch.tensor(train_labels, device=device))
    trainloader = DataLoader(dataset, batch_size=1, shuffle=True)

    # load autoencoder model
    model = SquareAE()
    model.to(device)
    model.load_state_dict(torch.load(model_dir))
    model.encoder.eval()  # inference mode
    
    #### train MLP ####
    # epoch_validation = []
    # epoch_times = []

    epochs = 100
    learning_rate = 1e-3
    dropout_prob = 0.5
    loop = tqdm(range(epochs))

    mlp = MLP(2, 20*4*4, dropout_prob=dropout_prob)
    mlp.to(device)
    optimizer = optim.Adam(mlp.parameters(), lr=learning_rate)
    criterion = nn.MSELoss()
    epoch_loss = []

    dataset = TensorDataset(torch.tensor(train_res, device=device), 
                            torch.tensor(train_labels, device=device))
    trainloader = DataLoader(dataset, batch_size=1, shuffle=True)

    # begin training MLP
    print("Training MLP...\r", end="")
    train_start = time.time()
    for epoch in range(epochs):
        loop = tqdm(trainloader)
        running_loss = 0.0  # record losses

        for i, batch_data in enumerate(loop):
            image, labels = batch_data  # feed in images and labels (V, P)
            target = model.encoder(image).view(1, -1)  # encoding shape: (1, 20, 4, 4)

            optimizer.zero_grad()  # reset gradients

            output = mlp(labels)  # forward pass
            loss = criterion(output, target)
            loss.backward()  # backward propagation
            optimizer.step()  # apply changes to network

            # print statistics
            loop.set_description(f"Epoch {epoch+1}/{epochs}")
            running_loss += loss.item()

        epoch_loss.append(loss.item())
        if (epoch+1) % epochs == 0:
            # save model every 10 epochs (so i dont lose all training progress in case i do something unwise)
            torch.save(model.state_dict(), out_dir/f'{name}')
            save_history_graph(epoch_loss, out_dir)

    print("\33[2KMLP training complete!")
    train_end = time.time()
    torch.save(model.state_dict(), out_dir/f'{name}')
    save_history_graph(epoch_loss, out_dir)

    mlp.eval()
    scores = []

    # construct a fake encoding from a pair of (V, P) and reshape to the desired dimensions
    with torch.no_grad():
        fake_encoding = mlp(torch.tensor(test_labels, device=device, dtype=torch.float32))  # mps does not support float64
        # reshape encoding from (1, 320) to (1, 20, 4, 4)
        fake_encoding = fake_encoding.reshape(1, 20, 4, 4)

    eval_time = plot_comparison_ae(test_res, model, out_dir=out_dir, is_square=True)
    write_metadata_ae(out_dir)