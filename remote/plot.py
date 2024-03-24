# Plotting functions module

import matplotlib.pyplot as plt
import matplotlib.patches as pat
import matplotlib.colors as colors
import matplotlib.ticker as ticker
from mpl_toolkits.axes_grid1 import ImageGrid
from matplotlib import gridspec
import matplotlib
matplotlib.use('Agg')

import pandas as pd
import numpy as np
import xarray as xr

import torch
import torch.nn as nn
import torchvision

import time
import pickle
from pathlib import Path

from sklearn.preprocessing import MinMaxScaler

from data_helpers import mse, get_data

# global stuff 
units = {'potential (V)'    :' ($\mathrm{10 V}$)', 
            'Ne (#/m^-3)'      :' ($10^{14}$ $\mathrm{m^{-3}}$)',
            'Ar+ (#/m^-3)'     :' ($10^{14}$ $\mathrm{m^{-3}}$)', 
            'Nm (#/m^-3)'      :' ($10^{16}$ $\mathrm{m^{-3}}$)',
            'Te (eV)'          :' (eV)'}  # list of keys can be extracted using units.keys()
columns_math = ['$\phi$', '$n_e$', '$n_i$', '$n_m$', '$T_e$']
cat_rainbow = ['#d20f39', '#df8e1d', '#40a02b', '#04a5e5', '#8839ef']
root = Path.cwd()


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


def quickplot(df:pd.DataFrame, data_dir=None, triangles=None, nodes=None, mesh=False):
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
    cmap = plt.cm.viridis

    # check whether to plot a filled contour or mesh points
    
    fig = plt.figure(dpi=200, figsize=(9, 4), constrained_layout=True)
    grid = ImageGrid(
        fig, 111, nrows_ncols=(1, len(df.columns)), 
        axes_pad=0.5, label_mode="L", share_all=True,
        cbar_location="right", cbar_mode="each", cbar_size="7%", cbar_pad="5%")

    titles = [column.split()[0] for column in df.columns]

    if mesh:
        for i, column in enumerate(df.columns):
            ax = grid[i]
            cax = grid.cbar_axes[i]
            ax.set_aspect('equal')
            cmin, cmax = get_cbar_range_300V_60Pa(column, lin=True)
            sc = ax.scatter(nodes['x'], nodes['y'], c=df[column], 
                                    cmap=cmap,
                                    norm=colors.Normalize(vmin=cmin, vmax=cmax),
                                    s=0.2)
            cax.colorbar(sc)
            draw_apparatus(ax)
            ax.set_xlim(0,20)
            ax.set_ylim(0,70.9)
            ax.set_title(titles[i])

    else:
        for i, column in enumerate(df.columns):
            ax = grid[i]
            cax = grid.cbar_axes[i]
            ax.set_aspect('equal')
            cmin, cmax = get_cbar_range_300V_60Pa(column, lin=True)
            tri = ax.tricontourf(triangles, df[column], levels=36, 
                                    cmap=cmap, vmin=cmin, vmax=cmax)
            cax.colorbar(tri)
            draw_apparatus(ax)
            ax.set_title(titles[i])
        

    if data_dir is not None:
        if mesh:
            fig.savefig(data_dir/'quickplot_mesh.png', bbox_inches='tight')
        else:
            fig.savefig(data_dir/'quickplot.png', bbox_inches='tight')

    return fig


def correlation(prediction: pd.DataFrame, targets: pd.DataFrame, scores=None, scores_list=None, out_dir=None):
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
        if scores is None:
            r2 = round(scores_list[i], 2)
        else: 
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

    diff = 100 * ((py - ty) / np.abs(ty)) 
    titles = [column.split()[0] for column in diff.columns]

    tX['x'] = tX['x']*100
    tX['y'] = tX['y']*100
    
    cmap = plt.get_cmap('coolwarm')

    # fig, ax = plt.subplots(ncols=5, dpi=200, figsize=(12, 4), constrained_layout=True)
    fig = plt.figure(dpi=200, figsize=(8, 4), constrained_layout=True)
    gs = gridspec.GridSpec(1, 6, width_ratios=[1, 1, 1, 1, 1, 0.1], figure=fig)
    
    for i, column in enumerate(ty.columns):
        ax = fig.add_subplot(gs[0, i])
        sc = ax.scatter(tX['x'], tX['y'], c=diff[column], cmap=cmap, 
                        #    norm=colors.Normalize(vmin=ranges[column][0], vmax=ranges[column][1]), 
                           norm=colors.Normalize(vmin=-100, vmax=100),
                           s=0.2) 
        draw_apparatus(ax)
        ax.set_title(titles[i])
        ax.set_aspect('equal')
        ax.set_xlim(0,20)
        ax.set_ylim(0,70.9)
        draw_apparatus(ax)
    
    cax = fig.add_subplot(gs[0, 5])
    cbar = plt.colorbar(sc, extend='both', cax=cax)
    cbar.ax.tick_params(labelsize=8)
    cbar.set_label(r'% difference', size=8)

    fig.savefig(out_dir/'difference.png', bbox_inches='tight')

    return fig


