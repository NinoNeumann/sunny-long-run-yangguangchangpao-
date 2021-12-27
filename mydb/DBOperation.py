import sqlite3
import pymysql

host = 'localhost'
user = 'root'
password = '123456'
db = 'test'
port = 3306


def main():
    db = pymysql.connect(host='localhost', user='root', password='123456', db='test', port=3306)
    cursor = db.cursor()
    cursor.execute()
    db.close()


def dbCreteTable():
    db = pymysql.connect(host='localhost', user='root', password='123456', db='test', port=3306)
    cursor = db.cursor()

    sql_create = '''
    create table userinfo(
    userid CHAR(30) primary key,
    username VARCHAR(30) ,
    imeicode CHAR(50),
    runtimes integer,
    morning_run integer,
    today_state integer 
    );
    '''
    try:
        cursor.execute(sql_create)
        print("create table successfully!!")
    except Exception as e:
        print(e)

    cursor.close()
    db.close()


def dbupdate(uid, runtimes, morning_run, today_state=1, imeicode = -1):
    try:
        connection = pymysql.connect(host=host, user=user, password=password, db=db, port=port)
        cursor = connection.cursor()
    except Exception as e:
        print(e)
        if connection!=None:
            connection.close()
        if cursor!=None:
            cursor.close()
    sql = '''
    update userinfo
    set runtimes={1}, morning_run={2}, today_state={3}
    where userid={0}
    '''.format(uid,int(runtimes),int(morning_run),int(today_state))

    if imeicode != -1:
        sql = '''
            update userinfo
            set runtimes={1}, morning_run={2}, today_state={3}, imeicode={4}
            where userid={0}
            '''.format(uid, int(runtimes), int(morning_run), int(today_state),str(imeicode))


    try:
        cursor.execute(sql)
        connection.commit()
    except Exception as e:
        print(e)
        connection.rollback()



def dbselect(uid):

    try:
        connection = pymysql.connect(host=host, user=user, db=db, password=password, port=port)
        cursor = connection.cursor()
    except Exception as e:
        print(e)

    sql = '''
    select * from userinfo where userid = {}
    '''.format(uid)

    try:
        cursor.execute(sql)
    except Exception as e:
        print(e)
        cursor.close()
        connection.close()
        return None

    data = cursor.fetchone()

    if data is None:
        print("there is no information of the user!!")
        return None

    userid = data[0]
    username = data[1]
    imeicode = data[2]
    runtimes = data[3]
    morning_run = data[4]
    today_state = data[5]

    print("get the user's information!!!")
    print(userid, username, imeicode, runtimes, morning_run, today_state)
    cursor.close()
    connection.close()
    return userid, username, imeicode, runtimes, morning_run, today_state




def dbInsert(userid, username, imeicode, runtimes=0, morning_run=0, today_state=1):
    try:
        connection = pymysql.connect(host=host, user=user, port=port, db=db, password=password)
        cursor = connection.cursor()
    except Exception as e:
        print(e)

    insert_sql = "insert into userinfo values ({uid}," \
                 "'{uname}','{imei}',{runtimes}," \
                 "{morning},{today_state})".format(uid=userid, uname=str(username),
                                                   imei=imeicode,
                                                   runtimes=runtimes,
                                                   morning=morning_run,
                                                   today_state=today_state)

    try:
        cursor.execute(insert_sql)
        connection.commit()
        print("insert successfully!!!")
    except Exception as e:
        connection.rollback()
        print(e)

    if connection != None:
        connection.close()
    if cursor != None:
        cursor.close()


"""
思路：
    执行之前向数据库查询用户信息：查询条件：用户姓名？
    查询到用户信息后返回imeicode 然后使用imeicode运行sunrun程序（查询这一部分是不需要再程序的一开始执行的）

    一开始遍历数据库执行所有的imei 将结果返回给数据库 如果成功执行 runningtimes+1 todayrun=1
    否则todayrun=0 不操作runningtimes

    读取数据：
        1、将用户的信息 （关键信息）存放到一个excel表中 然后用程序读取
        2、在第一次输入imeicode的时候 
            成功 获取用户信息 
                在db中查询 
                    有 更新
                    无 将用户信息添加入db中
                    
    
    先做insert函数
"""
