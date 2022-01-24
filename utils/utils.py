import glob                        # use linux wildcard syntax
import numpy as np
import sys
import pandas
import seaborn as sns
import matplotlib.pyplot as plt

#Function to read msd from a .xvg file
def msd(filename, is_print=False, is_plot=False, area=[]):
    data_file = glob.glob(filename)
    time = []
    data = []

    with open(filename,"r") as f:
        for line in f:
            if line.startswith("#"):
                words = line.split()

    # Print MSD value
    if is_print:
        print("MSD Diffusion: " + str(words[4]) + ' ' +  str(words[5]) + str(words[6]) + "e-9 m s^-2")

    # Read data
    for i,file in enumerate(data_file):
            time = np.genfromtxt(file, skip_header = 20,usecols = 0)
            data =np.genfromtxt(file, skip_header = 20, usecols = 1)

    # Plot msd
    if is_plot:
        plt.title("MSD")
        sns.lineplot(x=time,y=data)
        plt.xlabel("time")
        plt.ylabel("MSD")



    # Return data
    return time, data,str(words[4]), str(words[4]) + ' ' +  str(words[5]) + str(words[6]) + "e-9"

#Function to read desnity from a .xvg file
def density(filename, is_print=False, is_plot=False):
    # Read data and set list
    data_file = glob.glob(filename)
    length = []
    data = []

    # Read data
    for i,file in enumerate(data_file):
            length = np.genfromtxt(file, skip_header = 24,usecols = 0)
            data = np.genfromtxt(file, skip_header = 24, usecols = 1)

    # Calculate density
    density_mean = np.mean(data)

    # Print density
    if is_print:
        print("Density: " + str(density_mean) + " kg m^-3")

    if is_plot:
        plt.title("Density")
        sns.lineplot(x=length,y=data)
        plt.xlabel("Box length")
        plt.ylabel("Density")


    # Return results
    return length, data, density_mean


# Function to read experimental data from ddb excel files
def read_exp(filename, prop, temp1, p1=None, tol_temp=0, tol_p = 0, disp_tab=False, p_nan=False, plot=False, is_print=False):



    # Read excel data file
    df_all = pandas.read_excel(filename)

    # Read unit and drop first row
    unit = df_all[prop][0]
    df_all = df_all.drop(index=0)

    # Cut off references
    rows_with_nan = df_all[df_all['T'].isnull()].index.tolist()

    # Reference Table
    df_ref = df_all.truncate(before=int(rows_with_nan[0]))


    # Values table
    df = df_all.truncate(after=int(rows_with_nan[0]))
    pandas.to_numeric(df['T'])

    # Search for the desired temperature
    a = df[df['T'] <= (temp1 + tol_temp)]
    a = a[a['T'] >= (temp1 - tol_temp)]



    # Search for the desired pressure
    if p1:
        if "P" in a:
            pandas.to_numeric(df['P'])
            if p_nan:
                a['P'] = a['P'].fillna(p1)
            a = a[a['P'] <= (p1 + tol_p) ]
            a = a[a['P'] >= (p1 - tol_p) ]

    # Write the prop in vector
    data = a.to_dict()
    prop_vec = []
    ref_vec = []

    for i in (data[prop]):
        prop_vec.append(float(data[prop][i]))
        ref = df_ref[df_ref['PCP Data Set#'] == (data['Ref. Number'][i])]
        a = ref['T'].values[0]
        ref_vec.append(a.split("] ")[1])

    # Display the chossen values
    if disp_tab:
        display(a)

    if plot:
        plt.figure(figsize=(13,4))
        plt.title(filename)
        plt.subplot(1,2,1)
        sns.scatterplot(x=a['T'],y=prop_vec)
        plt.xlabel("T (K)")
        plt.ylabel(str(prop +" (" + unit +")"))
        if p1:
            if "P" in a:
                plt.subplot(1,2,2)
                sns.scatterplot(x=a['P'],y=prop_vec)
                plt.xlabel("p (bar)")
                plt.ylabel(str(prop +" (" + unit +")"))

    # Calculate mean and std
    data_amount = len(prop_vec)
    mean = np.mean(prop_vec)
    std = np.std(prop_vec)

    # Print results
    if is_print:
        print("Mean (" + prop + ") : " +  str(mean))
        print("Std  (" + prop + ") : " +  str(std))
        print("Amount of data : " + str(len(prop_vec)))

    #Return results
    return mean, std, unit, data_amount, prop_vec, ref_vec
