import matplotlib.pyplot as plt
from pandas import DataFrame
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Activation, BatchNormalization, Dropout
from keras.callbacks import ModelCheckpoint
from keras.regularizers import l1, l2


def ModelTrain(train_X, train_y, val_X, val_y, test_X, test_y, ep, bs, dr): 

    # design network
    print ("\nModel's structure: ")
    model = Sequential()
    model.add(LSTM(30, return_sequences=True, kernel_initializer='glorot_uniform', input_shape=(train_X.shape[1], train_X.shape[2])))
    model.add(BatchNormalization())
    model.add(Dropout(dr))
    model.add(LSTM(20, return_sequences=True, kernel_initializer='glorot_uniform'))
    model.add(BatchNormalization())
    model.add(Dropout(dr))
    model.add(LSTM(10, kernel_initializer='glorot_uniform'))
    model.add(BatchNormalization())
    model.add(Dropout(dr))
#    model.add(Dense(10, activation='tanh', kernel_initializer='glorot_uniform'))
#    model.add(BatchNormalization())
#    model.add(Dropout(dr))
#    model.add(Dense(10, activation='tanh', kernel_initializer='glorot_uniform'))
#    model.add(BatchNormalization())
#    model.add(Dropout(dr))
    model.add(Dense(3, activation='softmax'))
    checkpoint = ModelCheckpoint('model.h5', verbose=0, monitor='val_loss', save_best_only=True, mode='auto')  
    #model.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    print(model.summary())

    # fit network
    print ("\nModel's training process: ")    
    history = model.fit(train_X, train_y, epochs=ep, batch_size=bs, validation_data=(val_X, val_y), callbacks=[checkpoint], verbose=2, shuffle=False)
    
    # plot history
    plt.plot(history.history['loss'], label='train')
    plt.plot(history.history['val_loss'], label='val')
    plt.ylim(top=1.2)
    plt.legend()
    plt.show()

    # evaluation by val set
    val_scores = model.evaluate(val_X, val_y, verbose=0)
    print ("\nVal score:  ", val_scores)
    
    # evaluation by test set
    test_scores = model.evaluate(test_X, test_y, verbose=0)
    print ("\nTest score: ", test_scores)
    
    return ()


def PreicNew(new_X, ep, bs, dr): 

    # make a prediction
    new_yhat = model.predict(new_X)

    return ()

