from lxml import etree

def get_full_xpath(self, node, position=False, class_=False, id_=False): 
    ''' 取得节点完整xapth路径，选择是否包含位置，class，id属性'''
    path = ''
    for j in node.xpath('./ancestor-or-self::*'):  # 拼接所有祖先节点标签名及属性
        temp_str = ""
        if position == True:
            if j.tag == "div" or j.tag == "ul":
                pattern = './preceding-sibling::' + j.tag  # 添加节点的位置属性
                temp_str += "[" + str(len(j.xpath(pattern)) + 1) + "]"
        if class_ == True:
            if "class" in j.attrib:
                temp_str += '[@class="' + j.attrib["class"] + '"]'  # 添加 class属性
        if id_ == True:
            if "id" in j.attrib:
                temp_str += '[@id="' + j.attrib["id"] + '"]'  # 添加 id属性
        path += j.tag + temp_str + "/"
    path = r"//" + path.rstrip(r"/")  # 加“//”也可
    return path


def get_text_all(etree_node,space = ''):
    '''获得节点全部文字，可拼接字符'''
    all_text = ""
    for i in etree_node.xpath('./descendant-or-self::*'):
        if i.text and i.text.strip():
            all_text += i.text.strip() + space
        if i.tail and i.tail.strip():
             all_text += i.tail.strip() + space
    return all_text.strip()

'''
res = requests.get('https://www.baidu.com')
tree = etree.HTML(res.text)

'''
