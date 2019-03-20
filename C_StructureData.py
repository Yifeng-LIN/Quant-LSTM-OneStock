import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame
from pandas import concat
from keras.wrappers.scikit_learn import KerasClassifier
from keras.utils import np_utils
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder



# Parameters
logfile   = 'Log-DataSet.txt'
datafile  = 'Alldata.csv'
datafileY = 'AlldataY.csv'



def PrintLog(logfile, overwrite, txt):
    with open(logfile, overwrite) as f:
        print(txt, file=f)
    print(txt)



def StructureData(perc_train, n_steps, data_cont, data_name, change, TestFrom, TestTo): 

    data_cont[0] = data_cont[0].squeeze().dropna()
    data = data_cont[0]
    for i in range(1, len(data_cont)):
        data_cont[i] = data_cont[i].squeeze().dropna()
        data = concat([data, data_cont[i].squeeze()], axis=1, join_axes=[data_cont[0].index])
        i+=1
    PrintLog(logfile, 'w', "Datas range:")
    for i in range(0, len(data_cont)):
        Text1 = str(data_name[i]) + str(", ")
        Text2 = str(data_cont[i].index[0].date()) + str(", ")
        Text3 = str(data_cont[i].index[-1].date()) + str(", ")
        Text4 = str(data_cont[i].shape) + str(", ")
        PrintLog(logfile, 'a', Text1+Text2+Text3+Text4)
    
    data.columns = data_name
    data = data.interpolate(method="time")
    data = data.dropna()
    Text1 = str("\nAlldata , ")
    Text2 = str(data.index[0].date()) + str(", ")
    Text3 = str(data.index[-1].date()) + str(", ")
    Text4 = str(data.shape) + str(", ")
    PrintLog(logfile, 'a', Text1+Text2+Text3+Text4)
    
    plt.plot(data)
    plt.show()
    
    # convert series to supervised learning
    def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
        n_vars = 1 if type(data) is list else data.shape[1]
        df = DataFrame(data)
        df_name = list(df)
        Text1 = str("\nData shape :       ")
        Text2 = str(df.shape) 
        PrintLog(logfile, 'a', Text1+Text2)
        cols, names = list(), list()
        
        # input sequence (t-n, ... t-0)
        for i in range(n_in, 0, -1):
            cols.append(df.shift(i))
            for j in range(n_vars):
                temps = str('In_' + '(t-%d)_' % (i) + str(df_name[j]))
                names.append(temps)
        
        # forecast sequence (t, t+1, ... t+n)
        for i in range(0, n_out):
            cols.append(df.shift(-i))
            if i == 0:
                for j in range(n_vars):
                    temps = str('Out_' + '(t)_' + str(df_name[j]))
                    names.append(temps)
            else:
                for j in range(n_vars):
                    temps = str('Out_' + '(t+%d)_' % (i) + df_name[j])
                    names.append(temps)
        
        # put it all together
        agg = concat(cols, axis=1)
        agg.columns = names
        
        # drop rows with NaN values
        if dropnan:
            agg.dropna(inplace=True)
        return agg
    
    # normalize features    
    scalerMin = data.min(axis=0)
    scalerRng = data.max(axis=0) - data.min(axis=0)
    scaled = (data - scalerMin) / scalerRng
    
    # specify the number of lag hours
    n_features = data.shape[1]
    
    # frame as supervised learning
    reframed = series_to_supervised(scaled, n_steps, 1)
    Text1 = str("\nReframed shape :   ")
    Text2 = str(reframed.shape)
    PrintLog(logfile, 'a', Text1+Text2)
    
    # split into input and outputs
    n_obs = n_steps * n_features
    
    # definit X(Only In part) and Y(Out part)
    values = reframed.values
    
    # X definte
    data_X = values[:, :n_obs] # 50 days data before the day
    
    # Y definte
    data_y_dm1 = data.shift(1).iloc[n_steps:,0]
    data_y_day = data.iloc[n_steps:,0]
    
    # dummy (Buy No Sell)
    dummy_y = np.zeros((data_X.shape[0],3))
    dummy_y[:,0][(data_y_day / data_y_dm1) > (1+change)] = 1
    dummy_y[:,2][(data_y_day / data_y_dm1) < (1-change)] = 1
    dummy_y[:,1][dummy_y[:,0] + dummy_y[:,2] == 0] = 1    

    # date index and number samples
    dateindex  = reframed.index
    NoTestFrom = list(dateindex.strftime('%Y-%m-%d')).index(TestFrom)+1
    
    # shuffle train and test data
    train_samples = int ((NoTestFrom) * perc_train/100)
    val_samples   = int ((NoTestFrom) * (1-perc_train/100))
#    tv_samples = train_samples + val_samples
#    data_X_dummy_y = np.concatenate((data_X, dummy_y), axis=1)
#    np.random.shuffle(data_X_dummy_y[:tv_samples,:])
#    data_X = data_X_dummy_y[:, :data_X.shape[1]]
#    dummy_y = data_X_dummy_y[:, -dummy_y.shape[1]:]


    # split into train and val sets
    train_X = data_X[:train_samples, :]
    train_y = dummy_y[:train_samples, :]
    val_X   = data_X[train_samples:(train_samples+val_samples), :]
    val_y   = dummy_y[train_samples:(train_samples+val_samples), :]
    test_X  = data_X[(train_samples+val_samples):, :]
    test_y  = dummy_y[(train_samples+val_samples):, :]
    test_dt = reframed.index[(train_samples+val_samples)]
    
    # reshape input to be 3D [samples, timesteps, features]
    train_X = train_X.reshape((train_X.shape[0], n_steps, n_features))
    val_X   = val_X.reshape((val_X.shape[0], n_steps, n_features))
    test_X  = test_X.reshape((test_X.shape[0], n_steps, n_features))
    PrintLog(logfile, 'a', "\nTotal sample nb :  "+str(data.shape[0]))
    PrintLog(logfile, 'a', "Time set number :  "+str(n_steps))
    PrintLog(logfile, 'a', "Train set shape :  "+str(train_X.shape)+str(train_y.shape))
    PrintLog(logfile, 'a', "Valid set shape :  "+str(val_X.shape)+str(val_y.shape))
    PrintLog(logfile, 'a', "Test  set shape :  "+str(test_X.shape)+str(test_y.shape))
    PrintLog(logfile, 'a', "Train/Val period:  "+str(reframed.index[0])+str(" to ")+str(reframed.index[len(train_y)+len(val_y)-1]))
#    PrintLog(logfile, 'a', "Valid set period:  "+str(reframed.index[len(train_y)])+str(" to ")+str(reframed.index[len(train_y)+len(val_y)-1]))
    PrintLog(logfile, 'a', "Test  set period:  "+str(reframed.index[len(train_y)+len(val_y)])+str(" to ")+str(reframed.index[len(train_y)+len(val_y)+len(test_y)-1]))

    # save to csv
    data.iloc[n_steps:, :].to_csv(datafile)
    
    return (train_X, train_y, val_X, val_y, test_X, test_y, dummy_y, test_dt, dateindex)



if __name__ == '__main__':
    change     = 0.003
    perc_train = 90
    n_steps    = 20
    param = load("Par-DataSource.npy")
    data_cont, data_name = param[0], param[1]
    train_X, train_y, val_X, val_y, test_X, test_y, dummy_y, test_dt, dateindex = StructureData(perc_train, n_steps, data_cont, data_name, change, TestFrom, TestTo)

