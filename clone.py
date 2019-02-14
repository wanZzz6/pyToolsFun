import requests
from urllib import parse
from requests.utils import urlparse
import time
import re
import os


# class SaveError(Exception):
#     pass

def request_url(url, header={}, verify=False, timeout=5):
    '''请求url， 返回Response对象'''
    global session
    try:
        print('正在请求-->', url)
        res = session.get(url, headers=header, verify=verify, timeout=timeout)
        if res.status_code < 400:
            print('Request Success!', end='--')
            return res
        raise Exception('Status Code:', res.status_code)
    except Exception as e:
        print('Request Error!!!', e)
        fail_url.add(url)


def find_href_src(html_str):
    '''提取页面所有连接，并用集合去重'''
    href = set(i for i in re.findall(r'href\s*=[\'\"]([^\'\">]*)[\'\"][^>]*>', html_str) if
               'javascript' not in i and urlparse(i).fragment == '')
    src = set(a.strip('url()') for a in re.findall(r'src=\s*[\"\']([^\"\'>]+)[\'\"]', html_str))
    return href | src


# def find_no_sufix(links):
#     '''查找没有后缀的连接，添加指定后缀，并作为页面替换规则
#     '''
#     rules = set()
#     for i in links:
#         if os.path.splitext(i)[1] == '':
#             rules.add((i, i.strip('\/') + suffix))
#     return rules

def replace_str(raw_str):
    for rule in replace_rules:
        raw_str = re.sub(rule[0], rule[1], raw_str)
    return raw_str


def url2local(url):
    '''将url 转换成本地文件名，没有后缀的连接，添加指定的后缀
    '''
    # 取url路径
    temp = urlparse(url).path
    # 分割
    temp = re.split('[\/]', temp)
    # 拼接
    local_name = os.path.join(*temp).strip('\/')
    # 获取扩展名
    sufix = os.path.splitext(local_name)[1]
    # 如果没有后缀，添加指定后缀
    if sufix == '':
        local_name += suffix
    return local_name


def collect_urls_rules(html_str):
    print('Collect url', end='--')
    clear_url = set()
    rules = []
    links = find_href_src(html_str)
    # 替换无后缀的链接
    for url in links:
        if not url.startswith(domain.strip('/')) and url.startswith('http'):
            out_link.add(url)
        # print('外链：', url)
        #         elif not url.startswith('http') or url.startswith(domain):
        else:
            url = url.replace(domain, '').strip().strip('/')
            if url and url not in have_crawl and not url in uncrawl:
                clear_url.add(url)
                if os.path.splitext(url)[1] == '':
                    rules.append((url, url.strip('/') + suffix))
    return clear_url, rules


def save_source(str_or_byte, without_domain_url, source_type="str", encoding='utf-8'):
    '''
     保存源代码，按url（去除域名）路径结构保存
    '''
    local_name = url2local(without_domain_url)

    if not os.path.exists(local_name):
        dirname = os.path.dirname(local_name)
        #  判断文件夹路径是否存在,根目录为空字符串，再创建会出错
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)
        #   以字符串形式保存
        if source_type == 'str':
            with open(local_name, 'w', encoding=encoding) as f:
                f.write(str_or_byte)
        #                 媒体文件，比特流形式保存
        elif source_type == 'byte':
            with open(local_name, 'wb') as f:
                f.write(str_or_byte)


def downloadPage(url):
    '''保存页面并收集新的url
     '''
    if not url.startswith('http'):
        full_url = domain + url
    else:
        full_url = url
    res = request_url(full_url, header=header, timeout=timeout)
    if res:
        #  判断是文本还是 媒体文件
        source_type = 'byte' if res.encoding == None else 'str'
        # 如果是文本网页，查找页面所有连接，否则pass
        if source_type == 'str':
            res.encoding = res.apparent_encoding
            links, rules = collect_urls_rules(res.text)
            print('新收集%d个链接' % len(links), end='--')
            uncrawl.update(links)
            replace_rules.extend(rules)
            print('Collect Success!', end='--')
        try:
            print('保存-', end='--')
            if source_type == 'str':
                html_str = replace_str(res.text)
                save_source(html_str, url)
            else:
                save_source(res.content, url, source_type='byte')
        except Exception as e:
            print('Save Failed!！', e)
            fail_url.add(url)
        print('Save Success!')


def init():
    try:
        with open(r'temp\have_crawl.txt', 'r') as f:
            #             f.write('\n'.join(list(have_crawl)))
            have_crawl = set(f.read().split('\n'))
    except Exception:
        have_crawl = set()
    try:
        with open(r'temp\uncrawl.txt', 'r') as f:
            uncrawl = set(f.read().split('\n'))
    except:
        uncrawl = set()
    return have_crawl, uncrawl


def exit(have_crawl, uncrawl, out_link):
    try:
        with open(r'temp\have_crawl.txt', 'w') as f:
            f.write('\n'.join(list(have_crawl)))
        with open(r'temp\uncrawl.txt', 'w') as f:
            f.write('\n'.join(list(uncrawl)))
        with open(r'temp\out_links.txt', 'w') as f:
            f.write('\n'.join(list(out_link)))
    except FileNotFoundError:
        os.mkdir('temp')
        return exit(have_crawl, uncrawl, out_link)


if __name__ == "__main__":

    os.chdir(r'C:\Users\wanzheng\Desktop\D')
    # 已经爬取、未爬取 url
    have_crawl, uncrawl = init()
    # 爬取失败的 url
    fail_url = set()
    # 外链
    out_link = set()
    # 请求超时时间
    timeout = 20
    # 每个请求间隔
    sleep = 1
    # 页面内容替换规则
    suffix = '.html'
    replace_rules = []

    #  域名（末尾有斜杠）
    domain = 'https://templated.co/items/demos/caminar/'
    # 起始网页
    start = 'https://templated.co/items/demos/caminar/'
    header = {
        'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'Referer': domain,
        #         'Connection': 'keep-alive',
    }
    session = requests.Session()

    uncrawl.add(start)
    print('待爬取%d, 已爬取%d' % (len(uncrawl), len(have_crawl)))

    try:
        while uncrawl:
            url = uncrawl.pop()
            print('剩余%d个链接' % len(uncrawl))
            try:
                downloadPage(url)
            except Exception as e:
                fail_url.add(url)
                print('Error!!!', e)
                continue
            have_crawl.add(url)
            time.sleep(sleep)
    except Exception as e:
        print(e)
        exit(have_crawl, uncrawl)
        print('已保存爬取状态')