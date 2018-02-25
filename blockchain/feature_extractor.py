# encoding:utf8
import json
import os
from skimage import io
from skimage.filters import sobel

def output_image_to_array(file_path):
    file = os.path.join(file_path)
    image = io.imread(file, as_grey=True)
    edge_sobel = sobel(image)
    return edge_sobel

if __name__ == '__main__':
    img_list = [
        'c0719e49d8948a746fb49df75091e420.jpg',
        'a4849bc3c44376b913234e83a338ce3d.jpg',
        'a735b18701ef7915cc996c7956017059.jpg',
        'a3e3b01b134ec84c68a7a918e0b35863.jpg',
        '107da4fb98566238a4d045f659a71b24.jpg'
    ]

    crawled_url = 'http://digi.163.com/18/0222/06/DB7R8CND001680NS.html'
    with open('./source/crawled_pic_feature.txt', 'wb') as f:
        data = {}
        for each in img_list:
            feature = output_image_to_array('./img/%s'%each)
            feature_hash = hash(str(feature))
            data[feature_hash] = crawled_url
        f.write(json.dumps(data))