def plot_comparison_ae(reference: np.ndarray, prediction: torch.tensor, 
                       model:nn.Module, out_dir=None, is_square=False, cbar='magma'): 
    """Create plot comparing the reference data with its autoencoder reconstruction.

    Args:
        reference (np.ndarray): Reference dataset.
        prediction (torch.tensor): Tensor reshaped to match the encoding shape.
        model (nn.Module): Autoencoder model whose decoder used to make predictions.
        out_dir (Path, optional): Output directory. Defaults to None.
        is_square (bool, optional): Switch for square image and full rectangle.
            Defaults to False.

    Returns:
        float: Evaluation time (ns).
        scores: List of reconstruction MSE
    """

    resolution = reference.shape[2]
    # if prediction.shape[2] or prediction.shape[3] != resolution:
    #     raise ValueError(f'Prediction is not cropped properly! size={resolution}')

    if is_square:
        figsize = (6, 3)
        extent = [0, 20, 35, 55]
    else:
        figsize = (10, 5)
        extent =[0, 20, 0, 70.7]

    fig = plt.figure(dpi=300, layout='constrained')
    
    grid = ImageGrid(fig, 111,  # similar to fig.add_subplot(142).
                     nrows_ncols=(2, 5), axes_pad=0.0, label_mode="L", share_all=True,
                     cbar_location="right", cbar_mode="single", cbar_size="5%", cbar_pad='5%')

    with torch.no_grad():
        start = time.perf_counter_ns()
        decoded = model.decoder(prediction).cpu().numpy()
        reconstruction = decoded[:, :, :resolution, :resolution]  # assumes shape: (samples, channels, height, width)
        end = time.perf_counter_ns()

    eval_time = (end-start)

    # get the larger value between maxima of each dataset
    cbar_reference = 'original' if reference[0].max() > reconstruction[0].max() else 'prediction'
    cbar_ranges = (0, max(reference[0].max(), reconstruction[0].max()))
    vmin, vmax = cbar_ranges

    # plot the figures
    for i, ax in enumerate(grid):
        if i <= 4:
            org = ax.imshow(reference[0, i, :, :], origin='lower', extent=extent, aspect='equal',
                            vmin=vmin, vmax=vmax, cmap=cbar)
            draw_apparatus(ax)
            ax.set_ylabel('z [cm]', fontsize=8)
        else:
            rec = ax.imshow(reconstruction[0, i-5, :, :], origin='lower', extent=extent, aspect='equal',
                            vmin=vmin, vmax=vmax, cmap=cbar)
            draw_apparatus(ax)
            ax.set_ylabel('z [cm]', fontsize=8)
            ax.set_xlabel('r [cm]', fontsize=8)
    
    if cbar_reference == 'original':
        cb = grid.cbar_axes[0].colorbar(org) 
    else:
        cb = grid.cbar_axes[0].colorbar(rec)
        
    cb.set_label('Minmax scaled magnitude', rotation=270, fontsize=8, va='bottom', ha='center')

    global columns_math

    # set font sizes and tick stuff
    for i, ax in enumerate(grid):
        if i <= 4:
            ax.set_title(columns_math[i%5])
        ax.xaxis.set_major_locator(ticker.MaxNLocator(3, steps=[10], prune='upper'))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(2))

        ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(2))
        ax.tick_params(axis='both', labelsize=8)

    # record scores
    scores = []
    for i in range(5):
        score = mse(reference[0, i, :, :], reconstruction[0, i, :, :])
        scores.append(score)

    name = 'test_comparison'
    if cbar != 'magma':
        name = 'test_comparison_' + cbar

    if out_dir is not None:
        fig.savefig(out_dir/f'{name}.png', bbox_inches='tight')

    return eval_time, scores


