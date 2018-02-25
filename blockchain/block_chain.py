# coding:utf8
import json
import urllib
from collections import defaultdict

import requests
from flask import Flask, request

from block import Block
from taker import taker
from feature_extractor import output_image_to_array

app = Flask('block_chain')
app.config['JSON_AS_ASCII'] = False

# 当前链
chain = []
# 待插入区块链的数据
queued_data = {
    'picture_feature': [],
    'author_feature': [],
    'rights': []
}

block = {
    'picture_feature': [],
    'author_feature': [],
    'rights': []
}

tort_list = []
readed_tort_list = []

author_upload_feature = {}
feature_author_info = {}
crawled_picture_feature = {}

with open('./source/crawled_pic_feature.txt') as f:
    data = json.loads(f.read())
    crawled_picture_feature = data

# 区块链集合，其他区块链节点地址
chain_set = set()
# root_url = 'http://47.91.250.27:8889/get_url_set'
# # get all node url
# for each in requests.get(root_url).json()['data']:
#     chain_set.add(each)

# 添加创世区块
block = Block(data='None', pre_hash='None')
block.mine()
chain.append(block)

@app.route('/add_queued_data')
@taker
def add_data():
    global queued_data
    key = request.args.get('key')
    value = request.args.get('value')
    assert key in queued_data.keys(), u'请传入数据'.encode('utf8')

    queued_data[key].append(value)
    return u'添加成功'.encode('utf8')

# 挖矿
# 一般来说一个区块可以记录很多数据，类似于比特币一个区块能存储1M的数据。
# 如果平均一个交易的大小为250B，那么比特币每个区块只能记录 1024 * 1024 / 250 = 4194个交易。
# 又因为比特币大概十分钟产生一个区块，所以平均一秒能够处理7笔交易。
# 多余的交易会根据交易费用进行排队。
# 这里的例子是每次只挖最新的一条数据
@app.route('/mine')
@taker
def mine():
    # data = request.args.get('data')
    # assert data, u'请传入数据'.encode('utf8')

    pre_hash = chain[-1].hash()

    data = defaultdict(list)
    for key in queued_data.keys():
        count = 10
        while len(queued_data[key]) and count:
            data[key].append(queued_data[key].pop())
            count -= 1

    block = Block(data=data, pre_hash=pre_hash)
    block.mine()

    chain.append(block)

    return u'创建成功'.encode('utf8')

def send_sync():
    try:
        for node in chain_set:
            node_data = requests.get('http://%s/sync_chain'%node).json()['data']
            currect_chain = map(lambda x: Block.restore(x), node_data)
            # 如果新的链比现在的长并且合法的花，就替换成最新的链
            chain = currect_chain if len(chain) < len(currect_chain) and valid_chain(currect_chain) else chain
    except Exception, e:
        print e

# 验证区块链的有效性
def valid_chain(chain):
    last_block = chain[0]
    current_index = 1

    # 遍历区块并检测合法性
    while current_index < len(chain):
        block = chain[current_index]

        # 检测当前区块的pre_hash是否合法
        if block.pre_hash != last_block.hash():
            return False

        last_block = block
        current_index += 1

    return True

# 区块链共识部分
# 这个地方就是用来解决区块链冲突的问题
# 就是在所有节点里面找一个最长的合法链
@app.route('/sync_chain')
@taker
def sync_chain():
    # 获取所有节点的区块数据，并校验
    global chain
    for node in chain_set:
        node_data = requests.get('http://%s/chain'%node).json()['data']
        currect_chain = map(lambda x: Block.restore(x), node_data)
        # 如果新的链比现在的长并且合法的花，就替换成最新的链
        chain = currect_chain if len(chain) < len(currect_chain) and valid_chain(currect_chain) else chain

    return u'当前节点同步完成'.encode('utf8')

# 返回区块
@app.route('/chain')
@taker
def return_chain():
    ret = []
    for block in chain:
        ret.append(block.to_dict())

    return ret

@app.route('/regist_node')
@taker
def regest_node():
    node_url = request.args.get('url', '')

    # TODO:验证url合法性
    assert node_url, u'请传入合法的url地址'.encode('utf8')

    # 添加区块链节点
    chain_set.add(node_url)
    return u'节点注册成功'.encode('utf8')

@app.route('/get_url_set')
@taker
def get_url_set():
    global chain_set
    return chain_set

# upload picture and get feature
@app.route('/upload_feature')
@taker
def upload_feature():
    img_url = request.args.get('url')
    author = request.args.get('author')

    assert img_url and author

    with open('./img/%s'%img_url.split('/')[-1], 'wb') as f:
        resp = urllib.urlopen(img_url)
        f.write(resp.read())

    img_feature = output_image_to_array('./img/%s'%img_url.split('/')[-1])
    feature_hash = str(hash(str(img_feature)))

    if feature_hash in crawled_picture_feature:
        tort_list.append({
            'author': author,
            'img_url': img_url,
            'crawled_url': crawled_picture_feature[feature_hash]
        })

    return 'success'

# get tort
@app.route('/get_tort')
@taker
def get_tort():
    ret = []
    for each in tort_list:
        if each not in readed_tort_list:
            ret.append(each)
            readed_tort_list.append(each)

    return ret


if __name__ == '__main__':
    app.run(threaded=True)
