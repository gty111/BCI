#some functions to call

import pyeeg as pe
import numpy as np
import interface
import server
from threading import Thread
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import joblib

refresh_rate = 100 #every refresh_rate times update once
data_raw = np.zeros(5000,dtype=np.int16)
shape_data_raw = data_raw.shape[0]
data_each = np.zeros(refresh_rate,dtype=np.int16)
data_band = np.zeros((5,100))
shape_data_band = data_band.shape[1]
data_band_legend = ["theta", 
                    "alpha",
                    "low_beta",
                    "high_beta",
                    "gamma"]
color_band = ["darkviolet","brown","yellowgreen","dodgerblue","darkblue"]
data_pre = np.zeros(100)
data_pre_pro = np.zeros(100) # moving average of data_pre
models = []
model_num = 5

def cal_data_pre():
    global data_pre
    prob= 0
    band = [4,8,12,16,25,45] #5 bands
    sample_rate = 500 #Sampling rate of 500 Hz
    X = pe.bin_power(data_raw[-1000:], band, sample_rate)
    X = X[0].tolist()
    X.extend([data_raw[-1000:].std(),data_raw[-1000:].mean(),data_raw[-1000:].max()-data_raw[-1000:].min(),data_raw[-1000:].max(),data_raw[-1000:].min()])
    X = np.array(X)
    X = X.reshape(1,10)
    for i in models:
        result = i.predict(X)
        prob += result[0]
    prob = prob/5
    #prob = np.round(prob/5)
    data_pre[:99] = data_pre[1:]
    data_pre[99] = prob
    data_pre_pro[:99] = data_pre_pro[1:]
    data_pre_pro[99] = data_pre[-5:].mean()

def cal_freq_band():
    global data_band
    band = [4,8,12,16,25,45] #5 bands
    sample_rate = 500 #Sampling rate of 500 Hz
    X = pe.bin_power(data_raw[shape_data_raw-refresh_rate:],band,sample_rate)
    data_band[:,:shape_data_band-1] = data_band[:,1:]
    data_band[:,-1] = X[1]

def call():
    count = 0
    while(server.STATE and server.device_state):
        if count%refresh_rate==0:
            data_raw[:shape_data_raw-refresh_rate] = data_raw[refresh_rate:]
            data_raw[shape_data_raw-refresh_rate:] = data_each
            cal_freq_band()
            cal_data_pre()
        data_one = interface.read()
        if(data_one==None):
            continue
        data_each[count%refresh_rate] = data_one
        count += 1

        
def connect():
    global models
    for i in range(model_num):
        models.append(joblib.load("model/lgb"+str(i)+".model"))
    print("models loaded")
    if(interface.mindwaveDataPointReader==None):
        interface.connect()
    #call()
    t1 = Thread(target=call)
    t1.start()
    
def draw_raw():
    fig = plt.figure(1)
    fig.set_size_inches(7.1,4)
    plt.clf()
    plt.title("data_raw")
    plt.plot([i for i in range(len(data_raw))],data_raw)
    #plt.xticks([])
    #plt.yticks([])
    plt.axis('off')
    plt.ylim(-2048,2048)
    sio = BytesIO()
    fig.savefig(sio, format='jpg',bbox_inches='tight')
    data = base64.encodebytes(sio.getvalue()).decode()
    src = 'data:image/png;base64,' + str(data)
    return src
        
def draw_band():
    fig = plt.figure(2)
    fig.set_size_inches(6.2,3.5)
    plt.clf()
    plt.title("data_band")
    for j in range(5):    
        if server.STATE_band[j]==0:
            continue
        plt.plot([i for i in range(data_band.shape[1])],
                 data_band[j],
                 label=data_band_legend[j],
                 color=color_band[j])
    plt.legend(loc=2)
    #plt.xticks([])
    plt.ylim(0,1)
    plt.axis('off')
    sio = BytesIO()
    fig.savefig(sio,format='jpg',bbox_inches='tight')
    data = base64.encodebytes(sio.getvalue()).decode()
    src = 'data:image/png;base64,' + str(data)
    return src

def draw_pre():
    fig = plt.figure(3)
    fig.set_size_inches(7.1, 4)
    plt.clf()
    plt.title("emotion")
    plt.plot([i for i in range(len(data_pre_pro))],data_pre_pro)
    #plt.xticks([])
    #plt.yticks([])
    plt.axis('off')
    plt.ylim(0,1)
    sio = BytesIO()
    fig.savefig(sio, format='jpg',bbox_inches='tight')
    data = base64.encodebytes(sio.getvalue()).decode()
    src = 'data:image/png;base64,' + str(data)
    return src
    