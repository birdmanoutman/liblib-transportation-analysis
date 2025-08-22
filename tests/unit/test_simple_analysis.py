#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化测试脚本
验证分析功能是否正常工作
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime

def test_simple_analysis():
    """测试简单分析功能"""
    print("🧪 开始测试简单分析功能...")
    
    # 创建测试数据
    test_data = [
        {"title": "测试模型1", "views": 100, "likes": 10, "category": "测试类别"},
        {"title": "测试模型2", "views": 200, "likes": 20, "category": "测试类别"},
        {"title": "测试模型3", "views": 150, "likes": 15, "category": "其他类别"}
    ]
    
    # 转换为DataFrame
    df = pd.DataFrame(test_data)
    
    # 简单分析
    total_models = len(df)
    total_views = df['views'].sum()
    total_likes = df['likes'].sum()
    avg_views = df['views'].mean()
    
    print(f"✅ 数据分析完成:")
    print(f"   - 模型总数: {total_models}")
    print(f"   - 总浏览量: {total_views}")
    print(f"   - 总点赞数: {total_likes}")
    print(f"   - 平均浏览量: {avg_views:.1f}")
    
    # 创建输出目录
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存数据
    csv_path = os.path.join(output_dir, "test_data.csv")
    df.to_csv(csv_path, index=False, encoding='utf-8')
    
    json_path = os.path.join(output_dir, "test_analysis.json")
    analysis_results = {
        "total_models": total_models,
        "total_views": total_views,
        "total_likes": total_likes,
        "avg_views": avg_views,
        "timestamp": datetime.now().isoformat()
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        # 转换numpy类型为Python原生类型
        analysis_results_converted = {
            "total_models": int(total_models),
            "total_views": int(total_views),
            "total_likes": int(total_likes),
            "avg_views": float(avg_views),
            "timestamp": datetime.now().isoformat()
        }
        json.dump(analysis_results_converted, f, ensure_ascii=False, indent=2)
    
    # 生成简单报告
    report_path = os.path.join(output_dir, "test_report.md")
    report_content = f"""# 测试分析报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 分析结果

- **模型总数**: {total_models}
- **总浏览量**: {total_views}
- **总点赞数**: {total_likes}
- **平均浏览量**: {avg_views:.1f}

## 数据概览

```csv
{df.to_csv(index=False)}
```

---
*这是一个测试报告*
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"📁 输出文件:")
    print(f"   - CSV数据: {csv_path}")
    print(f"   - JSON分析: {json_path}")
    print(f"   - Markdown报告: {report_path}")
    
    return True

def test_file_operations():
    """测试文件操作功能"""
    print("\n📁 测试文件操作功能...")
    
    try:
        # 测试目录创建
        test_dir = "test_file_ops"
        os.makedirs(test_dir, exist_ok=True)
        
        # 测试文件写入
        test_file = os.path.join(test_dir, "test.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("测试文件内容\n")
            f.write("包含中文测试\n")
        
        # 测试文件读取
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ 文件操作测试成功:")
        print(f"   - 目录创建: {test_dir}")
        print(f"   - 文件写入: {test_file}")
        print(f"   - 文件读取: {len(content)} 字符")
        
        # 清理测试文件
        os.remove(test_file)
        os.rmdir(test_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ 文件操作测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始运行简化测试...")
    
    try:
        # 测试1: 简单分析
        if not test_simple_analysis():
            print("❌ 简单分析测试失败")
            return False
        
        # 测试2: 文件操作
        if not test_file_operations():
            print("❌ 文件操作测试失败")
            return False
        
        print("\n🎉 所有测试通过！")
        print("📁 查看输出文件: test_output/")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
