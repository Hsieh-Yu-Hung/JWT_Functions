#!/usr/bin/env python3
"""
配置檔案測試腳本
用於驗證 Function Compute 配置檔案的格式和內容
"""

import json
import sys
from pathlib import Path


def test_config_file(config_path: str = "config/fc-config.json"):
    """測試配置檔案"""
    print(f"🔍 測試配置檔案: {config_path}")
    
    # 檢查檔案是否存在
    if not Path(config_path).exists():
        print(f"❌ 配置檔案不存在: {config_path}")
        return False
    
    try:
        # 載入配置檔案
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ JSON 格式正確")
        
        # 檢查必要區段
        required_sections = ['function', 'container', 'vpc', 'log', 'acr']
        for section in required_sections:
            if section not in config:
                print(f"❌ 缺少必要區段: {section}")
                return False
            print(f"✅ 區段存在: {section}")
        
        # 檢查 function 區段
        function_fields = ['name', 'runtime', 'handler', 'timeout', 'memorySize']
        for field in function_fields:
            if field not in config['function']:
                print(f"❌ 缺少函數配置: {field}")
                return False
            print(f"✅ 函數配置: {field} = {config['function'][field]}")
        
        # 檢查 container 區段
        container_fields = ['image', 'port']
        for field in container_fields:
            if field not in config['container']:
                print(f"❌ 缺少容器配置: {field}")
                return False
            print(f"✅ 容器配置: {field} = {config['container'][field]}")
        
        # 檢查 acr 區段
        acr_fields = ['domain', 'namespace', 'imageName', 'imageVersion']
        for field in acr_fields:
            if field not in config['acr']:
                print(f"❌ 缺少 ACR 配置: {field}")
                return False
            print(f"✅ ACR 配置: {field} = {config['acr'][field]}")
        
        # 檢查 vpc 區段
        vpc_fields = ['vpcId', 'vSwitchIds', 'securityGroupId']
        for field in vpc_fields:
            if field not in config['vpc']:
                print(f"❌ 缺少 VPC 配置: {field}")
                return False
            print(f"✅ VPC 配置: {field} = {config['vpc'][field]}")
        
        # 檢查 log 區段
        log_fields = ['project', 'logstore']
        for field in log_fields:
            if field not in config['log']:
                print(f"❌ 缺少日誌配置: {field}")
                return False
            print(f"✅ 日誌配置: {field} = {config['log'][field]}")
        
        print("\n🎉 配置檔案測試通過！")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON 格式錯誤: {e}")
        return False
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False


def main():
    """主函數"""
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/fc-config.json"
    
    success = test_config_file(config_path)
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main() 