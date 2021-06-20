#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np


# In[2]:


def sn_random_numbers(shape, antithetic = True, moment_matching = True, fixed_seed = False):
    ''' shape 인수와 같은 shape를 가지면서 표준정규분포를 따르는 난수 배열 반환
    
    인수
    ====
    shape : tuple (0, n, m)
        shape (0, n, m) 형태의 배열 생성
        
    antithetic : Boolean
        대조 변수 (antithetic) 생성
        
    moment_matching : Boolean
        1차, 2차 모멘트 정합
    
    fixed_seed : Boolean
        seed를 고정하기 위한 플래그
    
    반환값
    ======
    ran : (0, n, m) 형태의 난수 배열
    
    '''
    
    if fixed_seed:
        np.random.seed(1000)
    
    if antithetic:
        ran = np.random.standard_normal((shape[0], shape[1], shape[2]/2))
        ran = np.concatenate((ran, -ran), axis = 2)
    
    else:
        ran = np.random.standard_normal(shape)
    
    if moment_matching:
        ran = ran - np.mean(ran)
        ran = ran / np.std(ran)
    
    if shape[0] == 1:
        return ran[0]
    
    else:
        return ran


# In[ ]:




