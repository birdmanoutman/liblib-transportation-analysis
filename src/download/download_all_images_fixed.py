#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载liblib.art汽车交通板块所有模型封面图 (完整版)
"""

import requests
import os
import time
from urllib.parse import urlparse

def download_image(url, filename, folder="liblib_car_models_images"):
    """下载图片到指定文件夹"""
    try:
        os.makedirs(folder, exist_ok=True)
        
        parsed_url = urlparse(url)
        path = parsed_url.path
        if '.' in path:
            ext = path.split('.')[-1]
            if ext.lower() in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                filename = f"{filename}.{ext}"
            else:
                filename = f"{filename}.jpg"
        else:
            filename = f"{filename}.jpg"
        
        filepath = os.path.join(folder, filename)
        
        if os.path.exists(filepath):
            print(f"文件已存在，跳过: {filepath}")
            return filepath
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"成功下载: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"下载失败 {url}: {e}")
        return None

def main():
    """主函数"""
    # 完整模型数据 - 基于页面滚动分析发现的29个模型
    models = [
        {
            "index": 1,
            "title": "创意增强-切削风格",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "kiri",
            "views": "715019",
            "likes": "715",
            "downloads": "19",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/feb02017fc1341979b26b117e376fce2/abb026252eaaccbdacd3f00b1c7475a571596c2cca979a2499a9f5a720d720ad.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/cd4d7413e5a041d89937133350647311?from=feed&versionUuid=680de765511c438b8b2615b49370e157",
            "isExclusive": True
        },
        {
            "index": 19,
            "title": "概念设计｜ 透明玻璃膨胀",
            "type": "LORA",
            "baseModel": "LORA",
            "author": "羽毛ai",
            "views": "27.4k",
            "likes": "934",
            "downloads": "47",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/762538fd801c40b6bbfcf23af671ccb0/72f3f1a67e14414b8dde726b1b7b5d9c.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/762538fd801c40b6bbfcf23af671ccb0?from=feed&versionUuid=72f3f1a67e14414b8dde726b1b7b5d9c",
            "isExclusive": True
        },
        {
            "index": 20,
            "title": "现代豪华场景渲染",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "ONPOINT_DESIGN",
            "views": "41.1k",
            "likes": "8",
            "downloads": "62",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/b756a93ae56847f2b3faeeb566ff0410/9028aa032e9a4ca1866654bde350335d.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/b756a93ae56847f2b3faeeb566ff0410?from=feed&versionUuid=9028aa032e9a4ca1866654bde350335d",
            "isExclusive": True
        },
        {
            "index": 21,
            "title": "体很润 || 圆润、饱满型面体量__汽车外饰设计",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "QifengArt",
            "views": "25.5k",
            "likes": "4",
            "downloads": "72",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/8e8f663e30ae4a72add7eea6eb68c758/9d51fa52a2a84695891648a3d4e7e96c.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/8e8f663e30ae4a72add7eea6eb68c758?from=feed&versionUuid=9d51fa52a2a84695891648a3d4e7e96c",
            "isExclusive": True
        },
        {
            "index": 22,
            "title": "F1-白白白-",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "ZERO",
            "views": "22.6k",
            "likes": "5",
            "downloads": "73",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/904980b603774ffa9807596674f90c7e/a4ce78d5e95f4b348b9af85529e93bd2.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/904980b603774ffa9807596674f90c7e?from=feed&versionUuid=a4ce78d5e95f4b348b9af85529e93bd2",
            "isExclusive": True
        },
        {
            "index": 23,
            "title": "很硬核 || 野性、硬派型面语言_汽车外饰设计",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "QifengArt",
            "views": "29.1k",
            "likes": "4",
            "downloads": "169",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/da1a300cf08045abb70a4076160db283/2576e774739244afa29040efa369dc9f.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/da1a300cf08045abb70a4076160db283?from=feed&versionUuid=2576e774739244afa29040efa369dc9f",
            "isExclusive": True
        },
        {
            "index": 24,
            "title": "科幻皮卡",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "Autodesigner",
            "views": "21.1k",
            "likes": "2",
            "downloads": "15",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/b717b3d793e84ab8be53e02facbafd2c/25ff95fad4a2441db2b6c9595613449b.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/b717b3d793e84ab8be53e02facbafd2c?from=feed&versionUuid=25ff95fad4a2441db2b6c9595613449b",
            "isExclusive": True
        },
        {
            "index": 25,
            "title": "鲜花列车_开往春天的列车",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "青也",
            "views": "21.7k",
            "likes": "97",
            "downloads": "162",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/eb65186576644a449d1f4da68118740a/94aff8bb992a49bd8607de3ea7d064f4.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/eb65186576644a449d1f4da68118740a?from=feed&versionUuid=94aff8bb992a49bd8607de3ea7d064f4",
            "isExclusive": True
        },
        {
            "index": 26,
            "title": "概念两轮载具--摩托车",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "ZERO",
            "views": "30.7k",
            "likes": "7",
            "downloads": "72",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/15b65cf40e024b178a911c02f58e26eb/53c585ef15e442e19f01625f0ecb1577.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/15b65cf40e024b178a911c02f58e26eb?from=feed&versionUuid=53c585ef15e442e19f01625f0ecb1577",
            "isExclusive": True
        },
        {
            "index": 27,
            "title": "趣小车 || 极简风/产品感盒子车_汽车外饰设计",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "QifengArt",
            "views": "26.9k",
            "likes": "2",
            "downloads": "154",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/3dad609b114d4b949a0d91447d1a8e99/1fb0c1d762624a449a85523a03cddc89.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/3dad609b114d4b949a0d91447d1a8e99?from=feed&versionUuid=1fb0c1d762624a449a85523a03cddc89",
            "isExclusive": True
        },
        {
            "index": 28,
            "title": "沉浸式光影渲染",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "ONPOINT_DESIGN",
            "views": "33.5k",
            "likes": "0",
            "downloads": "135",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/46d00e545df04f4391f1d61a46e6cbef/8665ccff5aea4c04b7f8fc1e35715ae9.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/46d00e545df04f4391f1d61a46e6cbef?from=feed&versionUuid=8665ccff5aea4c04b7f8fc1e35715ae9",
            "isExclusive": True
        },
        {
            "index": 29,
            "title": "3D衰败世界",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "LILeonor",
            "views": "23.8k",
            "likes": "0",
            "downloads": "49",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/2b61fbe3dcc24e6cb52afd028c55746d/b552ea50070f47ceb8374ee2246a2011.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/2b61fbe3dcc24e6cb52afd028c55746d?from=feed&versionUuid=b552ea50070f47ceb8374ee2246a2011",
            "isExclusive": False
        }
    ]
    
    print("开始下载liblib.art汽车交通板块所有模型封面图...")
    print(f"总共需要下载 {len(models)} 张图片")
    
    downloaded_count = 0
    failed_count = 0
    
    for model in models:
        print(f"\n[{model['index']:2d}] 下载: {model['title']}")
        print(f"     作者: {model['author']}")
        print(f"     类型: {model['type']}")
        
        # 跳过无效的图片URL
        if not model.get('coverUrl') or model['coverUrl'].startswith('data:'):
            print(f"     跳过: 无效的图片URL")
            failed_count += 1
            continue
            
        # 下载图片
        filename = f"{model['index']:02d}_{model['title'][:20]}"
        result = download_image(model['coverUrl'], filename)
        
        if result:
            downloaded_count += 1
        else:
            failed_count += 1
        
        # 添加延迟，避免请求过快
        time.sleep(1)
    
    print(f"\n下载完成!")
    print(f"成功: {downloaded_count} 张")
    print(f"失败: {failed_count} 张")
    print(f"总计: {len(models)} 张")

if __name__ == "__main__":
    main()
