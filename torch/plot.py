# Plotting functions module

import matplotlib.pyplot as plt
import matplotlib.patches as pat
import matplotlib.colors as colors
import matplotlib

import pandas as pd
import numpy as np

import torch
import torch.nn as nn

import time
from pathlib import Path

from sklearn.preprocessing import MinMaxScaler

from data_helpers import mse

def triangulate(df: pd.DataFrame):   
    """
    Create triangulation of the mesh grid, which is passed to tricontourf.
    
    Uses Delaunay triangulation.

    Parameters
    ----------
    df : DataFrame
        DataFrame with X and Y values for the triangulation.

    Returns
    -------
    triangles : matplotlib.tri.triangulation.Triangulation
        Triangulated grid.

    """
    x = df['x'].to_numpy()*100
    y = df['y'].to_numpy()*100
    triangles = matplotlib.tri.Triangulation(x, y)
    
    return triangles


# from data.py
def get_cbar_range(param_col_label):
    if param_col_label=='potential (V)':
        cmin = 0.0
        cmax = 210
    elif param_col_label=='Ex (V/m)':
        cmin = -150000
        cmax =   75000
    elif param_col_label=='Ey (V/m)':
        cmin = -150000
        cmax =  150000
    elif param_col_label=='Ne (#/m^-3)':
        cmin = 0.0
        cmax = 1.6e16
    elif param_col_label=='Ar+ (#/m^-3)':
        cmin = 7.5e10
        cmax = 1.6e16
    elif param_col_label=='Nm (#/m^-3)':
        cmin = 3.3e11
        cmax = 8.9e18
    elif param_col_label=='Te (eV)':
        cmin =  0.0
        cmax = 12.0
    return cmin, cmax


def get_cbar_range_300V_60Pa(param_col_label, lin=False): ## TODO: fix this
    if lin:
        if param_col_label=='potential (V)':
            cmin =  0.0
            cmax = 9.8
        elif param_col_label=='Ex (V/m)':
            cmin = -80000
            cmax =  19000
        elif param_col_label=='Ey (V/m)':
            cmin = -68000
            cmax =  72000
        elif param_col_label=='Ne (#/m^-3)':
            cmin = 0.0
            cmax = 58
        elif param_col_label=='Ar+ (#/m^-3)':
            cmin = 4.5e-3
            cmax = 58
        elif param_col_label=='Nm (#/m^-3)':
            cmin = 3.2e-3
            cmax = 88
        elif param_col_label=='Te (eV)':
            cmin = 0.0
            cmax = 6.0
    else:
        if param_col_label=='potential (V)':
            cmin =  0.0
            cmax = 98.0
        elif param_col_label=='Ex (V/m)':
            cmin = -80000
            cmax =  19000
        elif param_col_label=='Ey (V/m)':
            cmin = -68000
            cmax =  72000
        elif param_col_label=='Ne (#/m^-3)':
            cmin = 0.0
            cmax = 5.8e15
        elif param_col_label=='Ar+ (#/m^-3)':
            cmin = 4.5e11
            cmax = 5.8e15
        elif param_col_label=='Nm (#/m^-3)':
            cmin = 3.2e13
            cmax = 8.8e17
        elif param_col_label=='Te (eV)':
            cmin = 0.0
            cmax = 6.0
    return cmin, cmax


