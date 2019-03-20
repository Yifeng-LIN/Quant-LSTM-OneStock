import keras
import numpy as np
from numpy import save, load
from numpy import concatenate
from pandas import DataFrame
from pandas import read_csv
from pandas import concat
from A_Parameters import *
from B_SourceData import *
from C_StructureData import *
from D_ModelTrain import *
from E_PredicAll import *
from F_BackTesting import *



# Run mode define
RunSourceData    = 1
RunStructureData = 1
RunModelTrain    = 1
RunPredicNew     = 1
RunBackTesting   = 1



# Import parameters for Grid search
P = Parameters()
Cum_number = 0
Cum_portofolio = 0
for i in range(len(P)):
    change       = P[i][0]
    epoch        = P[i][1]
    batch        = P[i][2]
    drop         = P[i][3]
    SourceStart  = P[i][4] 
    TestFrom     = P[i][5] 
    TestTo       = P[i][6]



    # Run all process
    # 1) Import source data 
    print ("\n\n=======>>=======>>=======>>=======>>=======>>=======>>=======>>>>>>>")
    if RunSourceData  == 1:# and Cum_number == 0:
        print ("\n******************** 1) Import source data  ********************")
        SourceEnd = TestTo
        data_cont, data_name = SourceData(SourceStart, SourceEnd)
        save("Par-DataSource.npy", [data_cont, data_name])



    # 2) Structuring data 
    if RunStructureData  == 1:# and Cum_number == 0:
        print ("\n******************** 2) Structuring data    ********************")
        perc_train = 90
        n_steps    = 20
        
        # Load parameters
        param = load("Par-DataSource.npy")
        data_cont, data_name = param[0], param[1]
        
        # Structuring data
        train_X, train_y, val_X, val_y, test_X, test_y, dummy_y, test_dt, dateindex = StructureData(perc_train, n_steps, data_cont, data_name, change, TestFrom, TestTo)
        save("Par-DataStructure.npy", [train_X, train_y, val_X, val_y, test_X, test_y, dummy_y, test_dt, dateindex])



    # 3) LSTM train and validation
    if RunModelTrain == 1:
        print ("\n******************** 3) Training process    ********************")
    
        # Parameter definite
        ep = epoch
        bs = batch
        dr = drop
        
        # Load parameters
        param = load("Par-DataStructure.npy")
        train_X, train_y = param[0], param[1]
        val_X, val_y     = param[2], param[3]
        test_X, test_y   = param[4], param[5]
    
        # Train process
        ModelTrain(train_X, train_y, val_X, val_y, test_X, test_y, ep, bs, dr)



    # 4) Predict all data
    if RunPredicNew == 1:
        print ("\n******************** 4) Prediction process  ********************")
    
        # Load parameters
        param = load("Par-DataStructure.npy")
        train_X, train_y = param[0], param[1]
        val_X, val_y     = param[2], param[3]
        test_X, test_y   = param[4], param[5]
        dummy_y, dateindex = param[6], param[8]
    
        # Prediction
        model = keras.models.load_model("model.h5")
        data_X = concatenate((train_X, val_X, test_X), axis = 0)
        dummy_yhat = model.predict(data_X)

        # Use data to NoTestTo
        NoTestTo   = list(dateindex.strftime('%Y-%m-%d')).index(TestTo)+1
        dummy_yhat = dummy_yhat[:NoTestTo, :]
                
        # All_y dataframe
        all_y = np.zeros(len(dateindex))
        all_y[dummy_y[:,0]==1] = 1
        all_y[dummy_y[:,1]==1] = 0
        all_y[dummy_y[:,2]==1] = -1
        df_all_y = DataFrame(all_y, index=dateindex, columns=["y"])
        
        # All_yhat dataframe
        all_yhat = np.zeros(len(dateindex))
        all_yhat[dummy_yhat[:,0] == np.max(dummy_yhat,axis=1)] = 1
        all_yhat[dummy_yhat[:,1] == np.max(dummy_yhat,axis=1)] = 0
        all_yhat[dummy_yhat[:,2] == np.max(dummy_yhat,axis=1)] = -1
        df_all_yhat = DataFrame(all_yhat, index=dateindex, columns=["yhat"])

        # All yyhat dataframe
        df_all_yyhat = concat([df_all_y, df_all_yhat], axis=1)
        df_all_yyhat.to_csv("Allyyhat.csv")

        # Save to dataSinal
        df_all_close = read_csv("Alldata.csv", index_col=0, usecols=[0,1])
        df_all_close.columns = ['Close']
        df_all_open = df_all_close.shift(1)
        df_all_open.columns = ['Open']
        df_all_sig = df_all_yhat.shift(-1)
        df_all_sig.columns = ['Signal']
        df_all_signal = concat([df_all_close, df_all_open, df_all_sig], axis=1)
        df_all_signal.to_csv("Allsignal.csv")



    # 5) Backtest
    if RunBackTesting == 1:
        print ("\n******************** 5) Backtesting process ********************")
    
        # Load parameters
        param = load("Par-DataStructure.npy")
        test_dt = param[7]
        fromdate = test_dt.date()
        
        # Backtesting
        Porto_TrainVal = BackTesting()
        Porto_Test     = BackTesting(fromdate)
        
        # Average potofolio
        Cum_number += 1
        Cum_portofolio += Porto_Test
        Av_Porto_Test = Cum_portofolio / Cum_number
    
        # Save result
        with open("Log-Result.txt", "a") as f:
            print ("\nTest from : "+str(fromdate), file=f)
            print ("Case   /  Change  /  epoch  /  batch  /  drop", file=f)
            print ("No."+str(i+1)+"  /  "+str(change)+"   /  "+str(epoch)+"    /  "+str(batch)+"     /  "+str(drop), file=f)
            print ("Portofolio at the end of all period is  : "+str(round(Porto_TrainVal)), file=f)
            print ("Portofolio at the end of test period is : "+str(round(Porto_Test)), file=f)
            print ("Mean portofolio for test period is      : "+str(round(Av_Porto_Test)), file=f)