def ae_correlation(reference, prediction, out_dir=None, minmax=True):
    from sklearn.metrics import r2_score
    scores = []
    global columns_math
    prediction_cols = []
    reference_cols = []

    try:
        prediction = prediction.cpu().numpy()
    except:
        prediction = prediction
    
    for i, column in enumerate(columns_math):
        ref_series = pd.Series(reference[0, i, :, :].flatten(), name=column)
        pred_series = pd.Series(prediction[0, i, :, :].flatten(), name=column)
        scores.append(r2_score(reference[0, i, :, :].flatten(), 
                               prediction[0, i, :, :].flatten()))
        reference_cols.append(ref_series)
        prediction_cols.append(pred_series)
    
    ref_df = pd.DataFrame({k: v for k, v in zip(columns_math, reference_cols)})
    pred_df = pd.DataFrame({k: v for k, v in zip(columns_math, prediction_cols)})
    
    if out_dir is not None:
        correlation(pred_df, ref_df, scores_list=scores, out_dir=out_dir)

    return scores


def mesh_slices(model, scaler_dir: Path, kind='mesh', out_dir=None):
    """Plot 1D profile at specific vertical and horizontal slices (x=115 mm, y=440 mm).

    Args:
        model (nn.Module): Model with weights loaded.
        scaler_dir (Path): Path to scalers (model_dir/scalers)
        kind (str, optional): Get slices of mesh models or images. Defaults to 'mesh'.
        out_dir (Path, optional): Path to save the figure. Defaults to None.

    Raises:
        ValueError: If kind is not 'mesh' (I have to write the code for image slices)

    Returns:
        None: none
    """
    columns = ['potential (V)', 'Ne (#/m^-3)', 'Ar+ (#/m^-3)', 'Nm (#/m^-3)', 'Te (eV)']
    colors = ['#d20f39', '#df8e1d', '#40a02b', '#04a5e5', '#8839ef']

    sliceres = 1000
    
    # load reference data
    ds = xr.open_dataset(root/'data'/'interpolation_datasets'/'test_set.nc')

    xscalers_dir = sorted(scaler_dir.rglob('xscaler*.pkl'))  # order goes V, P, x, y
    yscalers_dir = sorted(scaler_dir.rglob('yscaler*.pkl'))
    scalers = []
    yscalers = []

    for i in range(len(xscalers_dir)):
        with open(xscalers_dir[i], 'rb') as f:
            # I would rename these to xscalers but there would be too many things to change
            scaler = pickle.load(f)
            scalers.append(scaler)
    
    for i in range(len(yscalers_dir)):
        with open(yscalers_dir[i], 'rb') as f:
            scaler = pickle.load(f)
            yscalers.append(scaler)

    # test v and p (scaled) (arent these validation?)
    v = 300.0
    p = 60.0
    testV = scalers[0].transform(np.array([v]).reshape(-1, 1))
    testP = scalers[1].transform(np.array([p]).reshape(-1, 1))
    
    # horizontal line
    xhs = scalers[2].transform(np.linspace(0, 0.2, sliceres).reshape(-1, 1))
    yh = scalers[3].transform(np.array([0.44]).reshape(-1, 1))  # m
    horizontal = np.array([np.array([testV.item(), testP.item(), xh.item(), yh.item()]) for xh in xhs])
    xhs = np.linspace(0, 0.2, sliceres)
    yh = yh.item()

    # vertical line 
    xv = scalers[2].transform(np.array([0.115]).reshape(-1, 1))  # m
    yvs = scalers[3].transform(np.linspace(0, 0.707, sliceres).reshape(-1, 1))
    vertical = np.array([np.array([testV.item(), testP.item(), xv.item(), yv.item()]) for yv in yvs])
    yvs = np.linspace(0, 0.707, sliceres)
    xv = xv.item()

    # create tensor of x, y points for both horizontal and vertical slices
    horizontal = torch.FloatTensor(horizontal)
    vertical = torch.FloatTensor(vertical)

    # predict x, y points from model and plot
    model.eval()
    with torch.no_grad():
        horizontal_prediction = pd.DataFrame(model(horizontal).numpy(), columns=columns)
        horizontal_prediction['x'] = xhs*1000
        horizontal_prediction.set_index('x', inplace=True)

        vertical_prediction = pd.DataFrame(model(vertical).numpy(), columns=columns)
        vertical_prediction['y'] = yvs*1000
        vertical_prediction.set_index('y', inplace=True)

    def scale_column(column_data):
    # divide by the magnitude of the mean
        mean_exp = round(np.log10(np.mean(column_data)), 0) - 1.0
        if mean_exp <= 0.0: 
            mean_exp = 0.0
        
        return column_data/(10**mean_exp)

    # horizontal plot
    def horizontal_plot():
        fig, ax = plt.subplots(figsize=(6,3), dpi=300)
        for i, column in enumerate(columns):
            # the dataset has x and y in mm
            reference = ds[column].sel(V=300, P=60, y=0.44).values.reshape(-1, 1)
            reference = scale_column(reference)
            reference = yscalers[i].transform(reference)

            horizontal_prediction[column].plot(ax=ax, color=colors[i], label=column)
            ax.plot(reference, color=colors[i], alpha=0.3)
            ax.grid()
            ax.legend(fontsize='small')
            ax.set_ylabel('Scaled magnitude')
            ax.set_xlabel('x [mm]')

        return fig


    def vertical_plot():
        fig, ax = plt.subplots(figsize=(3,6), dpi=300)
        for i, column in enumerate(columns):
            # the dataset has x and y in mm
            reference = ds[column].sel(V=300, P=60, x=0.115, method='nearest').values.reshape(-1, 1)
            reference = scale_column(np.nan_to_num(reference))
            reference = yscalers[i].transform(reference)

            ax.plot(vertical_prediction[column].values, vertical_prediction.index.values, color=colors[i], label=column)
            ax.plot(reference, ds.y.values*1000, color=colors[i], alpha=0.3)
            ax.grid()
            ax.legend(fontsize='small')
            ax.set_xlabel('Scaled magnitude')
            ax.set_ylabel('y [mm]')

        return fig
    
    hplot = horizontal_plot()
    vplot = vertical_plot()

    if out_dir is not None:
        hplot.savefig(out_dir/'h_slices.png', bbox_inches='tight')
        vplot.savefig(out_dir/'v_slices.png', bbox_inches='tight')


