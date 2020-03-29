#!/usr/bin/python
# encoding: utf-8

from workflow import Workflow, web
from lxml import etree
import sys,os

# eg: cvt 100 
def calc(amount,datas):
    res = list()
    for data in datas:
        t_dic = dict()
        total = float(amount) * (100 / float(data['hui_sell']))
        t_dic['type'] = data['type']
        t_dic['total'] = float("{0:.4f}".format(total))
        res.append(t_dic)
    return res

def get_html():
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    url = 'https://www.boc.cn/sourcedb/whpj/'
    cur_dic={'澳大利亚元':'AUD','港币':'HKD','日元':'JPY','美元':'USD'}
    curlist = list()
    headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3","Accept-Encoding": "gzip, deflate","Accept-Language": "zh-CN,zh;q=0.9,ja;q=0.8,zh-TW;q=0.7,en;q=0.6","Cache-Control": "no-cache","Connection": "keep-alive","Pragma": "no-cache","Upgrade-Insecure-Requests": "1","User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1"}
    
    try:
        result = requests.get(url,verify = False, headers = headers,timeout=5)
        result.encoding = "UTF-8"
        html = etree.HTML(result.text);
        tr_html = html.xpath('//table[1]/tr')
        for tr in tr_html[2:]:
            td = tr.xpath('td')
            cur_name = td[0].text.encode("utf-8")
            if cur_name in cur_dic.keys():
                t_dict = dict()
                t_dict['type'] = cur_dic[cur_name]
                t_dict['hui_sell'] = td[3].text
                t_dict['update_time'] = td[6].text[2:]
                curlist.append(t_dict)
        return curlist
    except requests.exceptions.ConnectionError as e:
        return -1

def main(wf):
    args = ''.join(wf.args)
    datas = wf.cached_data('data', get_html, max_age=300)

    if not len(args):
        for data in datas:
            wf.add_item(title='100 '+data['type']+' = '+data['hui_sell']+' CNY',subtitle='Update Time: '+data['update_time'],icon='icon/{0}.png'.format(data['type']),valid='yes',arg = str(data['hui_sell']))
       
    else:
        args = args.strip(" ").split(" ")
        args = [e.upper() for e in args]
        if len(args) == 1:
            if args[0].replace('.', '', 1).isdigit():
                amount = args[0]
                res = calc(amount,datas)
                for item in res:
                    wf.add_item(title = '= ' + str(item['total'])+ " " + item['type'],icon='icon/{0}.png'.format(item['type']),valid='yes',arg = str(item['total']))
            else:
                return -1 # 输入有误
        elif len(args) == 2:
            t = 2
        else:
            wf.add_item('Type \'cvt -h\' for more info')
    # temp = ''.join()
    # args = temp.strip(" ").split(" ")
    # if len(args) == 0:


            
    # elif len(args) == 1:
    #     args = args
    # elif len(args) == 2:
    #     args = args
    
    
    wf.send_feedback()



if __name__ == '__main__':
    wf = Workflow(libraries=['./lib'])
    sys.exit(wf.run(main))
    print()

    




