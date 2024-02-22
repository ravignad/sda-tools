# This module provides a collection of utility functions for statistical data analysis
# including linear least squares fitting, covariance ellipse calculation, cost functions, and more.
# It also includes functions for analyzing parameter estimators and statistical properties.

# Standard Library Imports
import math
from pathlib import PurePath
from typing import Tuple

# Third-Party Imports
import matplotlib.pyplot as plt
import numpy as np
import scipy


def get_ellipse(center: np.ndarray, cova: np.ndarray, nsigma: int = 1, npoints: int = 1000) -> np.ndarray:
    """
    Return the coordinates of a covariance ellipse.

    Args:
        center (np.ndarray): The center of the ellipse.
        cova (np.ndarray): The covariance matrix.
        nsigma (int, optional): The number of standard deviations for the ellipse. Defaults to 1.
        npoints (int, optional): The number of points to generate on the ellipse. Defaults to 1000.

    Returns:
        np.ndarray: The coordinates of the ellipse.
    """
    cholesky_l = np.linalg.cholesky(cova)
    t = np.linspace(0, 2 * np.pi, npoints)
    circle = np.column_stack([np.cos(t), np.sin(t)])
    ellipse = nsigma * circle @ cholesky_l.T + center
    return ellipse.T


def get_bias(estimators: np.ndarray, parameter: float) -> Tuple[float, float]:
    """
    Estimate the bias of a parameter estimator.

    Args:
        estimators (np.ndarray): Array of parameter estimators.
        parameter (float): True parameter value.

    Returns:
        tuple: Bias and standard error of the estimator.
    """
    mean = np.mean(estimators)
    bias = mean - parameter
    sigma = np.std(estimators, ddof=1)
    sigma_mean = sigma / math.sqrt(len(estimators))
    return bias, sigma_mean


def get_coverage(lower_limits: np.ndarray, upper_limits: np.ndarray, parameter: float) -> Tuple[float, float]:
    """
    Estimate the coverage of the confidence intervals.

    Args:
        lower_limits (np.ndarray): Lower limit of the confidence intervals.
        upper_limits (np.ndarray): Upper limit of the confidence intervals.
        parameter (float): True parameter value.

    Returns:
        tuple: Coverage and its standard error.
    """
    nhits = np.logical_and(lower_limits < parameter, parameter < upper_limits).sum()
    ndata = len(lower_limits)
    coverage = nhits / ndata
    coverage_error = math.sqrt(coverage * (1 - coverage) / ndata)
    return coverage, coverage_error


def get_pvalue(chi2_sim: list, chi2_obs: float) -> Tuple[float, float]:
    """
    Estimate the p-value of a chi-squared test.

    Args:
        chi2_sim (list): List of simulated chi-squared values.
        chi2_obs (float): Observed chi-squared value.

    Returns:
        tuple: P-value and its standard error.
    """
    ntail = np.sum(np.array(chi2_sim) > chi2_obs)
    ndata = len(chi2_sim)
    pvalue = ntail / ndata
    pvalue_error = math.sqrt(pvalue * (1 - pvalue) / ndata)
    return pvalue, pvalue_error


def savefigs(basename: str, formats: tuple = ('.eps', '.pdf', '.png', '.svg'), folder: str = '') -> None:
    """
    Save a figure to multiple formats and print their names.

    Args:
        basename (str): Base filename for the saved figures.
        formats (tuple, optional): Tuple of file formats to save. Defaults to ('.eps', '.pdf', '.png', '.svg').
        folder (str, optional): Folder where the figures will be saved. Defaults to ''.
    """
    fig = plt.gcf()
    for fig_format in formats:
        figure_name = PurePath(folder, basename + fig_format)
        print(f'Saving figure to {figure_name}')
        fig.savefig(figure_name)