def plot_train_loss(losses, validation_losses=None, out_dir=None):

    losses = np.array(losses)
    fig, ax = plt.subplots()
    ax.set_yscale('log')
    ax.plot(losses, c='r', label='train')

    try:  # im not sure what the original validation_losses is
        validation_array = np.array(validation_losses)
    except:
        validation_array = validation_losses

    if validation_losses is not None:
        ax.plot(validation_array, c='r', ls=':', label='validation')
        ax.legend()

    ax.set_xlabel('Epoch')
    ax.set_ylabel('Loss')
    ax.grid()

    if out_dir is not None:
        fig.savefig(out_dir/'train_loss.png', bbox_inches='tight')


def image_slices(reference: np.ndarray, prediction: np.ndarray, out_dir:Path=None, cmap='magma'):
    """ Evaluate slices for images.

        Vertical and horizontal slices allow us to see 1-dimensional performance of the model.
        These assume fixed lines whose positions are controlled by y and x in hslice and vslice, 
        respectively.
    Args:
        reference (np.ndarray): Array containing reference data.
        prediction (np.ndarray): Array containing (cropped) predictions.
        out_dir (Path, optional): Path where figures are saved. Defaults to None.

    Returns:
        list of plt.Figure: List containing [hplot, vplot]
    """
    columns = ['potential (V)', 'Ne (#/m^-3)', 'Ar+ (#/m^-3)', 'Nm (#/m^-3)', 'Te (eV)']
    colors = ['#d20f39', '#df8e1d', '#40a02b', '#04a5e5', '#8839ef']

    resolution = reference.shape[2]
    if (prediction.shape[2] or prediction.shape[3]) != resolution:
        raise ValueError(f'prediction (shape {prediction.shape}) is not cropped properly!')

    def hslice(y=44):
        # horizontal slice (fixed y = 44 mm)
        yidx = round(resolution*((y-35))/(55-35))  # convert y coordinate to pixel coordinate
        fig, ax = plt.subplots(figsize=(6,3), dpi=300)
        for i, column in enumerate(columns):
            refslice = reference[0, i, yidx]
            predslice = prediction[0, i, yidx]  

            x = np.linspace(0, 20, resolution)

            ax.plot(x, predslice, color=colors[i], label=column)
            ax.plot(x, refslice, color=colors[i], alpha=0.3)
            ax.grid()
            ax.legend(fontsize='small')
            ax.set_ylabel('Scaled magnitude')
            ax.set_xlabel('r [cm]')
        
        return fig
    
    def vslice(x=115):
        # vertical (fixed x = 115 mm)
        xidx = round(resolution*(x/200))
        fig, ax = plt.subplots(figsize=(3, 6), dpi=300)
        for i, column in enumerate(columns):
            refslice = reference[0, i, :, xidx]
            predslice = prediction[0, i, :, xidx] + 0.01 

            y = np.linspace(35, 55, resolution)

            ax.plot(predslice, y, color=colors[i], label=column)
            ax.plot(refslice, y, color=colors[i], alpha=0.3)
            ax.grid()
            ax.legend(fontsize='small')
            ax.set_xlabel('Scaled magnitude')
            ax.set_ylabel('z [cm]')

        return fig
    
    def slices_reference(y=44, x=115):
        global columns_math
        extent = [0, 20, 35, 55]
        fig = plt.figure(figsize=(6,2), dpi=300)
        grid = ImageGrid(fig, 111,  # similar to fig.add_subplot(142).
                     nrows_ncols=(1, 5), axes_pad=0.0, label_mode="L", share_all=True,
                     cbar_location="right", cbar_mode="single", cbar_size="5%", cbar_pad='5%')

        for i, ax in enumerate(grid):
            column = columns_math[i]

            ref = ax.imshow(reference[0, i], origin='lower', extent=extent, 
                      aspect='equal', vmin=0, vmax=reference.max(), cmap=cmap)

            ax.set_ylabel('z [cm]')
            ax.set_xlabel('r [cm]')

            cb = grid.cbar_axes[0].colorbar(ref)

            # vertical line
            ax.axvline(x/10.0, 0, 1, color='r', alpha=0.6)

            # horizontal line (raise it by 35 cause the crop is higher)
            ax.axhline(y, 0, 1, color='r', alpha=0.6)

            ax.set_title(columns_math[i%5])

            ax.xaxis.set_major_locator(ticker.MaxNLocator(3, steps=[10], prune='upper'))
            ax.xaxis.set_minor_locator(ticker.MultipleLocator(2))
            ax.yaxis.set_minor_locator(ticker.MultipleLocator(2))

            draw_apparatus(ax)

        return fig

    hplot = hslice()
    vplot = vslice()
    refplot = slices_reference()

    if out_dir is not None:
        hplot.savefig(out_dir/'h_slices.png', bbox_inches='tight')
        vplot.savefig(out_dir/'v_slices.png', bbox_inches='tight')
        name = 'slices_ref'
        if cmap != 'magma': 
            name = 'slices_ref_' + cmap
        refplot.savefig(out_dir/(name + '.png'), bbox_inches='tight')
        

    return [hplot, vplot, refplot]


