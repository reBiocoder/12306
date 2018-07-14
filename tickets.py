"""
Usage:
ticket.py <from> <to> <date>
"""
from  prettytable  import PrettyTable
import  requests
from  stations  import site
import  json
from  PIL   import   Image
from  bs4  import  BeautifulSoup
from docopt import  docopt
from colorama import init,Fore,Back,Style
import  get_ticket
arugments=docopt(__doc__)
from_station=arugments["<from>"]
from_station_code=site[from_station]
to_station=arugments["<to>"]
to_station_code=site[to_station]
date=arugments["<date>"]
requests.packages.urllib3.disable_warnings()
url="https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT".format(date,from_station_code,to_station_code)
r=requests.get(url,verify=False)
all_info_list=r.json()['data']['result']
#反转字典
reversal_stations={v:k for k,v in site.items()}
tb=PrettyTable()
tb.field_names=[Fore.LIGHTWHITE_EX+"序号",Fore.LIGHTGREEN_EX+"车次编号",Fore.LIGHTWHITE_EX+"出发地",Fore.LIGHTGREEN_EX+"终点",Fore.LIGHTBLUE_EX+"出发时间",Fore.LIGHTWHITE_EX+"结束时间",Fore.LIGHTGREEN_EX+"总耗时",Fore.RED+"特等座",Fore.LIGHTYELLOW_EX+"一等座",Fore.GREEN+"二等座",Fore.LIGHTWHITE_EX+"无座"+Fore.RESET,Fore.MAGENTA+"硬座",Fore.YELLOW+"硬卧",Fore.LIGHTMAGENTA_EX+"软卧"]
init(autoreset=False)
class Colored(object):
    #  前景色:红色  背景色:默认
    def red(self, s):
        return Fore.LIGHTRED_EX + s + Fore.RESET
    #  前景色:绿色  背景色:默认
    def green(self, s):
        return Fore.LIGHTGREEN_EX + s + Fore.RESET
    def yellow(self, s):
        return Fore.LIGHTYELLOW_EX + s + Fore.RESET
    def white(self,s):
        return Fore.LIGHTWHITE_EX + s + Fore.RESET
    def blue(self,s):
        return Fore.LIGHTBLUE_EX + s + Fore.RESET
k=1
color=Colored()
for  info_list  in  all_info_list:
    all_list = []
    all_list.append(k)
    list_text=info_list.split("|")
    number=list_text[3]
    number=color.green(number)
    all_list.append(number)
    from_sub_code=list_text[6]
    from_sub=reversal_stations[from_sub_code]
    from_sub = color.white(from_sub)
    all_list.append(from_sub)
    to_sub_code=list_text[7]
    to_sub=reversal_stations[to_sub_code]
    to_sub=color.green(to_sub)
    all_list.append(to_sub)
    first_time=list_text[8]
    first_time=color.blue(first_time)
    all_list.append(first_time)
    finally_time=list_text[9]
    finally_time=color.white(finally_time)
    all_list.append(finally_time)
    all_time=list_text[10]
    all_time=color.green(all_time)
    all_list.append(all_time)
    premier_seat=list_text[-5]  or  "--"
    premier_seat=color.red(premier_seat)
    all_list.append(premier_seat)
    first_seat=list_text[-6]  or  "--"
    first_seat=color.yellow(first_seat)
    all_list.append((first_seat))
    sec_seat=list_text[-7]   or "--"
    sec_seat=color.green(sec_seat)
    all_list.append(sec_seat)
    no_seat=list_text[-11]   or  "--"
    no_seat=color.white(no_seat)
    all_list.append(no_seat)
    hard_seat=list_text[-8]   or  "--"
    all_list.append(hard_seat)
    hard_sleeper=list_text[-9]  or  "--"
    all_list.append(hard_seat)
    soft_sleeper=list_text[-14]  or  "--"
    all_list.append(soft_sleeper)
    tb.add_row(all_list)
    tb.padding_width = 1
    k=k+1
print(tb)
#----------------查票完成--------------------------
#---------------下面开始验证登录-------------
username=input("请12306账号：")
password=input("请输入密码：")
mail2=input("请输入您的邮箱（抢票成功之后会自动给您发送邮件）：")
train =get_ticket.Train()
train.login(username,password)
train.check(date,from_station,to_station)
train.order(mail2)