def draw_a_2D_graph(avg_data, param_col_label, file_path=None, set_cbar_range=True, c_only=False, lin=False):
    # data
    
    units = {'potential (V)'    :' ($\mathrm{10 V}$)', 
             'Ne (#/m^-3)'      :' ($10^{14}$ $\mathrm{m^{-3}}$)',
             'Ar+ (#/m^-3)'     :' ($10^{14}$ $\mathrm{m^{-3}}$)', 
             'Nm (#/m^-3)'      :' ($10^{16}$ $\mathrm{m^{-3}}$)',
             'Te (eV)'          :' (eV)'}

    
    matplotlib.rcParams['font.family'] = 'Arial'
    x = avg_data.X.values.reshape(-1,1)*100
    y = avg_data.Y.values.reshape(-1,1)*100
    z = avg_data[param_col_label].values.reshape(-1,1)
    
    cmap=plt.cm.viridis
    
    # settings for drawing
    # plt.rcParams['font.family'] = 'serif'
    fig = plt.figure(figsize=(3.3,7), dpi=200)
    ax = fig.add_subplot(111)
    ax.set_aspect('equal')
    if set_cbar_range:
        #cmin, cmax = get_cbar_range(param_col_label)
        cmin, cmax = get_cbar_range_300V_60Pa(param_col_label, lin=lin)
        sc = ax.scatter(x, y, c=z, cmap=cmap, alpha=0.5, s=2, linewidths=0, vmin=cmin, vmax=cmax)
    else:
        sc = ax.scatter(x, y, c=z, cmap=cmap, alpha=0.5, s=2, linewidths=0)
    cbar = plt.colorbar(sc)
    cbar.minorticks_off()
    
    if lin:
        title = param_col_label.split(' ')[0] + units[param_col_label]
    else:
        title = param_col_label
    
    ax.set_title(title, fontsize=13)
    ax.set_xlabel('r [cm]')
    ax.set_ylabel('z [cm]')
    ax.set_xlim(0, 21)
    ax.set_ylim(0, 72)
    fig.tight_layout()
    
    if file_path==None:
        plt.show()
    else:
        fig.savefig(file_path)
    plt.close('all')


def save_history_graph(history: list, out_dir: Path):
    matplotlib.rcParams['font.family'] = 'Arial'
    x  = np.array(history)

    plt.rcParams['font.size'] = 12 # 12 is the default size
    plt.rcParams['xtick.minor.size'] = 2
    plt.rcParams['ytick.minor.size'] = 2
    fig, ax = plt.subplots(figsize=(6.0,6.0), dpi=200)
    
    # axis labels
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Loss')
    
    ax.plot(x, color='green', lw=1.0, label='train_error')
    
    # set both x_min and y_min as zero
    _, x_max = ax.get_xlim()
    _, y_max = ax.get_ylim()
    ax.set_xlim(0, x_max)
    ax.set_ylim(0, y_max)
    
    ax.xaxis.get_ticklocs(minor=True)
    ax.yaxis.get_ticklocs(minor=True)
    ax.minorticks_on()
    
    plt.legend()
    ax.grid()
    plt.tight_layout()
    
    # save the figure
    # if param=='mae':
    #     file_name = 'history_graph_mae.png'
    # elif param=='loss':
    file_name = 'history_graph_loss.png'
    file_path = out_dir / file_name
    fig.savefig(file_path)


def draw_apparatus(ax):
    def edge_unit_conv(edges):
        u = 1e-1 # unit conv. mm -> cm
        return [(xy[0]*u,xy[1]*u) for xy in edges]
    
    pt_colors = {'fc':'white', 'ec':'black'}
    
    edges = [(0,453), (0,489), (95,489), (95,487), (40,487), (40,453)]
    patch_top = pat.Polygon(xy=edge_unit_conv(edges), fc=pt_colors['fc'], ec=pt_colors['ec'])
    ax.add_patch(patch_top)
    
    edges = [(0,0), (0,415), (95,415), (95,395), (90,395), (90,310), (120,310), (120,277), (90,277), (90,0)]
    patch_bottom = pat.Polygon(xy=edge_unit_conv(edges), fc=pt_colors['fc'], ec=pt_colors['ec'])
    ax.add_patch(patch_bottom)
    
    edges = [(122,224), (122,234), (185,234), (185,224)]
    patch_float = pat.Polygon(xy=edge_unit_conv(edges), fc=pt_colors['fc'], ec=pt_colors['ec'])
    ax.add_patch(patch_float)


