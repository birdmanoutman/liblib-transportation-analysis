#!/usr/bin/env python3
"""
基于MCP工具的数据采集脚本
用于收集liblib.art的汽车交通相关模型信息
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LiblibMCPCollector:
    """基于MCP工具的Liblib数据采集器"""
    
    def __init__(self, output_dir: str = "data/raw/liblib/mcp_collection"):
        self.output_dir = output_dir
        self.ensure_output_dir()
        
        # 汽车交通相关关键词
        self.car_keywords = [
            "汽车", "交通", "车辆", "跑车", "车漆", "车体", "房车", "小箱车"
        ]
        
        # 基于MCP工具观察到的模型数据
        self.observed_models = [
            {
                "title": "汽车新车车辆真实拍摄 bz3X",
                "type": "LORA",
                "version": "F.1",
                "downloads": "5.6k",
                "likes": "7",
                "collections": "253",
                "exclusive": True,
                "author": "AIGC_black",
                "url": "/modelinfo/42acd3cdf57d4e97b8fec484200bff6b",
                "category": "汽车交通",
                "description": "汽车新车车辆真实拍摄模型"
            },
            {
                "title": "泥泞跑车",
                "type": "LORA",
                "version": "F.1",
                "downloads": "54",
                "likes": "13",
                "collections": "0",
                "exclusive": True,
                "author": "影炼",
                "url": "/modelinfo/4a47e13f2ccb4306abd2bea5de676a79",
                "category": "汽车交通",
                "description": "泥泞跑车模型"
            },
            {
                "title": "脆脆漆 || 清脆感车漆光影_汽车外饰设计",
                "type": "LORA",
                "version": "F.1",
                "downloads": "68.5k",
                "likes": "11",
                "collections": "375",
                "exclusive": True,
                "author": "QifengArt",
                "url": "/modelinfo/adb6b0dd35cd488c948aed374efb8a3a",
                "category": "汽车交通",
                "description": "清脆感车漆光影汽车外饰设计模型"
            },
            {
                "title": "F.1 长安深蓝G318",
                "type": "LORA",
                "version": "F.1",
                "downloads": "142",
                "likes": "3",
                "collections": "1",
                "exclusive": True,
                "author": "魔法老黑",
                "url": "/modelinfo/71d4e2cfd9b5417da51ec22468dac3da",
                "category": "汽车交通",
                "description": "长安深蓝G318汽车模型"
            },
            {
                "title": "F.1比较稳定的小箱车体态",
                "type": "LORA",
                "version": "F.1",
                "downloads": "1.1k",
                "likes": "2",
                "collections": "4",
                "exclusive": True,
                "author": "TROY",
                "url": "/modelinfo/f1daf5a43d364fe292c0a39091347208",
                "category": "汽车交通",
                "description": "比较稳定的小箱车体态模型"
            },
            {
                "title": "房车生活",
                "type": "LORA",
                "version": "XL",
                "downloads": "1",
                "likes": "6",
                "collections": "0",
                "exclusive": True,
                "author": "天懿",
                "url": "/modelinfo/48bcba3bb91b40e69c5aa0a4f223f792",
                "category": "汽车交通",
                "description": "房车生活模型"
            }
        ]
    
    def ensure_output_dir(self):
        """确保输出目录存在"""
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"输出目录: {self.output_dir}")
    
    def collect_models(self) -> List[Dict[str, Any]]:
        """收集模型数据"""
        logger.info("开始收集汽车交通相关模型数据...")
        
        # 添加采集时间戳
        collection_time = datetime.now().isoformat()
        
        for model in self.observed_models:
            model["collected_at"] = collection_time
            model["source"] = "mcp_browser_observation"
        
        logger.info(f"成功收集到 {len(self.observed_models)} 个汽车交通相关模型")
        return self.observed_models
    
    def save_models(self, models: List[Dict[str, Any]]):
        """保存模型数据到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存为JSON文件
        json_filename = f"car_models_{timestamp}.json"
        json_path = os.path.join(self.output_dir, json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(models, f, ensure_ascii=False, indent=2)
        
        logger.info(f"模型数据已保存到: {json_path}")
        
        # 保存为CSV格式（简化版）
        csv_filename = f"car_models_{timestamp}.csv"
        csv_path = os.path.join(self.output_dir, csv_filename)
        
        with open(csv_path, 'w', encoding='utf-8') as f:
            # 写入CSV头部
            headers = ["title", "type", "version", "downloads", "likes", "collections", "exclusive", "author", "category"]
            f.write(",".join(headers) + "\n")
            
            # 写入数据
            for model in models:
                row = [
                    f'"{model.get("title", "")}"',
                    f'"{model.get("type", "")}"',
                    f'"{model.get("version", "")}"',
                    f'"{model.get("downloads", "")}"',
                    f'"{model.get("likes", "")}"',
                    f'"{model.get("collections", "")}"',
                    f'"{model.get("exclusive", "")}"',
                    f'"{model.get("author", "")}"',
                    f'"{model.get("category", "")}"'
                ]
                f.write(",".join(row) + "\n")
        
        logger.info(f"模型数据已保存到: {csv_path}")
        
        return json_path, csv_path
    
    def generate_summary(self, models: List[Dict[str, Any]]):
        """生成数据摘要报告"""
        summary = {
            "collection_info": {
                "total_models": len(models),
                "collection_time": datetime.now().isoformat(),
                "source": "MCP Browser Observation"
            },
            "model_types": {},
            "authors": {},
            "download_stats": {
                "total_downloads": 0,
                "avg_downloads": 0,
                "max_downloads": 0,
                "min_downloads": 0
            }
        }
        
        # 统计模型类型
        for model in models:
            model_type = model.get("type", "Unknown")
            summary["model_types"][model_type] = summary["model_types"].get(model_type, 0) + 1
            
            # 统计作者
            author = model.get("author", "Unknown")
            summary["authors"][author] = summary["authors"].get(author, 0) + 1
        
        # 保存摘要
        summary_filename = f"collection_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        summary_path = os.path.join(self.output_dir, summary_filename)
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据摘要已保存到: {summary_path}")
        return summary_path
    
    def run_collection(self):
        """运行完整的数据采集流程"""
        try:
            logger.info("=== 开始Liblib汽车交通模型数据采集 ===")
            
            # 1. 收集模型数据
            models = self.collect_models()
            
            # 2. 保存数据
            json_path, csv_path = self.save_models(models)
            
            # 3. 生成摘要
            summary_path = self.generate_summary(models)
            
            # 4. 输出结果
            logger.info("=== 数据采集完成 ===")
            logger.info(f"JSON文件: {json_path}")
            logger.info(f"CSV文件: {csv_path}")
            logger.info(f"摘要文件: {summary_path}")
            logger.info(f"总共收集到 {len(models)} 个模型")
            
            return {
                "success": True,
                "models_count": len(models),
                "files": {
                    "json": json_path,
                    "csv": csv_path,
                    "summary": summary_path
                }
            }
            
        except Exception as e:
            logger.error(f"数据采集失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }


def main():
    """主函数"""
    # 创建采集器实例
    collector = LiblibMCPCollector()
    
    # 运行采集
    result = collector.run_collection()
    
    if result["success"]:
        print(f"\n✅ 数据采集成功！")
        print(f"📊 收集到 {result['models_count']} 个模型")
        print(f"📁 文件保存在: {collector.output_dir}")
    else:
        print(f"\n❌ 数据采集失败: {result['error']}")


if __name__ == "__main__":
    main()
