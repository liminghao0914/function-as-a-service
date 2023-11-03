from Application import Application
from Function import Function
import pandas as pd
import numpy as np
from numpy import number
from collections import defaultdict
import time
import json
import os

class Function:
    def __init__(self,day,start_time,application_id,function_id,trigger,occur_count): 
        self.start_time=start_time #[0,1440]
        self.application_id=application_id #unique string from 256
        self.function_id=function_id
        self.trigger=trigger
        self.day=day
        self.occur_count=occur_count



class Application:
    def __init__(self):
        self.owner_id=0
        self.name_id=0
        self.functions=[]
        

class Generator:
    def __init__(self, day, data_root='./', total_app=10):
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
        self.day=day
        self.total_app=total_app
        tf = open(f"app_dict_{total_app}.json", "r")
        tmp = json.load(tf)
        self.app_dict = tmp[0]
        self.function_dict = tmp[1]
        
        self.invocations_function=pd.read_csv("{}invocations_per_function_md.anon.d{:02d}.csv".format(data_root,self.day))                
        
        duration_percentiles=pd.read_csv("{}function_durations_percentiles.anon.d{:02d}.csv".format(data_root,self.day))
        
        for index, row in duration_percentiles.iterrows():
            self.duration_pattern[row['HashFunction']]=[row['percentile_Average_0'],row['percentile_Average_1'],row['percentile_Average_25'],row['percentile_Average_50'],row['percentile_Average_75'],row['percentile_Average_99'],row['percentile_Average_100']]
        
        memory_percentiles=pd.read_csv("{}app_memory_percentiles.anon.d{:02d}.csv".format(data_root,self.day))        
        for index, row in memory_percentiles.iterrows():
            self.memory_pattern[row['HashApp']]=[row['AverageAllocatedMb_pct1'],row['AverageAllocatedMb_pct5'],row['AverageAllocatedMb_pct25'],row['AverageAllocatedMb_pct50'],row['AverageAllocatedMb_pct75'],row['AverageAllocatedMb_pct95'],row['AverageAllocatedMb_pct99'],row['AverageAllocatedMb_pct100']]         

    def gen(self):
        """
        _explaination_
        
        """
        start_time = time.time()
        print("total number of rows:{}".format(len(self.invocations_function)))
        for index, row in self.invocations_function.iterrows():
            function_id = row['HashFunction']
            app_id = row['HashApp']
            trigger = row['Trigger']
            if not app_id in self.app_dict:
                continue
            app_id_num = self.app_dict[app_id]  #number of invocation per application
            function_id_num = self.function_dict[function_id]   #number of invocation per function
            duration_pattern=self.duration_pattern[function_id]
            memory_pattern=self.memory_pattern[app_id]
            if (len(self.duration_pattern[function_id])==0):
                continue
            if (len(self.memory_pattern[app_id])==0):
                continue
            # for j in range(1, 1441):
            for j in range(1, 181):
                count=int(row[str(j)])
                if count == 0:
                    continue
                random_sec = np.random.uniform(0, 1, count) * 60
                duration_list = self.get_duration_vector(duration_pattern, count)
                memory_list = self.get_memory_vector(memory_pattern, count)
                function_id_list = [function_id_num] * count
                app_id_list = [app_id_num] * count
                trigger_list = [trigger] * count
                start_time_list = (j-1)*60+random_sec+(self.day-1)*24*60*60
                current_function_list = np.array([function_id_list, app_id_list, start_time_list, trigger_list, duration_list, memory_list]).T
                self.function_list.append(current_function_list)

            if (index%1000==0 and index > 0):
                print(index,"\t", time.time()-start_time)

        function_array = np.concatenate(self.function_list)
        function_array = function_array[np.argsort(function_array[:, 2].astype(float))]
        # print(function_array.shape)
        if not os.path.exists(f'./workload_{self.total_app}'):
            os.makedirs(f'./workload_{self.total_app}')
        np.save(f'./workload_{self.total_app}/day{self.day}.npy', function_array)
        self.function_list = []

    def get_duration(self,func):
        day=func.day
        function_id=func.function_id
        pattern=self.duration_pattern[function_id][day]
        random_float=np.random.uniform()*100
        if random_float<1:
            return pattern[0]+(pattern[1]-pattern[0])*(random_float-0)/(1-0)
        elif 1<=random_float<=25:
            return pattern[1]+(pattern[2]-pattern[1])*(random_float-1)/(25-1)
        elif 25<=random_float<=50:
            return pattern[2]+(pattern[3]-pattern[2])*(random_float-25)/(50-25)
        elif 50<=random_float<=75:
            return pattern[3]+(pattern[4]-pattern[3])*(random_float-50)/(75-50)
        elif 75<=random_float<=99:
            return pattern[4]+(pattern[5]-pattern[4])*(random_float-75)/(99-75)
        elif 99<=random_float<=100:
            return pattern[5]+(pattern[6]-pattern[5])*(random_float-99)/(100-99)

    def get_duration_vector(self, pattern, size):
        random_float=np.random.uniform(0, 1, size)*100
        result = np.zeros(size)
        result[random_float<=100]=(pattern[5]+(pattern[6]-pattern[5])*(random_float-99)/(100-99))[random_float<=100]
        result[random_float<=99]=(pattern[4]+(pattern[5]-pattern[4])*(random_float-75)/(99-75))[random_float<=99]
        result[random_float<=75]=(pattern[3]+(pattern[4]-pattern[3])*(random_float-50)/(75-50))[random_float<=75]
        result[random_float<=50]=(pattern[2]+(pattern[3]-pattern[2])*(random_float-25)/(50-25))[random_float<=50]
        result[random_float<=25]=(pattern[1]+(pattern[2]-pattern[1])*(random_float-1)/(25-1))[random_float<=25]
        result[random_float<1]=(pattern[0]+(pattern[1]-pattern[0])*(random_float-0)/(1-0))[random_float<1]

        return result


    def get_memory(self,func):
        day=func.day
        app_id=func.application_id
        pattern=self.memory_pattern[app_id][day]
        random_float=np.random.uniform()*100
        if random_float<1:
            return (pattern[0])*(random_float-0)/(1-0)
        elif 1<=random_float<=5:
            return pattern[0]+(pattern[1]-pattern[0])*(random_float-1)/(5-1)
        elif 5<=random_float<=25:
            return pattern[1]+(pattern[2]-pattern[1])*(random_float-5)/(25-5)
        elif 25<=random_float<=50:
            return pattern[2]+(pattern[3]-pattern[2])*(random_float-25)/(50-25)
        elif 50<=random_float<=75:
            return pattern[3]+(pattern[4]-pattern[3])*(random_float-50)/(75-50)
        elif 75<=random_float<=95:
            return pattern[4]+(pattern[5]-pattern[4])*(random_float-75)/(95-75)
        elif 95<=random_float<=99:
            return pattern[5]+(pattern[6]-pattern[5])*(random_float-95)/(99-95)
        elif 99<=random_float<=100:
            return pattern[6]+(pattern[7]-pattern[6])*(random_float-99)/(100-99)    

    def get_memory_vector(self, pattern, size):    
        random_float=np.random.uniform(0, 1, size)*100
        result = np.zeros(size)
        result[random_float<=100]=(pattern[6]+(pattern[7]-pattern[6])*(random_float-99)/(100-99))[random_float<=100]
        result[random_float<=99]=(pattern[5]+(pattern[6]-pattern[5])*(random_float-75)/(99-75))[random_float<=99]
        result[random_float<=75]=(pattern[4]+(pattern[5]-pattern[4])*(random_float-50)/(75-50))[random_float<=75]
        result[random_float<=50]=(pattern[3]+(pattern[4]-pattern[3])*(random_float-25)/(50-25))[random_float<=50]
        result[random_float<=25]=(pattern[2]+(pattern[3]-pattern[2])*(random_float-5)/(25-5))[random_float<=25]
        result[random_float<=5]=(pattern[1]+(pattern[2]-pattern[1])*(random_float-1)/(5-1))[random_float<=5]
        result[random_float<1]=(pattern[0]+(pattern[1]-pattern[0])*(random_float-0)/(1-0))[random_float<1]

        return result
                          
if __name__ == "__main__":
    for app in [17577]:
        for i in range(1,13):
            tmp=Generator(i, data_root="./data/", total_app=app)
            function_list=tmp.gen()
    # print(tmp.get_memory(function_list[0]))
    # print(tmp.get_duration(function_list[0]))