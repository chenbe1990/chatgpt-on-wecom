import datetime
import pymysql.connections
from config import conf, load_config
from common.log import logger


class Database:
    def __init__(self):
        load_config()
        self.conn = None
        self.cursor = None
        print(conf().get("datatable"))
        try:
            self.conn = pymysql.connect(
                host=conf().get("host"),
                user=conf().get("user"),
                password=conf().get("password"),
                database=conf().get("database")
            )
            self.cursor = self.conn.cursor()
        except Exception as e:
            logger.warn(f"连接数据库时出错: {str(e)}")

    def insert_chatlog(self, user_id, req_content, res_content, prompt_tokens, completion_tokens, total_tokens):
        if not self.conn or not self.cursor:
            logger.warn("无法执行SQL语句，数据库连接未成功建立")
            return

        try:
            datatable=conf().get("datatable")
            sql = f"INSERT INTO {datatable} (user_id,req_content,res_content,prompt_tokens,completion_tokens,total_tokens,created_at) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            values = (user_id, req_content, res_content, prompt_tokens, completion_tokens, total_tokens, datetime.datetime.now())
            self.cursor.execute(sql, values)
            self.conn.commit()
        except Exception as e:
            logger.warn(f"插入聊天记录时出错: {str(e)}")

