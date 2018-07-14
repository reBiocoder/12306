import requests
import json
import urllib.parse
import re
from  stations  import  site
import  time
import  datetime
import urllib.request
import http.cookiejar
import  yagmail
requests.packages.urllib3.disable_warnings()
class Train:
    """12306抢票"""
    def __init__(self):
        self.session = requests.session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        }
        self.site_dict = dict()
        self.secretStr = []

    def prepare(self):
            self.site_dict=site

    # 登录函数
    def login(self,username,password):
        self.username=username
        self.password=password
        print("--------------------------登陆12306系统-------------------------")
        img_code = self.session.get(
            'https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&0.8826254050991758',
            verify=False, headers=self.headers)
        with open(r'C:\Users\13016\Desktop\验证码.png', 'wb') as f:
            f.write(img_code.content)
        img_xy = input('请输入验证码坐标:')
        data = {
            'answer': img_xy,
            'login_site': 'E',
            'rand': 'sjrand',
        }
        req = self.session.post('https://kyfw.12306.cn/passport/captcha/captcha-check', verify=False,
                                headers=self.headers,
                                data=data)
        print(req.text)
        # 用户名密码
        data = {
            'username':self.username,
            'password':self.password,
            'appid': 'otn',

        }
        req = self.session.post('https://kyfw.12306.cn/passport/web/login', verify=False, headers=self.headers,
                                data=data)
        response = json.loads(req.text)
        if response['result_code'] == 0:
            data = {
                'appid': 'otn',
            }
            req = self.session.post('https://kyfw.12306.cn/passport/web/auth/uamtk', verify=False, headers=self.headers,
                                    data=data)
            response = json.loads(req.text)
            print(response)
            tk = response['newapptk']
            data = {
                'tk': tk
            }
            req = self.session.post('https://kyfw.12306.cn/otn/uamauthclient', verify=False, headers=self.headers,
                                    data=data)
            response = json.loads(req.text)
            if response['result_code'] == 0:
                print('登录成功')
                return True
        print('登录失败')
        self.login(username,password)

    # 查票函数
    def check(self, date, start, end):
        print("-------------------------------------进行内部查票------------------------------------")
        # 查询车票
        # 处理点代码
        self.prepare()
        # 查询车票
        self.date = date
        self.start = start
        self.end = end
        # train_date   出发时间
        train_date = date
        # from_station 出发站点
        from_station = self.site_dict[start]
        # to_station   到达站点
        to_station = self.site_dict[end]
        url = """https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=%s&leftTicketDTO.from_station=%s&leftTicketDTO.to_station=%s&purpose_codes=ADULT""" % (
        train_date, from_station, to_station)
        req = self.session.get(url, verify=False, headers=self.headers)
        response = json.loads(req.text)
        data = response['data']['result']
        """
        car[3]  车次
        car[8]  起始时间
        car[9]  结束时间
        car[10] 历时
        car[22] 高级软卧
        car[23] 软卧
        car[24] 动卧
        car[25] 未知
        car[26] 无座
        car[27] 软座
        car[28] 硬座
        car[29] 硬卧
        car[32] 商务座特等座
        car[31] 一等座
        car[30] 二等座

        """
        i = 1
        for line in data:
            car = line.split('|')
            self.secretStr.append(car)
            i += 1
    # 下单
    def order(self,mail2):
        self.mail2=mail2
        # data = {
        #     '_json_att': ''
        # }
        # req = self.session.post('https://kyfw.12306.cn/otn/login/checkUser', verify=False, headers=self.headers, data=data)
        # print(req.text)
        print("------------------------------进行下单操作---------------------------")
        i = eval(input('请输入下单班次(序号):'))
        data = {
            # urllib.parse.unquote()
            'secretStr': urllib.parse.unquote(self.secretStr[i - 1][0]),
            'train_date': self.date,
            'back_train_date': '2018-4-29',
            'tour_flag': 'dc',
            'purpose_codes': 'ADULT',
            'query_from_station_name': self.start,
            'query_to_station_name': self.end,
            'undefined': ''
        }
        req = self.session.post('https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest', verify=False,
                                headers=self.headers, data=data)
        if req.text.find('您还有未处理的订单') != -1:
            print('还有订单未处理，无法继续抢票！！！')
            return
        data = {
            '_json_att': ""
        }
        req = self.session.post('https://kyfw.12306.cn/otn/confirmPassenger/initDc', verify=False, headers=self.headers,
                                data=data)

        token = re.findall(r'globalRepeatSubmitToken = \'(\w+)\';', req.text)[0]
        key_check_isChange = re.findall(r"'key_check_isChange':'(\w+)',", req.text)[0]
        print("-----------------------正在查询乘客信息-------------------------")
        data = {
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token,

        }
        req = self.session.post('https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs', verify=False,
                                headers=self.headers, data=data)
        data = json.loads(req.text)
        passengers = data['data']['normal_passengers']
        k = 1
        print("可供选择的乘客姓名为：")
        for passeng in passengers:
            name=passeng["passenger_name"]
            print(k,name)
            k += 1
        k = eval(input('请输入需要购买车票乘客的序号:'))
        data = {
            'cancel_flag': '2',
            'bed_level_order_num': '000000000000000000000000000000',
            'passengerTicketStr': 'O,0,1,' + passengers[k - 1]['passenger_name'] + ',1,' + passengers[k - 1][
                'passenger_id_no'] + ',,N',
            'oldPassengerStr': passengers[k - 1]['passenger_name'] + ',1,' + passengers[k - 1][
                'passenger_id_no'] + ',1_',
            'tour_flag': 'dc',
            'randCode': '',
            'whatsSelect': '1',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token,
        }
        req = self.session.post('https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo', verify=False,
                                headers=self.headers, data=data)
        print(req.text)
        print("个人信息检查成功...")
        print("------------------------------------验证所选车次信息-------------------------------------")
        strtime = datetime.datetime.strptime(self.date, "%Y-%m-%d").date()
        gmt = "%a %b %d %Y"
        thistime = strtime.strftime(gmt) + " 00:00:00 GMT+0800(中国标准时间)"
        data = {
            'train_date':thistime,
            'train_no': self.secretStr[i - 1][2],
            'stationTrainCode': self.secretStr[i - 1][3],
            'seatType': 'O',
            'fromStationTelecode': self.secretStr[i - 1][6],
            'toStationTelecode': self.secretStr[i - 1][7],
            'leftTicket': self.secretStr[i - 1][12],
            'purpose_codes': '00',
            'train_location': self.secretStr[i - 1][15],
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token,
        }
        req = self.session.post('https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount', verify=False,
                                headers=self.headers, data=data)
        number=req.json()["data"]["ticket"]
        print(req.text)
        print("车次检查成功...")
        print("剩余票数为：{}".format(number))
        print("-----------------------------------进入排队系统---------------------------------")
        data = {
            'passengerTicketStr': 'O,0,1,' + passengers[k - 1]['passenger_name'] + ',1,' + passengers[k - 1][
                'passenger_id_no'] + ',,N',
            'oldPassengerStr': passengers[k - 1]['passenger_name'] + ',1,' + passengers[k - 1][
                'passenger_id_no'] + ',1_',
            'randCode': '',
            'purpose_codes': '00',
            'key_check_isChange': key_check_isChange,
            'leftTicketStr': self.secretStr[i - 1][12],
            'train_location': self.secretStr[i - 1][15],
            'choose_seats': '',
            'seatDetailType': '000',
            'whatsSelect': '1',
            'roomType': '00',
            'dwAll': 'N',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token
        }
        req = self.session.post('https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue', verify=False,
                                headers=self.headers, data=data)
        print("获取队列成功，下面开始抢票...")
        print("-------------------------------循环抢票，直到抢到为止------------------------------")
        m=1
        while  1:
            time1=round(time.time()*1000)
            req=self.session.get("https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?random="+str(time1)+"&tourFlag=dc&_json_att=&REPEAT_SUBMIT_TOKEN="+str(token),verify=False,headers=self.headers)
            result=req.json()["data"]["waitTime"]
            print("第{}次抢票，系统剩余等待时间为：{}".format(m,result))
            m=m+1
            if  result== -1:
                orderId=req.json()["data"]["requestId"]
                print("抢票成功，请尽快前往支付，requestId：{}".format(orderId))
                yag = yagmail.SMTP(user='1301646236@qq.com', password='xebdikvjdmpggbji', host='smtp.qq.com',port='465')
                body = "亲，您的票已经抢到了，请在半个小时之内前往支付，车票id为"+str(orderId)+str("[本抢票系统作者：我爱小徐子（知乎）]")
                yag.send(to=self.mail2, subject='12306抢票系统通知', contents=body)
                print("已发送邮件")
                break
            if  result== -2:
                print("您今日的购票次数已经达到最大限制，无法再次购票！")

