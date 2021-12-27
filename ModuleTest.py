import sys
import argparse
from mydb import DBOperation
import time
import pymysql
import mydb

# parse = argparse.ArgumentParser(description="imeicode")
# # parse.add_argument('-i','--uid',help='uid 属性，非必要参数',default='0')
# # parse.add_argument('-n','--uname',help='username 属性，非必要参数',default='0')
# parse.add_argument('--i','--imei',help='imeicode 属性，非必要参数',default='0')
# args = parse.parse_args()
#
#
# if __name__=='__main__':
#     print(type(args))
#     print(args.length())

# DBOperation.dbInsert('21312','rangang','1231321421')
# try:
#     userid, username, imeicode, runtimes, morning_run, today_state = DBOperation.dbselect('21312')
#     DBOperation.dbupdate(userid, runtimes=runtimes+1, morning_run=morning_run+1, today_state=today_state)
# except Exception as e:
#     print(e)

# DBOperation.dbInsert('121', '张昭', '9909', 1, 1)
# DBOperation.dbInsert('122', '汪涵', '9910', 1, 0)

# connection = pymysql.connect(host=mydb.host, port=mydb.port, user=mydb.user, db=mydb.db, password=mydb.password)
# cursor = connection.cursor()
# sql = '''
# select * from userinfo
# '''
# cursor.execute(sql)
#
# dataSet = cursor.fetchall()
# for data in dataSet:
#     print("=====before======")
#     userid = data[0]
#     username = data[1]
#     imeicode = data[2]
#     runtimes = data[3]
#     morning_run = data[4]
#     DBOperation.dbupdate(userid, runtimes + 1, morning_run)
#     print(userid, username, imeicode, runtimes, morning_run)
#     # data[3] = data[3]+2

DBOperation.dbCreteTable()