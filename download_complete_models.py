#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载liblib.art汽车交通板块所有模型封面图 (完整版 - 28个模型)
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
    # 完整模型数据 - 基于页面滚动分析发现的28个模型
    models = [
        {
            "index": 1,
            "title": "概念设计｜ 透明玻璃膨胀",
            "type": "LORA",
            "baseModel": "LORA",
            "author": "羽毛ai",
            "views": "27.4k",
            "likes": "934",
            "downloads": "47",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/d0ab9254b0b3405db82726c4f7f3596c/bdb8c9bdcfd10af9ae6081a3ea1d6b9401f1f6a29a63df2f95dda5025d11f48a.png?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/762538fd801c40b6bbfcf23af671ccb0?from=feed&versionUuid=72f3f1a67e14414b8dde726b1b7b5d9c",
            "isExclusive": True
        },
        {
            "index": 2,
            "title": "现代豪华场景渲染",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "ONPOINT_DESIGN",
            "views": "41.1k",
            "likes": "8",
            "downloads": "62",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/617e09a4fd254522a6b8c87550327b09/a01a6158594a05c769ce5fc7f1bf754615271c6fd44bd9a1c421d4223e49050c.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/b756a93ae56847f2b3faeeb566ff0410?from=feed&versionUuid=9028aa032e9a4ca1866654bde350335d",
            "isExclusive": True
        },
        {
            "index": 3,
            "title": "体很润 || 圆润、饱满型面体量__汽车外饰设计",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "QifengArt",
            "views": "25.5k",
            "likes": "4",
            "downloads": "72",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/c1d6e288a25f4ee8b43826741289d1b1/54d4917ce42ba9593bdc0410360d9986caa9fe0a872a7cfa0d926297e48840f9.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/8e8f663e30ae4a72add7eea6eb68c758?from=feed&versionUuid=9d51fa52a2a84695891648a3d4e7e96c",
            "isExclusive": True
        },
        {
            "index": 4,
            "title": "F1-白白白-",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "ZERO",
            "views": "22.6k",
            "likes": "5",
            "downloads": "73",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/9759d7f7e3764d9da497885cf1435ffd/fe925519d2a027d51261c224a0ddc5ae21c03da723a7ff6385589b1b0442df48.png?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/904980b603774ffa9807596674f90c7e?from=feed&versionUuid=a4ce78d5e95f4b348b9af85529e93bd2",
            "isExclusive": True
        },
        {
            "index": 5,
            "title": "很硬核 || 野性、硬派型面语言_汽车外饰设计",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "QifengArt",
            "views": "29.1k",
            "likes": "4",
            "downloads": "169",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/c1d6e288a25f4ee8b43826741289d1b1/c460aad4ac694aa3984ea28f18f256baa323acf2af519a2b03f9190da1661ed7.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/da1a300cf08045abb70a4076160db283?from=feed&versionUuid=2576e774739244afa29040efa369dc9f",
            "isExclusive": True
        },
        {
            "index": 6,
            "title": "科幻皮卡",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "Autodesigner",
            "views": "21.1k",
            "likes": "2",
            "downloads": "15",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/50f370e6b15b40319aa572dcb73ee967/54513b0f84481e9380c00a5f15e7e3e239ec73d0036089771fa0941e1979d4cf.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/b717b3d793e84ab8be53e02facbafd2c?from=feed&versionUuid=25ff95fad4a2441db2b6c9595613449b",
            "isExclusive": True
        },
        {
            "index": 7,
            "title": "鲜花列车_开往春天的列车",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "青也",
            "views": "21.7k",
            "likes": "97",
            "downloads": "162",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/48155074a1c04fceb36d81d6339a600e/0bf908dfd0c8601b8af89caa4079fc281d51487be1eb42b6ec4fceb79c67ccc2.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/eb65186576644a449d1f4da68118740a?from=feed&versionUuid=94aff8bb992a49bd8607de3ea7d064f4",
            "isExclusive": True
        },
        {
            "index": 8,
            "title": "概念两轮载具--摩托车",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "ZERO",
            "views": "30.7k",
            "likes": "7",
            "downloads": "72",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/9759d7f7e3764d9da497885cf1435ffd/3d1658e3c50a0ecaaf553ab6b0695d7bd0683cd7bbbc2e865822d6afbc2d54b8.gif?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/15b65cf40e024b178a911c02f58e26eb?from=feed&versionUuid=53c585ef15e442e19f01625f0ecb1577",
            "isExclusive": True
        },
        {
            "index": 9,
            "title": "趣小车 || 极简风/产品感盒子车_汽车外饰设计",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "QifengArt",
            "views": "26.9k",
            "likes": "2",
            "downloads": "154",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/c1d6e288a25f4ee8b43826741289d1b1/500fb7f899534581bf72311cc0ddeb76ab4bbc64d30117b1a60379ed231d4cf1.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/3dad609b114d4b949a0d91447d1a8e99?from=feed&versionUuid=1fb0c1d762624a449a85523a03cddc89",
            "isExclusive": True
        },
        {
            "index": 10,
            "title": "沉浸式光影渲染",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "ONPOINT_DESIGN",
            "views": "33.5k",
            "likes": "0",
            "downloads": "135",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/617e09a4fd254522a6b8c87550327b09/9e1f41f7439efe858eaea21d4897bd4bb97c7fef74aa316a82f9f70a6598cab1.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/46d00e545df04f4391f1d61a46e6cbef?from=feed&versionUuid=8665ccff5aea4c04b7f8fc1e35715ae9",
            "isExclusive": True
        },
        {
            "index": 11,
            "title": "3D衰败世界",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "LILeonor",
            "views": "23.8k",
            "likes": "0",
            "downloads": "49",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/85bcaef3ddf847219dba5f2ef18e9bce/94c10e181efca34107020781c1fd47c29e214bd8805587cf67836b7a0eb974de.GIF?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/2b61fbe3dcc24e6cb52afd028c55746d?from=feed&versionUuid=b552ea50070f47ceb8374ee2246a2011",
            "isExclusive": False
        },
        {
            "index": 12,
            "title": "创意补充模型",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "ONPOINT_DESIGN",
            "views": "25.0k",
            "likes": "6",
            "downloads": "33",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/617e09a4fd254522a6b8c87550327b09/fa3c170e5f9173799c14c5e91896a9e142c007bb90ca477c9c5a58a2746794a0.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/e77eb3bdf5e64fc89812387304b57977?from=feed&versionUuid=0e32624559284ac397eb1818ff85f17a",
            "isExclusive": True
        },
        {
            "index": 13,
            "title": "F.1 CarPaint车漆质感+",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "tub13",
            "views": "45.6k",
            "likes": "2",
            "downloads": "31",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/3d27ff4ccf5a4f29a08417a92079ed0a/cd1429d25b79260b19f74dacfdc3d08469cbfe4303d835f913a9d2bc4e908278.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/ceb9a1d0f4e74eff828a44aeb9f83787?from=feed&versionUuid=0de3642c435a479985d4d6f13f6d5b32",
            "isExclusive": True
        },
        {
            "index": 14,
            "title": "Lexury style-豪华汽车风格",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "老G登",
            "views": "28.2k",
            "likes": "5",
            "downloads": "17",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/3c8f140e991340bd9ee4eb714f262dd4/88c4e6e08a57126a8e29d709e4056f0462443bc712ad10ed463c50fa73fb57f4.gif?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/d6a5c1eb12e34483a6ba41352524177d?from=feed&versionUuid=c13baf53154c4c36976c9330777db756",
            "isExclusive": True
        },
        {
            "index": 15,
            "title": "概念造型，产品风",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "Autodesigner",
            "views": "23.8k",
            "likes": "53",
            "downloads": "27",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/50f370e6b15b40319aa572dcb73ee967/446d0248fbafe65628b1d69e3dcee85c856ea229c2e7d56b8ed375f11db65e29.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/668abaa67319461eb75d310f8c4e9274?from=feed&versionUuid=8a91330f64fe4126a0433cfd2f5a2349",
            "isExclusive": True
        },
        {
            "index": 16,
            "title": "Concept Big SUV",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "老G登",
            "views": "26.2k",
            "likes": "8",
            "downloads": "20",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/3c8f140e991340bd9ee4eb714f262dd4/38d67020c8fb2d55ab0bcf63b90cb226e62cc556a2077154edfdfbf86985a224.gif?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/3ea433930850402292dca4ad08194d5c?from=feed&versionUuid=aa222f5f1ce84f22bd2441353b452ea8",
            "isExclusive": True
        },
        {
            "index": 17,
            "title": "F.1 CarPaint车漆质感",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "tub13",
            "views": "44.8k",
            "likes": "0",
            "downloads": "104",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/3d27ff4ccf5a4f29a08417a92079ed0a/d783d1ad6fc3acb4951a4abc580c28fbc63242691bcb16225124ef83d2fbf347.png?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/46a8b20cd3214b3398a16c8bc5db4d84?from=feed&versionUuid=31a700b9d3e2464abe698ff8117f03e0",
            "isExclusive": True
        },
        {
            "index": 18,
            "title": "玩个灯 || CarLampDesign车灯_汽车外饰设计",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "QifengArt",
            "views": "37.5k",
            "likes": "7",
            "downloads": "50",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/c1d6e288a25f4ee8b43826741289d1b1/05cf40e800672c4123fe1ee13fe87baf415d5a097cbec88efa20aea25612beea.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/542ec655f84744a6bcd544a58edcef62?from=feed&versionUuid=c96ab490803f4ec5bdf974be7b12f8a4",
            "isExclusive": True
        },
        {
            "index": 19,
            "title": "硬朗科幻设计-产品+场景",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "kanggtr",
            "views": "37.7k",
            "likes": "0",
            "downloads": "155",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/fd8a404de0f84805b49f5b5251bc2d17/93d24454bfecbc48abbbd3def7828ffb6e44bbc2cd45de936e71be1e5181e4b9.png?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/f3db904fb7cf44b98a6ed67ee2ecc5e3?from=feed&versionUuid=6355fd77e7564c49b6f33da8938a4b8c",
            "isExclusive": True
        },
        {
            "index": 20,
            "title": "【十一】运营海报_踏青春游、春天户外出行、万物复苏、春日出游",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "十一",
            "views": "34.6k",
            "likes": "150",
            "downloads": "112",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/e130c69fac6848e38177528d6d6fd05e/3a0ecebfb63cd23f8b5c0aa60245cfb667f8afe5f2ecc6c3502a8e8d2f83b79b.gif?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/e0f5c68a3fa54f73a5a31cbc780664c4?from=feed&versionUuid=7b2f79f7f01146a9afe4aca6f4544e5d",
            "isExclusive": True
        },
        {
            "index": 21,
            "title": "法拉利purosague官图风格，细腻优雅氛围",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "BOYA",
            "views": "27.5k",
            "likes": "0",
            "downloads": "8",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/5130661235ce4ddbbea1582bd008cb93/7c5805a488c6dde6d2fcc1842c34062bd4f56622bbe2ba1918b1872470daaf6d.png?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/0005e0fffd804f8893b74e083d095dfc?from=feed&versionUuid=2c742a749cbb4c70a79b6e06971d8833",
            "isExclusive": True
        },
        {
            "index": 22,
            "title": "创意增强-玩具感",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "kiri",
            "views": "28.6k",
            "likes": "2",
            "downloads": "69",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/feb02017fc1341979b26b117e376fce2/473e829502c5b8f3718e65b44d9f1365d2965b97025c46d294ed8ae71de98b91.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/a57a269c7a374ac8ace38e9ea9541121?from=feed&versionUuid=a4e63be1014e47e7b09b68e5de287bae",
            "isExclusive": True
        },
        {
            "index": 23,
            "title": "AiARTiST-CybercarXL-未来载具XL",
            "type": "LORAXL",
            "baseModel": "LORAXL",
            "author": "元影AiGC非人类",
            "views": "26.1k",
            "likes": "2.4k",
            "downloads": "116",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/d6178593b5834f9fa487bca389ce5d83/89c63371c078d9c8d44fb4a6494db09834267532bcecb7f9ba9add7d89ce2e82.png?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/fab32e7bf2124d6a8bca116a78011df5?from=feed&versionUuid=783f3c8bab8e48289d4e34aba89eae36",
            "isExclusive": False
        },
        {
            "index": 24,
            "title": "汽车设计大赛专用概念越野风",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "Autodesigner",
            "views": "28.1k",
            "likes": "5",
            "downloads": "30",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/50f370e6b15b40319aa572dcb73ee967/b7132866b074512c8f927033f019cbc071b2d2d612620b78022e96c7c6f556a7.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/82603b29f30f46ab9715149354b755d7?from=feed&versionUuid=2815dce4eced4d049452de70048f004e",
            "isExclusive": True
        },
        {
            "index": 25,
            "title": "我不是灯神--------",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "ZERO",
            "views": "59.9k",
            "likes": "9",
            "downloads": "28",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/9759d7f7e3764d9da497885cf1435ffd/23b0937c75a7ca4f79d6a7f6fe8b92868d7599c0c390b74cb36b1c643eef2a23.gif?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/97fd1f7e848045768de797edbc4d184a?from=feed&versionUuid=30a92aa6f2c24fb7ad707bede259c512",
            "isExclusive": True
        },
        {
            "index": 26,
            "title": "F.1 豪华风格",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "土禾又",
            "views": "44.2k",
            "likes": "14",
            "downloads": "21",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/d5cf82695d5d4662bc9811a7c83ac50d/ecdb36ca96a0d0482f30b26cda6d91b211cdcca57dae10877928a1eef9e9275b.png?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/3ab3dbea07f745f682003ca9c5d44a7e?from=feed&versionUuid=11056ecc73d646a0a97fbd61dbb3c37a",
            "isExclusive": True
        },
        {
            "index": 27,
            "title": "汽车设计渲染风格-冷酷机械",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "全人类加速器",
            "views": "38.3k",
            "likes": "25",
            "downloads": "37",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/f2d120e063f542238acc1a2ffc4af2e6/147381232cba33e6a21f4ca40922c03e045eaf980537f3b984516b94f46b6ee7.png?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/0224ffcb3dea4b56820af3ba19f27e27?from=feed&versionUuid=61b6f7f9b63c430daecd351a169f0c00",
            "isExclusive": True
        },
        {
            "index": 28,
            "title": "F.1 未来世界_科幻纪元",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "Joe",
            "views": "39.1k",
            "likes": "108",
            "downloads": "127",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/d0d6324fc04ca15e2071e719b7a4fb08/7990af00cfb952a132f0722b6d21b57e1439d31e7a390b5fa1ad8ff3c47d2b8e.gif?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/9a8b6d4fb4b44e7080a1043948d91871?from=feed&versionUuid=949b7e43f7644984826d4c42402ec373",
            "isExclusive": True
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
        print(f"     浏览量: {model['views']}, 点赞: {model['likes']}, 下载: {model['downloads']}")
        
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
