import time


# args
# kwargs 默认参数
# log(1, 2, 3, a='b', c='d')
# args [1,2,3]
# kwargs { "a":'b', "c":'d'}
def log(*args, **kwargs):
    # time.time() 返回 unix time
    # 如何把 unix time 转换为普通人类可以看懂的格式呢？
    time_format = '%Y/%m/%d %H:%M:%S'
    value = time.localtime(int(time.time()))
    formatted = time.strftime(time_format, value)
    print(formatted, *args, **kwargs)