def delta(reference: np.ndarray, reconstruction: np.ndarray, 
                       out_dir:Path=None, is_square=False): 
    """Create difference plot comparing the reference data with its autoencoder reconstruction.

    Args:
        reference (np.ndarray): Reference dataset.
        reconstruction (np.ndarray): Array of (cropped) prediction.
        out_dir (Path, optional): Output directory. Defaults to None.
        is_square (bool, optional): Switch between square image and full rectangle.

    Returns:
        plt.figure: Figure of absolute and relative differences.
    """
    resolution = reference.shape[2]
    if (reconstruction.shape[2] != resolution) or (reconstruction.shape[3] != resolution):
        raise ValueError(f'Prediction is not cropped properly! size={reconstruction.shape} should match {resolution}')

    if is_square:
        figsize = (6, 2)
        extent = [0, 20, 35, 55]
    else:
        figsize = (10, 5)
        extent =[0, 20, 0, 70.7]

    extent = [0, 20, 35, 55]

    fig = plt.figure(dpi=300, figsize=figsize)
    
    topgrid = ImageGrid(fig, 111,
                     nrows_ncols=(1, 5), axes_pad=0.0,
                     cbar_location="right", cbar_mode="single", cbar_size="7%", cbar_pad='5%',
                     cbar_set_cax=True)

    absdelta = reconstruction - reference  # absolute difference
    # reldelta = np.nan_to_num((reconstruction - reference)*(100/reference), posinf=500)  # consider removing this

    def absolute(arr):
        # get the absolute largest magnitude of a dataset
        arrmax = arr.flat[np.abs(arr).argmax()]
        return np.abs(arrmax)

    cbar = 'coolwarm'  # Spectral or coolwarm work
    amax = absolute(absdelta)
    # rmax = 100  # fix it to 100 for now cause division by zero ruins everything

    # plot the figures for each ImageGrid
    for i, ax in enumerate(topgrid):
        absim = ax.imshow(absdelta[0, i, :, :], origin='lower', extent=extent, aspect='auto',
                          norm=colors.SymLogNorm(0.025, vmin=-amax, vmax=amax),
                          cmap=cbar)
        draw_apparatus(ax)
        ax.set_ylabel('z [cm]', fontsize=8)
        ax.set_xlabel('r [cm]', fontsize=8)

    # for i, ax in enumerate(botgrid):
    #     relim = ax.imshow(reldelta[0, i, :, :], origin='lower', extent=extent, aspect='auto',
    #                     vmin=-rmax, vmax=rmax, cmap=cbar)
    #     draw_apparatus(ax)
    #     ax.set_ylabel('z [cm]', fontsize=8)
    #     ax.set_xlabel('r [cm]', fontsize=8)

    # colorbar settings
    cb1 = topgrid.cbar_axes[0].colorbar(absim, extend='both')
    cb1.set_label('Absolute error', rotation=270, fontsize=7, va='bottom', ha='center')
    cb1.ax.tick_params(labelsize=7)

    # cb2 = botgrid.cbar_axes[0].colorbar(relim, extend='both')
    # cb2.set_label('Percent', rotation=270, fontsize=7, va='bottom', ha='center')
    # cb2.ax.tick_params(labelsize=7)

    global columns_math
        
    # set font sizes and tick stuff
    for i, ax in enumerate(topgrid):
        ax.set_title(columns_math[i%5])
        ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(2))
        ax.xaxis.set_major_locator(ticker.MaxNLocator(3, steps=[10], prune='upper'))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(2))

        ax.tick_params(axis='both', labelsize=8)
        # ax.tick_params(bottom=False, labelbottom=False)
    
    # for i, ax in enumerate(botgrid):
    #     ax.xaxis.set_major_locator(ticker.MaxNLocator(3, steps=[10], prune='upper'))
    #     ax.xaxis.set_minor_locator(ticker.MultipleLocator(2))

    #     ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
    #     ax.yaxis.set_minor_locator(ticker.MultipleLocator(2))

    #     ax.tick_params(axis='both', labelsize=8)

    # plt.subplots_adjust(hspace=0, wspace=0)  # not sure if this does something

    plt.close()
    if out_dir is not None:
        fig.savefig(out_dir/'delta.png', bbox_inches='tight')

    return fig


