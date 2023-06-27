import datetime
import pymysql.connections

class Database:
    def __init__(self):
        self.conn = pymysql.connect(
            host="localhost",
            user="root",
            password="84789791",
            database="chat"
        )
        self.cursor = self.conn.cursor()

    def insert_chatlog(self,user_id,req_content,res_content,prompt_tokens,completion_tokens,total_tokens):
        sql = "INSERT INTO chat_wecom (user_id,req_content,res_content,prompt_tokens,completion_tokens,total_tokens,created_at) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        values = (user_id, req_content,res_content,prompt_tokens,completion_tokens,total_tokens,datetime.datetime.now())
        self.cursor.execute(sql, values)
        self.conn.commit()



