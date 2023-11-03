from pip import main
from Application import Application
from Function import Function
import pandas as pd
import numpy as np
from numpy import number
from collections import defaultdict
import time
import json


class Sampler:
    def __init__(self, data_root='./'):
        """
        _summary_
        generate function
        randomly generate the trigger type, including Http, Queue, Event, Orchestration, Timer, Storage, Others
        randomly generator time, including Hour, Minute

        return a workload like:
        function_list = [
            Function(0, 0, 0, 3), 
            Function(0, 0, 5, 3), 
            Function(0, 0, 10, 1), 
            Function(0, 0, 15, 2), 
            Function(0, 0, 13, 1), 
            Function(0, 0, 18, 2), 
            Function(1, 0, 7, 4)
        ]
        """
        self.memory_pattern=defaultdict(list)
        self.duration_pattern=defaultdict(list)
        self.function_list=[]             
        self.data_root = data_root
        
        self.invocations_function=pd.read_csv("data/{}invocations_per_function_md.anon.d{:02d}.csv".format(data_root, 1))                
        self.function_dict = {}
        self.app_dict = {}

    def sample(self, total_app=None):
        """
        _explaination_
        
        """
        app_count = 0
        func_count = 0
        start_time = time.time()
        print("total number of rows:{}".format(len(self.invocations_function)))
        for index, row in self.invocations_function.iterrows():
            function_id = row['HashFunction']
            app_id = row['HashApp']

            if total_app is None:
                if not app_id in self.app_dict:
                    self.app_dict[app_id] = app_count
                    app_count += 1
            else:
                if not app_id in self.app_dict and app_count<total_app:
                    self.app_dict[app_id] = app_count
                    app_count += 1

            if not function_id in self.function_dict and app_id in self.app_dict:
                self.function_dict[function_id] = func_count
                func_count += 1

        for i in range(2, 13):
            self.invocations_function=pd.read_csv("data/{}invocations_per_function_md.anon.d{:02d}.csv".format(self.data_root, i))    

            for index, row in self.invocations_function.iterrows():
                function_id = row['HashFunction']
                app_id = row['HashApp']

                if not function_id in self.function_dict and app_id in self.app_dict:
                    self.function_dict[function_id] = func_count
                    func_count += 1
            
        
        print(self.app_dict)
        print("Size of app_dict: ", len(self.app_dict))
        print("Size of function_dict: ", len(self.function_dict))
        if total_app is None:
            total_app = len(self.app_dict)
        tf = open("app_dict_{}.json".format(total_app), "w")
        json.dump([self.app_dict, self.function_dict], tf)
        tf.close()
    
if __name__ == "__main__":
    # for i in [100]:
    #     tmp=Sampler()
    #     function_list=tmp.sample(i)
    tmp=Sampler()
    function_list=tmp.sample()