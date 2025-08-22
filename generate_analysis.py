#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成liblib.art汽车交通板块详细数据分析
"""

import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from collections import Counter
import re

def parse_number(value):
    """解析数字字符串，处理k等后缀"""
    if isinstance(value, str):
        if 'k' in value.lower():
            return float(value.lower().replace('k', '')) * 1000
        elif value.isdigit():
            return int(value)
        else:
            return 0
    return value

def main():
    """主函数"""
    # 模型数据
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
            "index": 2,
            "title": "A9L",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "阿扑ANA",
            "views": "5220",
            "likes": "5220",
            "downloads": "5220",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/3dfcfca58add4cf1b0d54959cce60c0f/8709434fe531d5417f4efdcdc9a9f0d9f67cc460869f4d472877caa6d3e0cab4.png?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/ee83a1df80a04a2aa333082b5d1e8742?from=feed&versionUuid=c84eba2fdd7744fab25cff63403a16cc",
            "isExclusive": False
        },
        {
            "index": 3,
            "title": "广汽moca 发散概念车！",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "ray_matttthew",
            "views": "11701",
            "likes": "117",
            "downloads": "1",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/2d8ca75c6cbb4cfcaac4b935da684a26/72e0aaa9f9e1ee2704b18770f69806ae5b7db39b25cde628bc044e47f7f147fb.png?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/3fc09a76e912483b97e43207f1e32fb9?from=feed&versionUuid=a1ada47a11e640bcbd85d5fc23548d22",
            "isExclusive": True
        },
        {
            "index": 4,
            "title": "Ferrari 296 设计迁移",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "lv筱林",
            "views": "7505",
            "likes": "75",
            "downloads": "5",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/b9abfe7f97364cdbb9ade435f1f74666/c0c918475e11077cebaa54de52e6a7f7f566febb449a0133204e2b3176057457.gif?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/b1207cf8880042358fac350c7cc270e0?from=feed&versionUuid=bfb3296d99084775a8fb1a117df625b4",
            "isExclusive": True
        },
        {
            "index": 5,
            "title": "问界 M8 Qwen版",
            "type": "LORAQwen-Image",
            "baseModel": "LORAQwen-Image",
            "author": "小胖子",
            "views": "4604",
            "likes": "4604",
            "downloads": "4604",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/b33bc5b23ec8443f93bb510ad35397a1/7c050b9b4fa6c82bd51293bcfb813615c38c7f018f413bca0e635dd891da68bf.png?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/03b7a06aefc94570abbaea954fb26f63?from=feed&versionUuid=1dd76a1691f14641b6198497f2c00659",
            "isExclusive": False
        },
        {
            "index": 6,
            "title": "高合家族化设计",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "陈土chentu",
            "views": "82012",
            "likes": "82",
            "downloads": "12",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/7d53ea4c12e3452ead348da2ca5b6370/95efb615ba75a9f01cb672e67a1a8dd8e85c4e07c642e62cc08de339b712508a.png?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/20f0c95af89247ce92dacfd0b3f011e3?from=feed&versionUuid=087fedbe6a0b4b6eac956bd969b63ef0",
            "isExclusive": True
        },
        {
            "index": 7,
            "title": "尊得很豪华||极致体态琉光璃彩质感_汽车设计",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "像素农夫DESIGN",
            "views": "210016",
            "likes": "210",
            "downloads": "16",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/605c133411b74a8b8092650ab2a83808/b9e7449fa29724dab87eaadc4b0930dddb4033ed20b62617cbacf83dc805c09b.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/a185ad5a73a6460f85ef51df3e0edbe8?from=feed&versionUuid=aee807dad9ed4a36916039dd6dc8ba1c",
            "isExclusive": True
        },
        {
            "index": 8,
            "title": "趣味小车创意灵感",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "T先生",
            "views": "324012",
            "likes": "324",
            "downloads": "12",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/a45340c6704344578c0f884b55121a00/2c2661a70ac786c3f7bfbccc8859127e1e834e03f458ea4ff35022d707a93e3d.jpeg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/8ae97ad089a74d708f9ad6cf4b9d762b?from=feed&versionUuid=864ac45a83ef427d9937a2a33187342e",
            "isExclusive": True
        },
        {
            "index": 9,
            "title": "小鹏全新THE NEXT P7发布会实拍模型",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "楠楠狗玩AI",
            "views": "26718",
            "likes": "267",
            "downloads": "1",
            "coverUrl": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDE2IDE2IiBmaWxsPSJub25lIj4KICA8cGF0aCBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGNsaXAtcnVsZT0iZXZlbm9kZCIgZD0iTTMuNTI0MjcgMTEuNzUyMlYzLjI0NzY4QzMuNTI0MjcgMi4zMTIyNiA0LjU0Mzk1IDEuNzI1MTEgNS4zNjMyNyAyLjE4OTg2TDEyLjg1NTggNi40Mzg4NkMxMy42ODA1IDYuOTA2NTcgMTMuNjgxMSA4LjA4NTYgMTIuODU2NCA4LjU1MzlMNS4zNjM4NiAxMi44MUM0LjU0NDU0IDEzLjI3NDggMy41MjQyNyAxMi42ODgyIDMuNTI0MjcgMTEuNzUyMloiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4=",
            "modelUrl": "https://www.liblib.art/modelinfo/2c57a5453bea4fceb9e61e6a2573c058?from=feed&versionUuid=4289199e53674a39a8a1847090afd56c",
            "isExclusive": True
        },
        {
            "index": 10,
            "title": "Audi AI-TRAIL",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "TT_Design",
            "views": "6900",
            "likes": "69",
            "downloads": "0",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/dc288ce458b24b06b3fd46b49775b4f3/2c0423281e3ad590e159a71d371b58b3a1d6a72f356228be0e69451e58af3470.png?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/a77d24cede514ddab298d4d1d879022b?from=feed&versionUuid=ae1d37d4fbca42acabf804394b3f1ad5",
            "isExclusive": True
        },
        {
            "index": 11,
            "title": "豪华氛围感 // 豪华内饰",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "T先生",
            "views": "240011",
            "likes": "240",
            "downloads": "11",
            "coverUrl": "https://liblibai-online.liblib.cloud/train/model_images/da5a3575320e49d8aaa9487eb083a305/flux-lora_e000004.png?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/b001cc9725844df2a2c9af9854151b87?from=feed&versionUuid=e4e0f2ffc2a442f28e6116a0051fc968",
            "isExclusive": True
        },
        {
            "index": 12,
            "title": "Kontext_汽车外饰_溶图打光+质感提升_V1",
            "type": "LORAKontext",
            "baseModel": "LORAKontext",
            "author": "玄一",
            "views": "1.6k",
            "likes": "2",
            "downloads": "3",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/ed6e37092a2e4ee9b1a4dfb6c11b37d5/d2ddb7ab89fd43415a5b0690493a97af92eda81f9e42743bc085a845ae0a03d6.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/19065d73e73a4b509c1b35946d96f6b4?from=feed&versionUuid=3e8dafede62a498bb8b3ea2b45cff82a",
            "isExclusive": True
        },
        {
            "index": 13,
            "title": "F.1-雾灯区设计-汽车外饰创意模型",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "及时行hang乐",
            "views": "17508",
            "likes": "175",
            "downloads": "8",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/77a7c2a8870f4c2888adcd4d0cadf8dc/828c1eb7c39ff2b7053d63f80a7d5f67794fa48af280a1d92684b4b26daf6f7f.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/11d0e46ab5f14e66bd4cdc3029ddf6d1?from=feed&versionUuid=0c45da55849b41c6bef2100d13ac6775",
            "isExclusive": True
        },
        {
            "index": 14,
            "title": "Neue BMW造型主体控制",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "TT_Design",
            "views": "7500",
            "likes": "75",
            "downloads": "0",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/dc288ce458b24b06b3fd46b49775b4f3/bc3a62d2bb1214569f241541912a9f2255b757351af1c70451372248eb13954b.png?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/aefde91ff1774ed69e80978d0671a208?from=feed&versionUuid=92ca3bbd468b4fa9b901cf61235cec73",
            "isExclusive": True
        },
        {
            "index": 15,
            "title": "F.1 柔和光影｜优雅运动｜大型纯电跨界轿跑SUV汽车模型",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "星火宇宙",
            "views": "7609",
            "likes": "76",
            "downloads": "9",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/afa99823831a4c2cb6f7d18323776c6e/8d673217022b352826afc57965782fe7dd4865cc26c86ebfbb3fd244fbff7db8.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/f26acbba7993482ea24379ffd19b699f?from=feed&versionUuid=6ce96a6296ff4ebea8250b98836cdf26",
            "isExclusive": True
        },
        {
            "index": 16,
            "title": "2025 款500Hi4-Z FLUX.1",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "团子",
            "views": "13500",
            "likes": "135",
            "downloads": "0",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/21ee27b9d5ad4a17beb5aafe2d393e2c/60e3a57c678345edb691fe04ec1d60dabb703b2a9d28855ec8d5c712567c18c3.png?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/593d8f29bd0e4b78a4f57f6bf9131008?from=feed&versionUuid=7bdab135d4f649aabf899215fe9f28ca",
            "isExclusive": True
        },
        {
            "index": 17,
            "title": "润色||洒脱光影画风与汽车体态强化",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "像素农夫DESIGN",
            "views": "78034",
            "likes": "78",
            "downloads": "34",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/605c133411b74a8b8092650ab2a83808/fee02914b7ee29ced3457d93837eb7a2b67ecdd3c7caaddfbee831a78756e209.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/bacb94a7533a4aa2913a2b6fc9aece56?from=feed&versionUuid=824aab4b594946deb02b36782538b2ea",
            "isExclusive": True
        },
        {
            "index": 18,
            "title": "现代N-vision 74主体控制模型",
            "type": "LORAF.1",
            "baseModel": "LORAF.1",
            "author": "K_Mind_Form",
            "views": "24200",
            "likes": "242",
            "downloads": "0",
            "coverUrl": "https://liblibai-online.liblib.cloud/img/ee84c07ba8774cfe8f712f5f40b389c8/5f0b262d39f8fac9ad0250208493a3b87e9b328b71f847414226367f6e96b1e5.jpg?image_process=format,webp&x-oss-process=image/resize,w_600,m_lfit/format,webp",
            "modelUrl": "https://www.liblib.art/modelinfo/764ef63d4a7445f6aa53b7d09be4fe92?from=feed&versionUuid=8267c025ec7a47e2b01998778a3983ef",
            "isExclusive": True
        }
    ]
    
    # 转换为DataFrame
    df = pd.DataFrame(models)
    
    # 解析数字
    df['views_num'] = df['views'].apply(parse_number)
    df['likes_num'] = df['likes'].apply(parse_number)
    df['downloads_num'] = df['downloads'].apply(parse_number)
    
    print("=== Liblib.art 汽车交通板块模型详细分析 ===\n")
    
    # 基础统计
    print("1. 基础统计信息")
    print(f"   总模型数量: {len(models)}")
    print(f"   独家模型: {df['isExclusive'].sum()} ({df['isExclusive'].sum()/len(models)*100:.1f}%)")
    print(f"   普通模型: {(~df['isExclusive']).sum()} ({(~df['isExclusive']).sum()/len(models)*100:.1f}%)")
    
    # 模型类型统计
    print(f"\n2. 模型类型分布")
    type_counts = df['type'].value_counts()
    for model_type, count in type_counts.items():
        print(f"   {model_type}: {count}个 ({count/len(models)*100:.1f}%)")
    
    # 作者统计
    print(f"\n3. 作者活跃度分析")
    author_counts = df['author'].value_counts()
    print("   作者模型数量排名:")
    for i, (author, count) in enumerate(author_counts.head(5).items(), 1):
        print(f"   {i}. {author}: {count}个模型")
    
    # 数据统计
    print(f"\n4. 数据统计")
    print(f"   总浏览量: {df['views_num'].sum():,}")
    print(f"   总点赞数: {df['likes_num'].sum():,}")
    print(f"   总下载量: {df['downloads_num'].sum():,}")
    print(f"   平均浏览量: {df['views_num'].mean():,.0f}")
    print(f"   平均点赞数: {df['likes_num'].mean():,.0f}")
    print(f"   平均下载量: {df['downloads_num'].mean():,.0f}")
    
    # 排行榜
    print(f"\n5. 浏览量排行榜 (前10名)")
    top_views = df.nlargest(10, 'views_num')[['title', 'author', 'views_num']]
    for i, row in top_views.iterrows():
        print(f"   {row.name+1:2d}. {row['title'][:30]:<30} - {row['author']:<15} ({row['views_num']:,})")
    
    print(f"\n6. 下载量排行榜 (前10名)")
    top_downloads = df.nlargest(10, 'downloads_num')[['title', 'author', 'downloads_num']]
    for i, row in top_downloads.iterrows():
        print(f"   {row.name+1:2d}. {row['title'][:30]:<30} - {row['author']:<15} ({row['downloads_num']:,})")
    
    # 相关性分析
    print(f"\n7. 数据相关性分析")
    correlation = df[['views_num', 'likes_num', 'downloads_num']].corr()
    print("   浏览量-点赞数相关性: {:.3f}".format(correlation.loc['views_num', 'likes_num']))
    print("   浏览量-下载量相关性: {:.3f}".format(correlation.loc['views_num', 'downloads_num']))
    print("   点赞数-下载量相关性: {:.3f}".format(correlation.loc['likes_num', 'downloads_num']))
    
    # 模型质量评估
    print(f"\n8. 模型质量评估")
    df['engagement_rate'] = (df['likes_num'] + df['downloads_num']) / df['views_num'] * 100
    df['engagement_rate'] = df['engagement_rate'].fillna(0)
    
    top_engagement = df.nlargest(5, 'engagement_rate')[['title', 'author', 'engagement_rate']]
    print("   用户参与度最高的模型 (前5名):")
    for i, row in top_engagement.iterrows():
        print(f"   {i+1}. {row['title'][:30]:<30} - {row['author']:<15} ({row['engagement_rate']:.2f}%)")
    
    # 保存详细数据
    output_data = {
        'summary': {
            'total_models': len(models),
            'exclusive_models': int(df['isExclusive'].sum()),
            'regular_models': int((~df['isExclusive']).sum()),
            'total_views': int(df['views_num'].sum()),
            'total_likes': int(df['likes_num'].sum()),
            'total_downloads': int(df['downloads_num'].sum()),
            'avg_views': float(df['views_num'].mean()),
            'avg_likes': float(df['likes_num'].mean()),
            'avg_downloads': float(df['downloads_num'].mean())
        },
        'models': models,
        'rankings': {
            'top_views': top_views.to_dict('records'),
            'top_downloads': top_downloads.to_dict('records'),
            'top_engagement': top_engagement.to_dict('records')
        },
        'statistics': {
            'type_distribution': type_counts.to_dict(),
            'author_distribution': author_counts.to_dict(),
            'correlations': correlation.to_dict()
        }
    }
    
    with open('liblib_car_models_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n9. 数据导出")
    print("   详细分析数据已保存到: liblib_car_models_analysis.json")
    
    # 生成图表数据
    print(f"\n10. 图表数据准备")
    print("    可以基于以下数据生成可视化图表:")
    print("    - 模型类型分布饼图")
    print("    - 浏览量柱状图")
    print("    - 作者活跃度条形图")
    print("    - 数据相关性热力图")

if __name__ == "__main__":
    main()
