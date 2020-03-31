#!/usr/bin/python
# encoding: utf-8

from workflow import Workflow, web, ICON_WARNING
import sys,os
from lxml import etree

global cur_dic
cur_dic={'澳大利亚元':'AUD','港币':'HKD','日元':'JPY','美元':'USD'}

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

# eg: cvt 100 usd
def exchange(amount, ctype, datas):
    res = dict()
    for data in datas:
        if data['type'] == ctype:
            total = float(amount) * (float(data['hui_sell']) / 100)
            res['total'] = float("{0:.4f}".format(total))
            res['type'] = 'CNY'

    return res

def get_html():
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    url = 'https://www.boc.cn/sourcedb/whpj/'
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
        
        if len(args) == 1:
            if str(args[0]) == u'-h':
                wf.add_item(title = 'cvt', subtitle='Display the latest exchange rate from BOC.',icon='icon/Quest.png')
                wf.add_item(title = 'cvt 100', subtitle='Convert 100 CNY to other currency type.',icon='icon/Quest.png')
                wf.add_item(title = 'cvt 100 usd', subtitle='Convert 100 usd to equivalent amount of RMB',icon='icon/Quest.png')
                wf.add_item(title = "You can change the currency type in './config.json'",subtitle='Default type includes AUD,USD,HKD,JPY',icon='icon/Quest.png')
            elif args[0].replace('.', '', 1).isdigit():
                amount = args[0]
                res = calc(amount,datas)
                for item in res:
                    wf.add_item(title = '= ' + str(item['total'])+ " " + item['type'],icon='icon/{0}.png'.format(item['type']),valid='yes',arg = str(item['total']))
            else:
                wf.add_item(title = 'Invalid input', subtitle='Type \'cvt -h\' for more info', icon=ICON_WARNING)


        elif len(args) == 2:
            amount, ctype = args[0], args[1].upper()
            if amount.replace('.', '', 1).isdigit() and ctype in cur_dic.values():
                res = exchange(amount,ctype,datas)
                wf.add_item(title = '= ' + str(res['total']) + " "+res['type'],icon='icon/{0}.png'.format(res['type'],valid='yes',arg = str(res['total'])))
            else:
                wf.add_item(title = 'Invalid input', subtitle='Type \'cvt -h\' for more info', icon=ICON_WARNING)

        else:
            wf.add_item(title = 'Invalid input', subtitle='Type \'cvt -h\' for more info', icon=ICON_WARNING)
    
    wf.send_feedback()



if __name__ == '__main__':
    wf = Workflow(libraries=['./lib'])
    log = wf.logger
    sys.exit(wf.run(main))
    print()

    




