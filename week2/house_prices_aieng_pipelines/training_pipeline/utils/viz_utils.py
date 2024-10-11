import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm
import numpy as np

def plot_distribution(data, feature, title):
    plt.figure(figsize=(10, 6))
    sns.distplot(data[feature], fit=norm)
    plt.title(title)
    plt.xlabel(feature)
    plt.ylabel('Frequency')

    # Get the fitted parameters used by the function
    (mu, sigma) = norm.fit(data[feature])
    print('\n mu = {:.2f} and sigma = {:.2f}\n'.format(mu, sigma))

    # Plot formatting
    plt.legend(['Normal dist. ($\mu=$ {:.2f} and $\sigma=$ {:.2f})'.format(mu, sigma)], loc='best')
    plt.show()

def plot_scatter(data, x_feature, y_feature, title):
    plt.figure(figsize=(10, 6))
    plt.scatter(data[x_feature], data[y_feature], alpha=0.5)
    plt.title(title)
    plt.xlabel(x_feature)
    plt.ylabel(y_feature)
    plt.show()

def plot_missing_data(missing_data):
    plt.figure(figsize=(15, 12))
    sns.barplot(x=missing_data.index, y=missing_data['Missing Ratio'])
    plt.xlabel('Features')
    plt.ylabel('Percent of missing values')
    plt.title('Percent missing data by feature')
    plt.xticks(rotation=90)
    plt.show()

