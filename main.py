import pymysql
import requests
import json
import time
import hashlib
import random
from sec import *
import argparse
import time

from mydb import DBOperation
import mydb

# Generate table Randomly
alphabet = list('abcdefghijklmnopqrstuvwxyz')
random.shuffle(alphabet)
table = ''.join(alphabet)[:10]

dbName = "SunRunner"

dbPath = "./DBresource" + "/" + dbName + ".sqlite"


def MD5(s):
    return hashlib.md5(s.encode()).hexdigest()


def encrypt(s):
    result = ''
    for i in s:
        result += table[ord(i) - ord('0')]
    # print(result)
    return result


def Run(IMEI, sckey):
    API_ROOT = 'http://client3.aipao.me/api'  # client3 for Android
    Version = '2.40'

    # Login
    TokenRes = requests.get(
        API_ROOT + '/%7Btoken%7D/QM_Users/Login_AndroidSchool?IMEICode=' + IMEI, headers={"version": "2.40"})
    TokenJson = json.loads(TokenRes.content.decode('utf8', 'ignore'))
    print(TokenJson)

    if not TokenJson['Success']:
        requests.get(f"https://sc.ftqq.com/{sckey}.send?text=IMEI过期")
        exit(0)

    print(TokenJson)

    # headers
    token = TokenJson['Data']['Token']
    userId = str(TokenJson['Data']['UserId'])
    timespan = str(time.time()).replace('.', '')[:13]
    auth = 'B' + MD5(MD5(IMEI)) + ':;' + token
    nonce = str(random.randint(100000, 10000000))
    sign = MD5(token + nonce + timespan + userId).upper()  # sign为大写

    header = {'nonce': nonce, 'timespan': timespan,
              'sign': sign, 'version': Version, 'Accept': None, 'User-Agent': None, 'Accept-Encoding': None,
              'Connection': 'Keep-Alive'}

    # Get User Info

    GSurl = API_ROOT + '/' + token + '/QM_Users/GS'
    GSres = requests.get(GSurl, headers=header, data={})
    GSjson = json.loads(GSres.content.decode('utf8', 'ignore'))

    Lengths = GSjson['Data']['SchoolRun']['Lengths']

    # 用户的姓名 学号
    NickName = GSjson['Data']['User']['NickName']
    UserID = GSjson['Data']['User']['UserName']
    Flag = True
    # 这两个是自己找的用户数据

    print('User Info:', GSjson['Data']['User']['UserID'], GSjson['Data']['User']['NickName'],
          GSjson['Data']['User']['UserName'], GSjson['Data']['User']['Sex'])
    print('Running Info:', GSjson['Data']['SchoolRun']['Sex'], GSjson['Data']['SchoolRun']['SchoolId'],
          GSjson['Data']['SchoolRun']['SchoolName'], GSjson['Data']['SchoolRun']['MinSpeed'],
          GSjson['Data']['SchoolRun']['MaxSpeed'], GSjson['Data']['SchoolRun']['Lengths'])

    # Start Running
    SRSurl = API_ROOT + '/' + token + \
             '/QM_Runs/SRS?S1=27.116333&S2=115.032906&S3=' + str(Lengths)
    SRSres = requests.get(SRSurl, headers=header, data={})
    SRSjson = json.loads(SRSres.content.decode('utf8', 'ignore'))

    # print(SRSjson)

    # Generate Runnig Data Randomly
    RunTime = str(random.randint(700, 800))  # seconds
    RunDist = str(Lengths + random.randint(0, 3))  # meters
    RunStep = str(random.randint(1300, 1600))  # steps

    # print(RunTime,RunStep,RunDist)

    # Running Sleep
    # StartT = time.time()
    # for i in range(int(RunTime)):
    #     time.sleep(1)
    #     # print("test")
    #     print(f"Current Minutes: {i/60:.2f} Running Progress {i*100.0/int(RunTime):.2f}")
    # print("")
    # print("Running Seconds:", time.time() - StartT)
    # print(SRSurl)
    # print(SRSjson)
    RunId = SRSjson['Data']['RunId']
    # End Running
    EndUrl = API_ROOT + '/' + token + '/QM_Runs/ES?S1=' + RunId + '&S4=' + \
             encrypt(RunTime) + '&S5=' + encrypt(RunDist) + \
             '&S6=&S7=1&S8=' + table + '&S9=' + encrypt(RunStep)
    EndRes = requests.get(EndUrl, headers=header)
    EndJson = json.loads(EndRes.content.decode('utf8', 'ignore'))
    print("-----------------------")
    print("Time:", RunTime)
    print("Distance:", RunDist)
    print("Steps:", RunStep)
    print("-----------------------")
    print(EndJson)
    if EndJson['Success']:
        print("[+]OK:", EndJson['Data'])
    else:
        print("[!]Fail:", EndJson['Data'])
    return Flag, NickName, UserID


