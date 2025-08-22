#!/usr/bin/env python3
"""
监控系统演示脚本

展示结构化日志、阶段性统计、阈值告警等功能的完整使用方法
"""

import time
import random
from pathlib import Path

from monitoring import (
    get_global_monitoring,
    create_monitoring_system,
    MonitoringContext,
    get_logger,
    global_metrics,
    global_alert_manager
)
from monitoring.alerts import AlertRule, AlertLevel, FileAlertChannel


def demo_basic_logging():
    """演示基础日志功能"""
    print("\n=== 演示基础日志功能 ===")
    
    # 获取日志记录器
    logger = get_logger("demo_basic")
    
    # 记录不同级别的日志
    logger.debug("这是一条调试日志")
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    
    # 记录带额外字段的日志
    logger.info("用户登录成功", extra_fields={
        'user_id': 12345,
        'ip_address': '192.168.1.100',
        'login_time': '2024-01-01T10:00:00'
    })
    
    # 记录带系统信息的日志
    logger.info("系统状态检查", include_system_info=True)


def demo_metrics_collection():
    """演示指标收集功能"""
    print("\n=== 演示指标收集功能 ===")
    
    # 开始指标收集会话
    global_metrics.start_session()
    
    # 模拟一些请求
    for i in range(10):
        success = random.choice([True, True, True, False])  # 75%成功率
        duration = random.uniform(0.1, 2.0)
        items_count = random.randint(1, 5) if success else 0
        
        if not success:
            error = Exception(f"模拟错误 {i}")
        else:
            error = None
        
        global_metrics.record_request(success, duration, items_count, error)
        
        # 记录处理时间
        processing_time = random.uniform(0.05, 0.5)
        global_metrics.record_processing_time(processing_time)
        
        time.sleep(0.1)
    
    # 记录阶段统计
    global_metrics.start_stage("数据采集")
    time.sleep(0.5)
    global_metrics.end_stage("数据采集", success_count=8, error_count=2, total_items=25)
    
    global_metrics.start_stage("数据处理")
    time.sleep(0.3)
    global_metrics.end_stage("数据处理", success_count=9, error_count=1, total_items=20)
    
    # 记录系统指标
    global_metrics.record_system_metrics(
        cpu_percent=random.uniform(20, 80),
        memory_percent=random.uniform(40, 90),
        disk_usage=random.uniform(30, 70)
    )
    
    # 结束会话
    global_metrics.end_session()
    
    # 显示统计信息
    print("指标收集完成！")
    print("汇总统计:")
    summary = global_metrics.get_summary_stats()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\n阶段统计:")
    stage_stats = global_metrics.get_stage_stats()
    for stage, stats in stage_stats.items():
        print(f"  {stage}: 成功率 {stats['success_rate_percent']}%, 耗时 {stats['duration']:.2f}秒")


def demo_alert_system():
    """演示告警系统功能"""
    print("\n=== 演示告警系统功能 ===")
    
    # 添加文件告警通道
    alerts_file = Path("data/monitoring/demo_alerts.log")
    file_channel = FileAlertChannel(alerts_file)
    global_alert_manager.add_channel(file_channel)
    
    # 添加自定义告警规则
    custom_rule = AlertRule(
        name="演示告警规则",
        metric_name="demo_metric",
        threshold=5.0,
        operator=">",
        level=AlertLevel.WARNING,
        description="演示用的告警规则"
    )
    global_alert_manager.add_rule(custom_rule)
    
    # 模拟触发告警
    print("模拟触发告警...")
    test_metrics = {
        'demo_metric': 7.5,  # 超过阈值5.0
        'cpu_percent': 85.0,  # 超过默认阈值80.0
        'success_rate_percent': 75.0  # 低于默认阈值90.0
    }
    
    global_alert_manager.check_metrics(test_metrics)
    
    # 显示告警历史
    print("\n告警历史:")
    alert_history = global_alert_manager.get_alert_history()
    for alert in alert_history:
        print(f"  [{alert['level'].upper()}] {alert['message']}")
    
    # 显示告警汇总
    print("\n告警汇总:")
    alert_summary = global_alert_manager.get_alert_summary()
    for key, value in alert_summary.items():
        print(f"  {key}: {value}")