def quickplot(df:pd.DataFrame, data_dir=None, grid=False, triangles=None):
    """Quick plot of all 5 parameters.

    This makes a plot for just the predictions, but it might help to have
    the actual simulation results for comparison (TODO).
    Args:
        df (pd.DataFrame): DataFrame of only the predictions (no features).
        data_dir (Path, optional): Path to where the model is saved. Defaults to None.
        grid (bool, optional): _description_. Defaults to False.
        triangles (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    matplotlib.rcParams['font.family'] = 'Arial'
    cmap = plt.cm.viridis

    fig, ax = plt.subplots(1, len(df.columns), figsize=(10, 4), dpi=200)

    titles = [column.split()[0] for column in df.columns]

    for i, column in enumerate(df.columns):
        ax[i].set_aspect('equal')
        cmin, cmax = get_cbar_range_300V_60Pa(column, lin=True)
        tri = ax[i].tricontourf(triangles, df[column], levels=36, 
                                 cmap=cmap, vmin=cmin, vmax=cmax)
        plt.colorbar(tri)
        draw_apparatus(ax[i])
        ax[i].set_title(titles[i])
    
    fig.subplots_adjust(left=0.05, right=0.95, wspace=0.8)       

    plt.show()
    if data_dir is not None:
        fig.savefig(data_dir/'quickplot.png', bbox_inches='tight')

    return fig


def correlation(prediction: pd.DataFrame, targets: pd.DataFrame, scores: pd.DataFrame, out_dir=None):
    """Plot correlation between true values and predictions.

    Args:
        prediction (pd.DataFrame): DataFrame of predicted values.
        targets (pd.DataFrame): DataFrame of true values.
        scores (pd.DataFrame): Scores containing the r2.
        out_dir (Path, optional): Path to save file. Defaults to None.
    """
    assert list(prediction.columns) == list(targets.columns)

    prediction = prediction.copy()
    targets = targets.copy()

    colors = ['#d20f39', '#df8e1d', '#40a02b', '#04a5e5', '#8839ef']

    fig, ax = plt.subplots(dpi=200)
    
    # customize axes
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_aspect('equal')
    ax.set_ylabel('Predicted')
    ax.set_xlabel('True')

    # plot 1:1 line
    x = np.linspace(0, 1, 1000)
    ax.plot(x, x, ls='--', c='k')

    for i, column in enumerate(prediction.columns):
        # transform with minmax to normalize between (0, 1)
        scaler = MinMaxScaler()
        scaler.fit(targets[column].values.reshape(-1, 1))
        scaled_targets = scaler.transform(targets[column].values.reshape(-1, 1))
        scaled_predictions = scaler.transform(prediction[column].values.reshape(-1, 1))

        # get correlation score
        r2 = round(scores[column].iloc[3], 2)

        # set label
        label = f'{column.split()[0]}: {r2}'

        ax.scatter(scaled_targets, scaled_predictions, s=1, marker='.',
                   color=colors[i], alpha=0.15, label=label)

    legend = ax.legend(markerscale=4, fontsize='small')
    for lh in legend.legendHandles: 
        lh.set_alpha(1)
    
    if out_dir is not None:
        fig.savefig(out_dir/'correlation.png', bbox_inches='tight')


def difference_plot(tX: pd.DataFrame, py: pd.DataFrame, ty: pd.DataFrame, out_dir: Path):
    """Plot the difference between predictions and true values. (py - ty)

    Args:
        tX (pd.DataFrame): DataFrame of (V, P, X, Y)
        py (pd.DataFrame): DataFrame of predictions.
        ty (pd.DataFrame): DataFrame of corresponding true values.
        out_dir (Path): Directory to save the figure.
    """
    assert list(py.columns) == list(ty.columns)

    # TODO: move elsewhere
    units = {'potential (V)'    :' ($\mathrm{10 V}$)', 
            'Ne (#/m^-3)'      :' ($10^{14}$ $\mathrm{m^{-3}}$)',
            'Ar+ (#/m^-3)'     :' ($10^{14}$ $\mathrm{m^{-3}}$)', 
            'Nm (#/m^-3)'      :' ($10^{16}$ $\mathrm{m^{-3}}$)',
            'Te (eV)'          :' (eV)'}

    diff = py - ty
    titles = [column.split()[0] for column in diff.columns]

    tX['x'] = tX['x']*100
    tX['y'] = tX['y']*100

    ranges = {'potential (V)': (-5, 5), 
              'Ne (#/m^-3)' : (-8, 8),
              'Ar+ (#/m^-3)' : (-9, 9),
              'Nm (#/m^-3)' : (-20, 20),
              'Te (eV)' : (-3, 3)}
    
    cmap = plt.get_cmap('coolwarm')

    fig, ax = plt.subplots(ncols=5, dpi=200, figsize=(12, 4))
    fig.subplots_adjust(wspace=0.2)
    
    for i, column in enumerate(ty.columns):
        sc = ax[i].scatter(tX['x'], tX['y'], c=diff[column], cmap='coolwarm', 
                           norm=colors.Normalize(vmin=ranges[column][0], vmax=ranges[column][1]), s=1)
        plt.colorbar(sc, extend='both')
        ax[i].set_title(titles[i] + ' ' + units[column])
        ax[i].set_aspect('equal')
        ax[i].set_xlim(0,20)
        ax[i].set_ylim(0,70.9)

    fig.savefig(out_dir/'difference.png', bbox_inches='tight')

    return fig


def plot_comparison_ae(reference: np.ndarray, prediction: torch.tensor, model:nn.Module, 
                       out_dir=None, is_square=False) -> float:  # TODO: move to plot module
    """Create plot comparing the reference data with its autoencoder reconstruction.

    Args:
        reference (np.ndarray): Reference dataset.
        prediction (torch.tensor): Tensor reshaped to match the encoding shape
        model (nn.Module): Model used to make predictions.
        out_dir (Path, optional): Output directory. Defaults to None.

    Returns:
        float: Evaluation time.
    """
    if is_square:
        figsize = (10, 5)
        extent = [0, 20, 35, 55]
    else:
        figsize = (10, 7)
        extent =[0, 20, 0, 70.7]

    fig = plt.figure(figsize=figsize, dpi=200, layout='constrained')
    subfigs = fig.subfigures(nrows=2, wspace=0.4)

    # if prediction.size() != model.encoded_size:
    #     raise ValueError(f'Tensor does not have the correct size {model.encoded_size}')

    axs1 = subfigs[0].subplots(nrows=1, ncols=5)
    axs2 = subfigs[1].subplots(nrows=1, ncols=5)

    subfigs[1].suptitle('Prediction from MLP to AE')
    subfigs[0].suptitle('Original (300V, 60Pa)')

    cbar_ranges = [(reference[0, i, :, :].min(),
                    reference[0, i, :, :].max()) for i in range(5)]

    start = time.time()
    reconstruction = model.decoder(prediction).cpu().numpy()
    end = time.time()

    scores = []

    for i in range(5):
        org = axs1[i].imshow(reference[0, i, :, :], origin='lower', aspect='equal',
                             extent=extent, cmap='magma')
        draw_apparatus(axs1[i])
        plt.colorbar(org)
        rec = axs2[i].imshow(reconstruction[0, i, :, :], origin='lower', extent=extent, aspect='equal',
                             vmin=cbar_ranges[i][0], vmax=cbar_ranges[i][1], cmap='magma')
        draw_apparatus(axs2[i])

        score = mse(reference[0, i, :, :], reconstruction[0, i, :, :])
        scores.append(score)

        plt.colorbar(rec)

    if out_dir is not None:
        fig.savefig(out_dir/f'test_comparison.png')

    return end-start, scores