def histogram(a, bins=10, range=None, density=None, weights=None):
    """
    Build a numpy histogram but return the bin centers instead of the edges.

    Args:
        Same as numpy.histogram
        density: same as numpy.histogram with the exception that if density is True, returns a histogram
        representing the probability density function. In contrast numpy.histogram returns a histogram normalized
        to 1 over the range specified in the input.

    Returns:
        hist (array): The values of the histogram.
        bin_centres (array): Bin centers.
    """

    hist_values, bin_edges = np.histogram(a, bins, range, density, weights)
    bin_centres = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Making the density a probability mass function by renormalizing by total number of elements
    if density is True and range is not None:
        total_elements = len(a)
        elements_in_range = np.count_nonzero( (range[0] < a) & (a < range[1]) )
        hist_values *= elements_in_range / total_elements
        
    
    return hist_values, bin_centres


def profile_histogram(x: np.ndarray, y: np.ndarray, bins: int, histo_range: tuple = None) \
        -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute a profile histogram.

    Args:
        x (np.ndarray): The x-values.
        y (np.ndarray): The y-values.
        bins (int): The number of bins.
        histo_range (tuple, optional): Range for the histogram. Defaults to None.

    Returns:
        tuple: Counts, means, standard deviations, and bin edges.
    """

    counts, bin_edges, __ = scipy.stats.binned_statistic(x, y, statistic='count', bins=bins, range=histo_range)
    means, __, __ = scipy.stats.binned_statistic(x, y, statistic='mean', bins=bins, range=histo_range)
    means2, __, __ = scipy.stats.binned_statistic(x, y*y, statistic='mean', bins=bins, range=histo_range)

    # Standard deviations with Bessel correction
    variances = counts * (means2 - means**2) / (counts-1)
    standard_deviations = np.sqrt(variances)
    
    return counts, means, standard_deviations, bin_edges


def array_rms(array):
    """
    Calculate the root of the mean of the squares of an array

    Args:
        array (np.array): input array

    Returns:
         square root of the mean of the array elements
    """
    return math.sqrt(np.mean(array ** 2))


def chi_square_test(observed: np.ndarray, mean_exp: np.ndarray, std_dev_exp: np.ndarray,
                    ddof: float = 0) -> Tuple[float, float]:
    """
    Perform a chi-square test

    Args:
        observed (np.array): observed value of the random variable
        mean_exp (np.array): expected mean of the random variable according to the null hypothesis
        std_dev_exp (np.ndarray): expected standard deviation of the random variable according 
            to the null hypothesis
        ddof (float): delta degrees of freedom

    Returns:
        tuple: observed value of the test statistic, pvalue of the test statistic
         
    """
    z_scores = (observed - mean_exp) / std_dev_exp
    test_statistic = np.sum(z_scores**2)
    degrees_of_freedom = len(observed) - ddof
    pvalue = scipy.stats.chi2.sf(test_statistic, degrees_of_freedom)
    return test_statistic, pvalue


def covariance_matrix_2d(sigma_x: float, sigma_y: float, correlation: float) -> np.array:
    covariance_matrix = np.empty(shape=(2, 2))
    covariance_matrix[0, 0] = sigma_x ** 2
    covariance_matrix[0, 1] = correlation * sigma_x * sigma_y
    covariance_matrix[1, 0] = covariance_matrix[0, 1]
    covariance_matrix[1, 1] = sigma_y ** 2
    return covariance_matrix


def normal_cost_2d(mu_mesh: np.ndarray, x_meas: np.ndarray, cov: np.ndarray) -> np.ndarray:
    """
    Calculate the normal cost of a bivariate normal variable for many points in the parameter space

    Parameters
    ----------
    mu_mesh :  np.ndarray
        Values of the 2d mu parameter. The shape of the array is (nx, ny, 2) with nx and ny the number of
        points along the x and y axis respectively
    x_meas : np.ndarray
        Measured value of the bivariate normal variable.
    cov : np.ndarray
        Covariance matrix.

    Returns
    -------
    An array with dimensions (nx, ny) containing the values of the cost function in each point
    """
    hessian_matrix = np.linalg.inv(cov)
    cost_mesh = np.einsum("kli,ij,klj->kl", x_meas-mu_mesh, hessian_matrix, x_meas-mu_mesh)
    return cost_mesh