def demo_monitoring_system():
    """演示完整监控系统功能"""
    print("\n=== 演示完整监控系统功能 ===")
    
    # 创建监控系统
    config = {
        'log_file': 'logs/demo_monitoring.log',
        'enable_system_monitoring': True,
        'system_monitoring_interval': 5  # 5秒检查一次
    }
    
    monitoring = create_monitoring_system("demo_system", config)
    
    # 使用上下文管理器自动启动和停止监控
    with MonitoringContext(monitoring) as mon:
        print("监控系统已启动，开始模拟爬虫任务...")
        
        # 模拟爬虫任务
        mon.log_scraping_event("start", stage_name="列表采集", target="汽车交通", total_pages=100)
        
        for page in range(1, 11):  # 模拟10页
            # 模拟请求
            success = random.choice([True, True, True, False])
            duration = random.uniform(0.5, 3.0)
            items_count = random.randint(5, 15) if success else 0
            
            mon.record_request(success, duration, items_count)
            
            # 记录进度
            if page % 3 == 0:
                success_count = sum(1 for _ in range(page) if random.choice([True, True, True, False]))
                error_count = page - success_count
                mon.log_scraping_event("progress", 
                                     current_page=page, 
                                     total_pages=100,
                                     success_count=success_count,
                                     error_count=error_count)
            
            # 模拟限速
            if random.random() < 0.1:  # 10%概率触发限速
                retry_after = random.randint(5, 15)
                mon.record_rate_limit(f"/api/page/{page}", retry_after)
                time.sleep(1)
            
            # 定期系统检查
            mon.periodic_system_check()
            
            time.sleep(0.2)
        
        # 完成爬虫任务
        mon.log_scraping_event("complete", 
                              stage_name="列表采集",
                              target="汽车交通",
                              total_pages=100,
                              success_count=85,
                              error_count=15,
                              total_items=1200,
                              duration=25.5)
        
        print("爬虫任务完成！")
        
        # 显示监控汇总
        summary = mon.get_monitoring_summary()
        print(f"\n监控汇总:")
        print(f"  系统名称: {summary['system_name']}")
        print(f"  监控状态: {'运行中' if summary['is_monitoring'] else '已停止'}")
        print(f"  总请求数: {summary['metrics_summary'].get('total_requests', 0)}")
        print(f"  成功率: {summary['metrics_summary'].get('success_rate_percent', 0)}%")
        print(f"  总告警数: {summary['alert_summary'].get('total_alerts', 0)}")
    
    print("监控系统已停止")


def demo_data_export():
    """演示数据导出功能"""
    print("\n=== 演示数据导出功能 ===")
    
    # 获取全局监控系统
    monitoring = get_global_monitoring()
    
    # 导出所有监控数据
    export_dir = Path("data/monitoring/exports")
    exported_files = monitoring.export_all_data(export_dir)
    
    print("数据导出完成！")
    print("导出的文件:")
    for file_type, file_path in exported_files.items():
        print(f"  {file_type}: {file_path}")
    
    # 生成文本报告
    report_content = global_metrics.generate_report()
    print(f"\n生成的报告预览（前10行）:")
    report_lines = report_content.split('\n')[:10]
    for line in report_lines:
        print(f"  {line}")


def main():
    """主函数"""
    print("Liblib 交通数据采集监控系统演示")
    print("=" * 50)
    
    # 创建必要的目录
    Path("logs").mkdir(exist_ok=True)
    Path("data/monitoring").mkdir(parents=True, exist_ok=True)
    
    try:
        # 演示各个功能模块
        demo_basic_logging()
        demo_metrics_collection()
        demo_alert_system()
        demo_monitoring_system()
        demo_data_export()
        
        print("\n" + "=" * 50)
        print("所有演示完成！")
        print("请检查以下目录查看生成的文件:")
        print("  - logs/: 日志文件")
        print("  - data/monitoring/: 监控数据和报告")
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
