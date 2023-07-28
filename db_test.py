#
# from db import Database
#
# db = Database()
#
# db.insert_chatlog("cx_cbe",'小明的爸爸有两个儿子，一个儿子叫大王，另一个儿子叫什么？','根据问题描述，小明的爸爸有两个儿子，其中一个儿子的名字已知为大王。因此，另一个儿子的名字应该是小明自己。'
# ,59,105,164)
# #分支122
#
#

import  os
config_path = "./config.json"
if not os.path.exists(config_path):
    print("配置文件不存在，将使用config-template.json模板")
    config_path = "./config-template.json"
else:
    print('文件存在')