def sep_comparison_ae(reference: np.ndarray, prediction: torch.tensor, 
                       model:nn.Module, out_dir=None, is_square=False, cbar='magma'): 
    """Create plot comparing the reference data with its autoencoder reconstruction.
    Each variable has its own colorbar scaling.

    Args:
        reference (np.ndarray): Reference dataset.
        prediction (torch.tensor): Tensor reshaped to match the encoding shape.
        model (nn.Module): Autoencoder model whose decoder used to make predictions.
        out_dir (Path, optional): Output directory. Defaults to None.
        is_square (bool, optional): Switch for square image and full rectangle.
            Defaults to False.
        cbar (str): Colormap used for the images. Defaults to 'magma'.

    Returns:
        float: Evaluation time (ns).
        scores: List of reconstruction MSE
    """

    resolution = reference.shape[2]
    if is_square:
        figsize = (7, 2)
        extent = [0, 20, 35, 55]
        axes_pad = 0.4
    else:
        figsize = (7, 6)
        extent =[0, 20, 0, 70.7]
        axes_pad = 0.4

    fig = plt.figure(figsize=figsize, dpi=300, layout='constrained')

    # create imagegrid for the original images (trugrid) and predicted ones (prdgrid)
    # 211 = 2x1 grid, 1st plot
    trugrid = ImageGrid(fig, 211, nrows_ncols=(1, 5), axes_pad=axes_pad, label_mode="L", share_all=True,
                     cbar_location="right", cbar_mode="each", cbar_size="10%", cbar_pad='0%')
    
    # 212 = 2x1 grid, 2nd plot
    prdgrid = ImageGrid(fig, 212, nrows_ncols=(1, 5), axes_pad=0.4, label_mode="L", share_all=True,
                     cbar_location="right", cbar_mode="each", cbar_size="10%", cbar_pad='0%')

    with torch.no_grad():
        start = time.perf_counter_ns()
        decoded = model.decoder(prediction).cpu().numpy()
        end = time.perf_counter_ns()
        reconstruction = decoded[:, :, :resolution, :resolution]  # assumes shape: (samples, channels, height, width)

    eval_time = (end-start)

    # select the maximum between the original and prediction (for each variable) to set as vmax
    cbar_ranges = [(0, max(reference[0, i].max(), reconstruction[0, i].max())) for i in range(5)]  # shape: (5, 2)

    global columns_math

    # plot the figures, vmax depends on which set (true or prediction) contains the higher values
    for i, ax in enumerate(trugrid):
        org = ax.imshow(reference[0, i, :, :], origin='lower', extent=extent, aspect='equal',
                        vmin=cbar_ranges[i][0], vmax=cbar_ranges[i][1], cmap=cbar)
        draw_apparatus(ax)
        ax.set_ylabel('z [cm]', fontsize=8)
        cb = trugrid.cbar_axes[i].colorbar(org)
        ax.set_title(columns_math[i], fontsize=10)  # set title following math labels in columns_math
        cb.ax.tick_params(labelsize=6)
 
    for i, ax in enumerate(prdgrid):
        rec = ax.imshow(reconstruction[0, i-5, :, :], origin='lower', extent=extent, aspect='equal',
                        vmin=cbar_ranges[i][0], vmax=cbar_ranges[i][1], cmap=cbar)
        draw_apparatus(ax)
        ax.set_ylabel('z [cm]', fontsize=8)
        ax.set_xlabel('r [cm]', fontsize=8)
        cb = prdgrid.cbar_axes[i].colorbar(rec)
        cb.ax.tick_params(labelsize=6)

    # set font sizes and tick stuff
    for grid in [trugrid, prdgrid]:
        for j, ax in enumerate(grid):
            ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
            ax.xaxis.set_minor_locator(ticker.MultipleLocator(2))

            ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
            ax.yaxis.set_minor_locator(ticker.MultipleLocator(2))
            ax.tick_params(axis='both', labelsize=8)

    for ax in trugrid:
        ax.tick_params(labelbottom=False)  # remove bottom labels on the upper set

    # plt.subplots_adjust(hspace=0)  # not sure if this does anything

    # record scores
    scores = []
    for i in range(5):
        score = mse(reference[0, i, :, :], reconstruction[0, i, :, :])
        scores.append(score)

    name = 'sep_test_comparison'
    if cbar != 'magma':
        name = 'sep_test_comparison_' + cbar

    if out_dir is not None:
        fig.savefig(out_dir/f'{name}.png', bbox_inches='tight')

    return eval_time, scores


