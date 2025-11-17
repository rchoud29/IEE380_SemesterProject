import csv
import yaml
import random
import numpy as np
import matplotlib.pyplot as plt
import math
import datetime as dt
import pandas as pd
import os

def get_config(preference_path):
    with open(preference_path, 'r') as file:
        return yaml.safe_load(file)

def get_data(file_path):
    sprint_times = []
    with open(file_path, mode='r') as file:
        data = csv.DictReader(file)
        for line in data:
            try:
                p = float(line['gameswon'])
                sprint_times.append(p)
            except:
                continue

    return sprint_times

def get_sample(data, k):
    return random.choices(data, k=k)

def get_sample_stats(data, k, n):
    stats = {
        'data': [],
        'means': [],
        'stds': [],
        'k': k
    }
    for _ in range(n):
        sample = get_sample(data, k)
        stats['data'].append(sample)
        stats['means'].append(np.mean(sample))
        stats['stds'].append(np.std(sample, ddof=1))

    return stats

def generate_hist(stat, k, templates, bins='auto', save=False, datetime=None):
    if bins == None:
        bins = int(math.sqrt(len(stat)))
    
    plt.figure(figsize=(6, 4))
    plt.hist(stat, bins=bins, color="skyblue", edgecolor="black", alpha=0.7)
    plt.title(f"{templates['title']} (n = {k})")
    plt.xlabel(templates['x'])
    plt.ylabel(templates['y'])

    if not save:
        plt.show()
    else:
        path = f"bin/{datetime}/hist_k{k}.png"
        plt.savefig(path, dpi=300, bbox_inches='tight')

def export(sets, path=None, datetime=None):
    if path == None:
        path = f"bin/{datetime}/data.csv"

    rows = []
    for k, s in sets.items():
        for mean, std in zip(s['means'], s['stds']):
            rows.append({
                'Sample Size (n)': k,
                'Sample Mean': mean,
                'Sample StdDev': std
            })
    df = pd.DataFrame(rows)

    # Compute the summary averages
    summary = (
        df.groupby('Sample Size (n)')
          .agg({'Sample Mean': 'mean', 'Sample StdDev': 'mean'})
          .rename(columns={
              'Sample Mean': 'Average of Sample Means',
              'Sample StdDev': 'Average of Sample StdDevs'
          })
          .reset_index()
    )

    # Write both tables to the same CSV, with a blank line between
    with open(path, 'w', newline='') as f:
        summary.to_csv(f, index=False)
        f.write('\n')  # blank line for readability
        df.to_csv(f, index=False)

def main():
    config = get_config("config.yaml")
    data = get_data(config['data_path'])
    datetime = dt.datetime.now().isoformat()

    os.mkdir("bin/" + datetime)
    
    sets = {}
    for k in config['sets']:
        sets[k] = get_sample_stats(data, k, config['sample_size'])
    
    for i in sets:
        s = sets[i]
        k = s['k']
        means = s['means']
        templates = config['templates']['means']
        generate_hist(means, k, templates, save=True, datetime=datetime)

    export(sets, datetime=datetime)

main()
