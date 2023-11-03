from generator_c import Generator
                 
if __name__ == "__main__":
    for app in [17577]:
        for i in range(1,13):
            tmp=Generator(i, data_root="./data/", total_app=app)
            function_list=tmp.gen()
    # print(tmp.get_memory(function_list[0]))
    # print(tmp.get_duration(function_list[0]))