def plot_imageset(image, v=300.0, p=60.0, cmap='viridis', out_dir=None):
    """
    Plot a set of images for each plasma parameter.

    Based on sep_test_comparison code.
    """

    resolution = image.shape[2]
    # if is_square:
    extent = [0, 20, 35, 55]
    columns_math = ['$\phi$', '$n_e$', '$n_i$', '$n_m$', '$T_e$']

    fig = plt.figure(figsize=(7,2), dpi=300, layout='constrained')

    # create imagegrid for the original images (trugrid) and predicted ones (prdgrid)
    grid = ImageGrid(fig, 111, nrows_ncols=(1, 5), axes_pad=0.3, label_mode="L", share_all=True,
                     cbar_location="right", cbar_mode="each", cbar_size="5%", cbar_pad='0%')
    
    cbar_ranges = [(0, image[0, i].max()) for i in range(5)]  # shape: (5, 2)

    # plot the figures, vmax depends on which set (true or prediction) contains the higher values
    for i, ax in enumerate(grid):
        org = ax.imshow(image[0, i, :, :], origin='lower', extent=extent, aspect='equal',
                        vmin=cbar_ranges[i][0], vmax=cbar_ranges[i][1], cmap=cmap)
        draw_apparatus(ax)
        ax.set_ylabel('z [cm]', fontsize=8)
        ax.set_xlabel('r [cm]', fontsize=8)
        cb = grid.cbar_axes[i].colorbar(org)
        ax.set_title(columns_math[i])  # set title following math labels in columns_math
        cb.ax.tick_params(labelsize=6)

        # ax tick stuff
        ax.xaxis.set_major_locator(ticker.MaxNLocator(3, steps=[10], prune='upper'))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(2))

        ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(2))
        ax.tick_params(axis='both', labelsize=8)

    fig.suptitle(f'({v}, {p})')

    return fig


