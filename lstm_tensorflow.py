
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
rnn_unit=10     
input_size=6
output_size=1
lr=0.0006

f=open('mydateset.csv')
df=pd.read_csv(f)     
data=df.iloc[:,0:7].values 
 
 

def get_train_data(batch_size=10,time_step=10,train_begin=0,train_end=6700):
    batch_index=[]
    data_train=data[train_begin:train_end]
    normalized_train_data=(data_train-np.mean(data_train,axis=0))/np.std(data_train,axis=0) 
    train_x,train_y=[],[]  
    for i in range(len(normalized_train_data)-time_step):
       if i % batch_size==0:
           batch_index.append(i)
       x=normalized_train_data[i:i+time_step,:6]
       y=normalized_train_data[i:i+time_step,6,np.newaxis]
       train_x.append(x.tolist())
       train_y.append(y.tolist())
    batch_index.append((len(normalized_train_data)-time_step))
    return batch_index,train_x,train_y
 
 
 

def get_test_data(time_step=10,test_begin=6700):
    data_test=data[test_begin:]
    mean=np.mean(data_test,axis=0)
    std=np.std(data_test,axis=0)
    normalized_test_data=(data_test-mean)/std
    size=(len(normalized_test_data)+time_step-1)//time_step
    test_x,test_y=[],[] 
    for i in range(size-1):
       x=normalized_test_data[i*time_step:(i+1)*time_step,:6]
       y=normalized_test_data[i*time_step:(i+1)*time_step,6]
       test_x.append(x.tolist())
       test_y.extend(y)
    test_x.append((normalized_test_data[(i+1)*time_step:,:6]).tolist())
    test_y.extend((normalized_test_data[(i+1)*time_step:,6]).tolist())
    return mean,std,test_x,test_y
 
 
weights={
         'in':tf.Variable(tf.random_normal([input_size,rnn_unit])),
         'out':tf.Variable(tf.random_normal([rnn_unit,1]))
        }
biases={
        'in':tf.Variable(tf.constant(0.1,shape=[rnn_unit,])),
        'out':tf.Variable(tf.constant(0.1,shape=[1,]))
       }
 

def lstm(X):    
    batch_size=tf.shape(X)[0]
    time_step=tf.shape(X)[1]
    w_in=weights['in']
    b_in=biases['in'] 
    input=tf.reshape(X,[-1,input_size]) 
    input_rnn=tf.matmul(input,w_in)+b_in
    input_rnn=tf.reshape(input_rnn,[-1,time_step,rnn_unit]) 
    cell=tf.nn.rnn_cell.BasicLSTMCell(rnn_unit)
    init_state=cell.zero_state(batch_size,dtype=tf.float32)
    output_rnn,final_states=tf.nn.dynamic_rnn(cell, input_rnn,initial_state=init_state, dtype=tf.float32)  #output_rnn是记录lstm每个输出节点的结果，final_states是最后一个cell的结果
    output=tf.reshape(output_rnn,[-1,rnn_unit])
    w_out=weights['out']
    b_out=biases['out']
    pred=tf.matmul(output,w_out)+b_out
    return pred,final_states
 
 
 

def train_lstm(batch_size=10,time_step=10,train_begin=0,train_end=6700):
    X=tf.placeholder(tf.float32, shape=[None,time_step,input_size])
    Y=tf.placeholder(tf.float32, shape=[None,time_step,output_size])
    batch_index,train_x,train_y=get_train_data(batch_size,time_step,train_begin,train_end)
    print(np.array(train_x).shape)
    print(batch_index)
    pred,_=lstm(X)

    loss=tf.reduce_mean(tf.square(tf.reshape(pred,[-1])-tf.reshape(Y, [-1])))
    train_op=tf.train.AdamOptimizer(lr).minimize(loss)
    saver=tf.train.Saver(tf.global_variables(),max_to_keep=10) 
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())

        for i in range(200):

            for step in range(len(batch_index)-1):
                _,loss_=sess.run([train_op,loss],feed_dict={X:train_x[batch_index[step]:batch_index[step+1]],Y:train_y[batch_index[step]:batch_index[step+1]]})
            print(i,loss_)
            if i % 200==0:
                print(saver.save(sess,'model/stock2.model',global_step=i))
 
 
train_lstm()