parse = argparse.ArgumentParser(description="输入学生的 学号 姓名 和 imeicode")
# parse.add_argument('-i','--uid',help='uid 属性，非必要参数',default='0')
# parse.add_argument('-n','--uname',help='username 属性，非必要参数',default='0')
parse.add_argument('--i', '--imei', help='imeicode 属性，非必要参数', default='0')
args = parse.parse_args()
t = time.localtime()
hour = t.tm_hour

if __name__ == '__main__':

    imei = args.i

    # 指定的imeicode 的用户跑一次，并搜索这个用户在不在数据库中 如果不在添加进去 在的话就更新
    if imei != '0':
        f, nickname, userid = Run(imei, sckey)
        if f is False:
            print("跑步失败！！")
            try:
                userid, username, imeicode, runtimes, morning_run, today_state = DBOperation.dbselect(userid)
                DBOperation.dbupdate(userid, runtimes=runtimes, morning_run=morning_run, today_state=0)
            except Exception as e:
                # 将用于数据添加到数据库中
                print(e)
                print("用户跑步失败，且未在数据库中查询到用户信息")
                print("用户信息：……")
        else:
            try:
                userid, username, imeicode, runtimes, morning_run, today_state = DBOperation.dbselect(userid)
                if hour < 8:
                    morning_run = morning_run + 1
                DBOperation.dbupdate(userid, runtimes=runtimes + 1, morning_run=morning_run, imeicode=imeicode)
            except Exception as e:
                print(e)
                print("检测到新用户！！ 将用户存入数据库中……")
                temp_morning = 0
                if hour < 7:
                    temp_morning = 1
                DBOperation.dbInsert(userid, nickname, imei, runtimes=1, morning_run=temp_morning)
    else:
        # 顺序执行数据库中的imei并更新
        try:
            connection = pymysql.connect(host=mydb.host, user=mydb.user, db=mydb.db, port=mydb.port,
                                         password=mydb.password)
            cursor = connection.cursor()
        except Exception as e:
            print(e)
            print("Run 数据库中的内容时 ： 连接数据库 发生故障！！")
            exit(1)

        sql = '''
        select * from userinfo
        '''

        try:
            cursor.execute(sql)
            # connection.commit()
            dataSet = cursor.fetchall()
            for data in dataSet:
                # userid = data[0]
                # username = data[1]
                # imeicode = data[2]
                # runtimes = data[3]
                # morning_run = data[4]
                userid, username, imeicode, runtimes, morning_run = data[0:5]
                f = Run(imeicode, sckey)[0]
                # 如果在数据库中的用户在执行run后失败了那么 将today_state 设置为0 表示出现了imeicode 重置的问题！！
                if f is False:
                    DBOperation.dbupdate(userid, runtimes=runtimes, morning_run=morning_run, today_state=0, imeicode=imeicode)
                    continue

                if hour <= 8:
                    morning_run = morning_run + 1
                today_state = data[5]

                DBOperation.dbupdate(userid, runtimes + 1, morning_run)
        except Exception as e:
            print(e)

    # sys的命令行参数主要读取 姓名和userid 和 iemicode

    # uid, uname, imei = sys.argv[1:4]
    # print(uid, uname, imei)

    # if Flag:
    #     #search the user is in db or not
    #     if DBOperation.db_select(cur, userid):
    #         DBOperation.db_update(cur, userid)
    #     else:
    #         DBOperation.db_insertion(cur, userid, nickname)
    # else:
    #     # user's todayrun = 0
    #     pass
    #
    #
    # cur.close()P
    # conn.close()

    '''
    到时候是这样操作：
        /在SQLyog里面可视化窗口对数据进行更新和添加操作
        
        所以这段代码主要做的是：
            遍历数据库 执行imei 如果成功update（）
        
    
        在main函数中打开数据库 cur指针 fetch数据 bool,nickname,userid run（fetch数据）
            如果run返回 True    调用process 函数
                  返回 False  
    '''