def image_compare(reference: np.ndarray, prediction: np.ndarray, out_dir=None, 
                  is_square=False, cmap='magma', unscale=False, minmax_scheme='true'): 
    """Create plot comparing the reference data with its autoencoder reconstruction.
    Each variable has its own colorbar scaling.

    Based on previous plot_comparison and sep_comparison plots. This now just makes the plots for a given prediction.

    Args:
        reference (np.ndarray): Reference dataset.
        prediction (np.ndarray): NumPy array matching reference size.
        out_dir (Path, optional): Output directory. Defaults to None.
        is_square (bool, optional): Switch for square image and full rectangle.
            Defaults to False.
        cmap (str, optional): Colormap used for the images. Defaults to 'magma'.
        unscale (bool, optional): Whether to reverse the minmax in the plots.
        minmax_scheme ('true', '99', or '999'): If unscaling, determine how the maximum value is selected.
            Minimum is always 0.

    Returns:
        float: Evaluation time (ns).
        scores: List of reconstruction MSE
    """

    matplotlib.rcParams["font.size"] = 7
    reconstruction = prediction  # I don't feel like changing all that at the bottom yet

    resolution = reference.shape[2]
    if is_square:
        figsize = (9, 2)
        extent = [0, 20, 35, 55]
        axes_pad = 0.3
    else:
        figsize = (15.4, 4)
        extent =[0, 20, 0, 70.7]
        axes_pad = 0.4

    fig = plt.figure(figsize=figsize, dpi=300, layout='constrained')

    # create imagegrid for each parameter containing the original and prediction
    def create_imagegrid(location:int):
        if is_square:
            return ImageGrid(fig, location, nrows_ncols=(2, 1), axes_pad=0.0, label_mode="L", share_all=True,
                  cbar_location="right", cbar_mode="single", cbar_size="4%", cbar_pad='3%')
        else:
            return ImageGrid(fig, location, nrows_ncols=(1, 2), axes_pad=0.0, label_mode="L", share_all=True,
                  cbar_location="right", cbar_mode="single", cbar_size="7%", cbar_pad='3%')
    
    phi_grid = create_imagegrid(151) 
    ne_grid = create_imagegrid(152) 
    ni_grid = create_imagegrid(153) 
    nm_grid = create_imagegrid(154)
    te_grid = create_imagegrid(155)

    # get the maximum of every parameter
    # TODO: this should be a separate function
    if unscale:
        data_dir = Path.cwd()/'data'/'interpolation_datasets'/'synthetic'  # TODO: fix this
        ds = xr.open_dataset(data_dir/'synthetic_averaged.nc')
        vars = list(ds.keys())

        minmax_schemes = ['true', '99', '999']

        if minmax_scheme not in minmax_schemes:
            raise ValueError(f'Invalid minmax scheme: {minmax_scheme}. Expected one of {minmax_schemes}')

        def get_max(variable, minmax_scheme=minmax_scheme):
            var_data = np.nan_to_num(ds[variable].values)
            if minmax_scheme == 'true':
                return var_data.max()  # use minmax values
            elif minmax_scheme == '999':
                return np.quantile(var_data, 0.999)
            elif minmax_scheme == '99':
                return np.quantile(var_data, 0.99)

        # convert to a vector to broadcast to an np array
        maxima = np.array([get_max(var) for var in vars]).reshape(5, 1, 1)

        # unscale the arrays
        reference = reference * maxima
        reconstruction = reconstruction * maxima

    # select the maximum between the original and prediction (for each variable) to set as vmax
    cbar_ranges = [(0, max(reference[0, i].max(), reconstruction[0, i].max())) for i in range(5)]  # shape: (5, 2)

    global columns_math
    units_list = [' (V)',
                  ' ($\mathrm{m^{-3}}$)',
                  ' ($\mathrm{m^{-3}}$)',
                  ' ($\mathrm{m^{-3}}$)',
                  ' (eV)']

    # plot the figures, vmax depends on which set (true or prediction) contains the higher values
    for i, grid in enumerate([phi_grid, ne_grid, ni_grid, nm_grid, te_grid]):
        org = grid[0].imshow(reference[0, i, :, :], origin='lower', extent=extent, aspect='equal',
                        vmin=cbar_ranges[i][0], vmax=cbar_ranges[i][1], cmap=cmap)
        
        rec = grid[1].imshow(reconstruction[0, i, :, :], origin='lower', extent=extent, aspect='equal',
                        vmin=cbar_ranges[i][0], vmax=cbar_ranges[i][1], cmap=cmap)
        
        if unscale:
            title = columns_math[i] + units_list[i]
            grid[0].set_title(title, fontsize=9)
        else:
            grid[0].set_title(columns_math[i], fontsize=9)
        cb = grid.cbar_axes[0].colorbar(org)
        cb.ax.tick_params(labelsize=6)
        for ax in grid:
            draw_apparatus(ax)

    # set font sizes and tick stuff
    for grid in [phi_grid, ne_grid, ni_grid, nm_grid, te_grid]:
        for j, ax in enumerate(grid):
            ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
            ax.xaxis.set_minor_locator(ticker.MultipleLocator(2))

            ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
            ax.yaxis.set_minor_locator(ticker.MultipleLocator(2))
            ax.tick_params(axis='both', labelsize=7)

    name = 'image_compare'
    if cmap != 'magma':
        name = 'image_compare_' + cmap

    if out_dir is not None:
        fig.savefig(out_dir/f'{name}.png', bbox_inches='tight')
        # fig.savefig(out_dir/f'{name}.svg', bbox_inches='tight')

    return fig
