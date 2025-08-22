#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T7 中间件配置文件
提供可配置化的限速、重试、熔断和代理参数
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

class MiddlewareConfig:
    """中间件配置类"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or str(PROJECT_ROOT / "config" / "middleware.json")
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        # 尝试从文件加载
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {e}，使用默认配置")
        
        # 返回默认配置
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'rate_limit': {
                'max_requests_per_second': float(os.getenv('MIDDLEWARE_RPS', '4.0')),
                'max_concurrent': int(os.getenv('MIDDLEWARE_MAX_CONCURRENT', '5')),
                'burst_size': int(os.getenv('MIDDLEWARE_BURST_SIZE', '10')),
                'time_window': float(os.getenv('MIDDLEWARE_TIME_WINDOW', '1.0'))
            },
            'retry': {
                'max_retries': int(os.getenv('MIDDLEWARE_MAX_RETRIES', '3')),
                'base_delay': float(os.getenv('MIDDLEWARE_BASE_DELAY', '1.0')),
                'max_delay': float(os.getenv('MIDDLEWARE_MAX_DELAY', '60.0')),
                'backoff_factor': float(os.getenv('MIDDLEWARE_BACKOFF_FACTOR', '2.0')),
                'jitter': os.getenv('MIDDLEWARE_JITTER', 'true').lower() == 'true',
                'retry_on_status_codes': [429, 500, 502, 503, 504]
            },
            'circuit_breaker': {
                'failure_threshold': int(os.getenv('MIDDLEWARE_FAILURE_THRESHOLD', '5')),
                'recovery_timeout': float(os.getenv('MIDDLEWARE_RECOVERY_TIMEOUT', '60.0')),
                'success_threshold': int(os.getenv('MIDDLEWARE_SUCCESS_THRESHOLD', '2'))
            },
            'proxy': {
                'enabled': os.getenv('MIDDLEWARE_PROXY_ENABLED', 'false').lower() == 'true',
                'proxies': self._parse_proxy_list(os.getenv('MIDDLEWARE_PROXIES', '')),
                'rotation_strategy': os.getenv('MIDDLEWARE_PROXY_STRATEGY', 'round_robin'),
                'health_check_interval': float(os.getenv('MIDDLEWARE_PROXY_HEALTH_CHECK', '300.0'))
            },
            'user_agents': {
                'enabled': os.getenv('MIDDLEWARE_UA_ROTATION', 'true').lower() == 'true',
                'custom_agents': self._parse_ua_list(os.getenv('MIDDLEWARE_CUSTOM_UAS', ''))
            },
            'logging': {
                'level': os.getenv('MIDDLEWARE_LOG_LEVEL', 'INFO'),
                'file': os.getenv('MIDDLEWARE_LOG_FILE', 'logs/middleware.log'),
                'format': os.getenv('MIDDLEWARE_LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            },
            'monitoring': {
                'enabled': os.getenv('MIDDLEWARE_MONITORING', 'true').lower() == 'true',
                'stats_interval': float(os.getenv('MIDDLEWARE_STATS_INTERVAL', '60.0')),
                'alert_threshold': float(os.getenv('MIDDLEWARE_ALERT_THRESHOLD', '0.8'))
            }
        }
    
    def _parse_proxy_list(self, proxy_string: str) -> List[str]:
        """解析代理列表字符串"""
        if not proxy_string:
            return []
        
        # 支持多种分隔符：逗号、分号、换行符
        proxies = []
        for proxy in proxy_string.replace('\n', ',').replace(';', ',').split(','):
            proxy = proxy.strip()
            if proxy and proxy.startswith(('http://', 'https://', 'socks5://')):
                proxies.append(proxy)
        
        return proxies
    
    def _parse_ua_list(self, ua_string: str) -> List[str]:
        """解析用户代理列表字符串"""
        if not ua_string:
            return []
        
        # 支持多种分隔符：逗号、分号、换行符
        uas = []
        for ua in ua_string.replace('\n', ',').replace(';', ',').split(','):
            ua = ua.strip()
            if ua:
                uas.append(ua)
        
        return uas
    
    def get_rate_limit_config(self) -> Dict[str, Any]:
        """获取限速配置"""
        return self.config['rate_limit']
    
    def get_retry_config(self) -> Dict[str, Any]:
        """获取重试配置"""
        return self.config['retry']
    
    def get_circuit_breaker_config(self) -> Dict[str, Any]:
        """获取熔断器配置"""
        return self.config['circuit_breaker']
    
    def get_proxy_config(self) -> Dict[str, Any]:
        """获取代理配置"""
        return self.config['proxy']
    
    def get_user_agent_config(self) -> Dict[str, Any]:
        """获取用户代理配置"""
        return self.config['user_agents']
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.config['logging']
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """获取监控配置"""
        return self.config['monitoring']
    
    def update_config(self, updates: Dict[str, Any]):
        """更新配置"""
        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, dict):
                    d[k] = deep_update(d.get(k, {}), v)
                else:
                    d[k] = v
            return d
        
        self.config = deep_update(self.config, updates)
    
    def save_config(self, config_path: str = None):
        """保存配置到文件"""
        save_path = config_path or self.config_path
        
        # 确保目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"配置已保存到: {save_path}")
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def validate_config(self) -> bool:
        """验证配置有效性"""
        try:
            # 验证限速配置
            rate_limit = self.config['rate_limit']
            if rate_limit['max_requests_per_second'] <= 0:
                print("错误: max_requests_per_second 必须大于0")
                return False
            
            if rate_limit['max_concurrent'] <= 0:
                print("错误: max_concurrent 必须大于0")
                return False
            
            # 验证重试配置
            retry = self.config['retry']
            if retry['max_retries'] < 0:
                print("错误: max_retries 不能为负数")
                return False
            
            if retry['base_delay'] <= 0:
                print("错误: base_delay 必须大于0")
                return False
            
            # 验证熔断器配置
            cb = self.config['circuit_breaker']
            if cb['failure_threshold'] <= 0:
                print("错误: failure_threshold 必须大于0")
                return False
            
            if cb['recovery_timeout'] <= 0:
                print("错误: recovery_timeout 必须大于0")
                return False
            
            return True
            
        except Exception as e:
            print(f"配置验证失败: {e}")
            return False
    
    def print_config(self):
        """打印当前配置"""
        print("=== 中间件配置 ===")
        print(json.dumps(self.config, indent=2, ensure_ascii=False))

# 环境特定配置
ENV_CONFIGS = {
    'development': {
        'rate_limit': {
            'max_requests_per_second': 2.0,
            'max_concurrent': 3
        },
        'retry': {
            'max_retries': 2,
            'base_delay': 0.5
        },
        'logging': {
            'level': 'DEBUG'
        }
    },
    'testing': {
        'rate_limit': {
            'max_requests_per_second': 1.0,
            'max_concurrent': 2
        },
        'retry': {
            'max_retries': 1,
            'base_delay': 0.1
        },
        'logging': {
            'level': 'DEBUG'
        }
    },
    'production': {
        'rate_limit': {
            'max_requests_per_second': 4.0,
            'max_concurrent': 5
        },
        'retry': {
            'max_retries': 3,
            'base_delay': 1.0
        },
        'logging': {
            'level': 'INFO'
        }
    }
}

def get_env_config(env: str = None) -> MiddlewareConfig:
    """获取环境特定配置"""
    if not env:
        env = os.getenv('ENV', 'development')
    
    config = MiddlewareConfig()
    
    if env in ENV_CONFIGS:
        config.update_config(ENV_CONFIGS[env])
    
    return config

# 预设配置
PRESET_CONFIGS = {
    'conservative': {
        'rate_limit': {
            'max_requests_per_second': 2.0,
            'max_concurrent': 3
        },
        'retry': {
            'max_retries': 5,
            'base_delay': 2.0
        },
        'circuit_breaker': {
            'failure_threshold': 3,
            'recovery_timeout': 120.0
        }
    },
    'balanced': {
        'rate_limit': {
            'max_requests_per_second': 4.0,
            'max_concurrent': 5
        },
        'retry': {
            'max_retries': 3,
            'base_delay': 1.0
        },
        'circuit_breaker': {
            'failure_threshold': 5,
            'recovery_timeout': 60.0
        }
    },
    'aggressive': {
        'rate_limit': {
            'max_requests_per_second': 8.0,
            'max_concurrent': 10
        },
        'retry': {
            'max_retries': 2,
            'base_delay': 0.5
        },
        'circuit_breaker': {
            'failure_threshold': 8,
            'recovery_timeout': 30.0
        }
    }
}

def get_preset_config(preset_name: str) -> MiddlewareConfig:
    """获取预设配置"""
    if preset_name not in PRESET_CONFIGS:
        raise ValueError(f"未知的预设配置: {preset_name}")
    
    config = MiddlewareConfig()
    config.update_config(PRESET_CONFIGS[preset_name])
    return config

if __name__ == "__main__":
    # 测试配置
    print("=== 测试默认配置 ===")
    config = MiddlewareConfig()
    config.print_config()
    
    print("\n=== 测试环境配置 ===")
    env_config = get_env_config('development')
    env_config.print_config()
    
    print("\n=== 测试预设配置 ===")
    preset_config = get_preset_config('conservative')
    preset_config.print_config()
    
    # 测试配置验证
    print(f"\n配置验证结果: {config.validate_config()}")
    
    # 测试配置保存
    test_config_path = PROJECT_ROOT / "config" / "test_middleware.json"
    config.save_config(str(test_config_path))
    
    # 清理测试文件
    if test_config_path.exists():
        test_config_path.unlink()
        print(f"已清理测试配置文件: {test_config_path}")
