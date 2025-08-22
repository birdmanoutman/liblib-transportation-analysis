# Liblib 汽车交通模型分析器使用指南

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装Python依赖
pip install requests pandas numpy

# 可选：安装Playwright（用于浏览器自动化）
pip install playwright
playwright install
```

### 2. 基本使用

```bash
# 运行完整分析流程
python liblib_car_analyzer.py --all

# 指定输出目录
python liblib_car_analyzer.py --all --output my_analysis

# 使用配置文件
python liblib_car_analyzer.py --all --config config.json
```

## 📋 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--all` | 执行完整流程（推荐） | `--all` |
| `--collect` | 仅执行数据采集 | `--collect` |
| `--download` | 仅执行图片下载 | `--download` |
| `--analyze` | 仅执行数据分析 | `--analyze` |
| `--report` | 仅生成分析报告 | `--report` |
| `--config` | 指定配置文件 | `--config config.json` |
| `--output` | 指定输出目录 | `--output my_output` |
| `--help` | 显示帮助信息 | `--help` |

## ⚙️ 配置说明

### 基础配置

```json
{
  "api_base": "https://api2.liblib.art",
  "base_url": "https://www.liblib.art",
  "output_dir": "liblib_analysis_output",
  "max_workers": 4,
  "timeout": 30,
  "retry_times": 3
}
```

### 高级配置

```json
{
  "page_size": 48,
  "max_pages": 10,
  "car_keywords": ["汽车", "跑车", "SUV"],
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s"
  }
}
```

## 🔧 功能特性

### 1. 智能数据采集
- **API采集**: 通过官方API获取模型数据
- **浏览器自动化**: 使用Playwright进行页面滚动和数据提取
- **关键词搜索**: 通过汽车相关关键词搜索模型
- **去重处理**: 自动识别和去除重复模型

### 2. 批量图片下载
- **多格式支持**: JPG, PNG, GIF, WebP
- **并发下载**: 多线程并发下载，提高效率
- **错误重试**: 自动重试失败的下载
- **文件管理**: 智能文件名生成和目录组织

### 3. 深度数据分析
- **基础统计**: 模型数量、浏览量、点赞数、下载量
- **作者分析**: 作者活跃度排行榜
- **类型分析**: 模型类型分布统计
- **参与度分析**: 用户参与度计算

### 4. 专业报告生成
- **Markdown格式**: 结构化的分析报告
- **数据可视化**: 清晰的统计表格
- **时间戳记录**: 自动记录分析时间
- **多语言支持**: 支持中文内容

## 📁 输出结构

```
liblib_analysis_output/
├── images/                    # 下载的模型图片
├── data/                      # 原始数据和分析结果
│   ├── models_data_*.json    # 模型数据
│   └── analysis_results_*.json # 分析结果
├── reports/                   # 分析报告
│   └── liblib_car_analysis_*.md
└── logs/                      # 运行日志
    └── liblib_analyzer_*.log
```

## 🚨 常见问题和解决方案

### 1. 网络连接问题

**问题**: 请求超时或连接失败
**解决方案**:
```bash
# 增加超时时间
python liblib_car_analyzer.py --all --config config.json

# 在config.json中调整
{
  "timeout": 60,
  "retry_times": 5,
  "retry_delay": 3
}
```

### 2. 图片下载失败

**问题**: 部分图片下载失败
**解决方案**:
```bash
# 检查网络连接
ping liblibai-online.liblib.cloud

# 调整并发数
{
  "max_workers": 2,
  "timeout": 45
}
```

### 3. 内存不足

**问题**: 处理大量数据时内存不足
**解决方案**:
```bash
# 减少页面大小和最大页数
{
  "page_size": 24,
  "max_pages": 5
}
```

### 4. Playwright安装问题

**问题**: 浏览器自动化功能不可用
**解决方案**:
```bash
# 重新安装Playwright
pip uninstall playwright
pip install playwright
playwright install

# 或者跳过浏览器采集，仅使用API
# 修改代码中的collect_data_browser调用
```

## 📊 性能优化建议

### 1. 网络优化
- 使用稳定的网络连接
- 适当调整超时和重试参数
- 考虑使用代理服务器

### 2. 并发优化
- 根据网络带宽调整`max_workers`
- 避免设置过高的并发数
- 监控系统资源使用情况

### 3. 存储优化
- 定期清理旧的输出文件
- 使用SSD存储提高I/O性能
- 考虑压缩存储图片文件

## 🔍 调试和监控

### 1. 日志查看
```bash
# 查看最新日志
tail -f liblib_analysis_output/logs/liblib_analyzer_*.log

# 搜索错误信息
grep "ERROR" liblib_analysis_output/logs/*.log
```

### 2. 进度监控
脚本运行时会显示详细的进度信息：
```
=== 第一阶段: 数据采集 ===
开始API数据采集...
第1页采集到48个模型
第2页采集到48个模型
API采集完成，共获取96个模型

=== 第二阶段: 图片下载 ===
开始批量图片下载...
下载进度: 5/96
下载进度: 10/96
...
```

### 3. 性能监控
```bash
# 监控系统资源
htop
iotop

# 监控网络连接
netstat -an | grep :443
```

## 🧪 测试验证

### 1. 运行测试套件
```bash
python test_liblib_analyzer.py
```

### 2. 功能测试
```bash
# 测试数据采集
python liblib_car_analyzer.py --collect

# 测试图片下载
python liblib_car_analyzer.py --download

# 测试数据分析
python liblib_car_analyzer.py --analyze
```

### 3. 性能测试
```bash
# 测试大数据量处理
# 修改config.json中的参数进行压力测试
{
  "page_size": 100,
  "max_pages": 20,
  "max_workers": 8
}
```

## 📈 扩展和定制

### 1. 添加新的分析维度
```python
# 在analyze_data方法中添加新的统计
def analyze_data(self, models):
    # ... 现有代码 ...
    
    # 添加新的分析维度
    new_analysis = self._custom_analysis(models)
    analysis_results['custom'] = new_analysis
    
    return analysis_results

def _custom_analysis(self, models):
    # 实现自定义分析逻辑
    pass
```

### 2. 自定义报告格式
```python
# 修改_generate_markdown_report方法
def _generate_markdown_report(self, analysis_results):
    # 添加自定义报告内容
    report = super()._generate_markdown_report(analysis_results)
    report += "\n## 自定义分析\n"
    # ... 自定义内容 ...
    return report
```

### 3. 集成其他数据源
```python
# 添加新的数据采集方法
async def collect_data_from_custom_source(self):
    # 实现自定义数据源采集
    pass
```

## 🤝 贡献和反馈

### 1. 报告问题
- 使用详细的错误描述
- 提供系统环境信息
- 附上相关的日志文件

### 2. 功能建议
- 描述具体的使用场景
- 提供实现思路
- 考虑向后兼容性

### 3. 代码贡献
- 遵循现有的代码风格
- 添加适当的测试用例
- 更新相关文档

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至项目维护者
- 参与项目讨论

---

**最后更新**: 2024年12月  
**版本**: 1.0.0  
**维护者**: Liblib分析项目团队
