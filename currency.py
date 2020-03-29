#!/usr/bin/python
# encoding: utf-8

from workflow import Workflow, web
from lxml import etree
import sys



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
    if len(wf.args):
         query = 1
         amount = wf.args[0]
         itype = wf.args[1]
    else:
         query = 0
    if not query:
        datas = wf.cached_data('data',get_html,max_age=60)
        for data in datas:
            wf.add_item(title='100 '+data['type']+' = '+data['hui_sell']+' CNY',subtitle='Update Time: '+data['update_time'])
        wf.add_item(title=u'转到中行外汇牌价页',subtitle="www.boc.cn/sourcedb/whpj/",valid=True)
    else:
        print(amount,itype)
    wf.send_feedback()



if __name__ == '__main__':
    wf = Workflow(libraries=['./lib'])
    sys.exit(wf.run(main))
    print()

    




