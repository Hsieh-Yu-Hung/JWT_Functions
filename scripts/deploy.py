#!/usr/bin/env python3
"""
Function Compute 部署腳本
使用 JSON 配置檔案管理部署設定
"""

import json
import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import Dict, Any
import shlex

class FunctionComputeDeployer:
    """Function Compute 部署器"""
    
    def __init__(self, config_path: str = "config/fc-config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.env_vars = self._load_env_vars()
    
    def _load_config(self) -> Dict[str, Any]:
        """載入配置檔案"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ 配置檔案不存在: {self.config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ 配置檔案格式錯誤: {e}")
            sys.exit(1)
    
    def _load_env_vars(self) -> Dict[str, str]:
        """載入環境變數"""
        env_vars = {}
        env_file = Path(".env")
        
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key] = value.strip('"')
        
        return env_vars
    
    def _run_command(self, command: str, check: bool = True) -> subprocess.CompletedProcess:
        """執行命令"""
        print(f"🔄 執行命令: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            print(f"📤 輸出: {result.stdout}")
        if result.stderr:
            print(f"⚠️  錯誤: {result.stderr}")
        
        if check and result.returncode != 0:
            print(f"❌ 命令執行失敗: {command}")
            sys.exit(1)
        
        return result
    
    def _get_acr_credentials(self) -> tuple:
        """取得 ACR 認證資訊"""
        username = self.env_vars.get('ACR_USERNAME')
        password = self.env_vars.get('ACR_PASSWORD')
        
        if not username or not password:
            print("❌ ACR_USERNAME 或 ACR_PASSWORD 未設定，請檢查 .env 檔案")
            sys.exit(1)
        
        return username, password
    
    def login_acr(self) -> None:
        """登入 ACR"""
        print("🔐 登入 ACR...")
        username, password = self._get_acr_credentials()
        domain = self.config['acr']['domain']
        
        # 清理密碼和帳號，移除可能的引號和空白
        username = username.strip().strip('"').strip("'")
        password = password.strip().strip('"').strip("'")
        
        print(f"🔍 使用帳號: {username}")
        print(f"🔍 使用域名: {domain}")
        
        # 使用 subprocess.Popen 來避免 shell 轉義問題
        try:
            process = subprocess.Popen(
                ['docker', 'login', '--username', username, '--password-stdin', domain],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input=password)
            
            if process.returncode == 0:
                print("✅ ACR 登入成功")
                if stdout:
                    print(f"📤 輸出: {stdout}")
            else:
                print(f"❌ ACR 登入失敗")
                if stderr:
                    print(f"⚠️  錯誤: {stderr}")
                if stdout:
                    print(f"📤 輸出: {stdout}")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ 登入過程發生錯誤: {e}")
            sys.exit(1)
    
    def build_image(self) -> None:
        """建構 Docker 映像檔"""
        print("🔨 建構 Docker 映像檔...")
        image_name = self.config['acr']['imageName']
        image_version = self.config['acr']['imageVersion']
        
        build_cmd = f"docker build -t {image_name}:{image_version} ."
        self._run_command(build_cmd)
        print("✅ Docker 映像檔建構成功")
    
    def tag_image(self) -> None:
        """為映像檔打標籤"""
        print("🏷️  為映像檔打標籤...")
        acr_config = self.config['acr']
        image_name = acr_config['imageName']
        image_version = acr_config['imageVersion']
        domain = acr_config['domain']
        namespace = acr_config['namespace']
        
        tag_cmd = f"docker tag {image_name}:{image_version} {domain}/{namespace}/{image_name}:{image_version}"
        self._run_command(tag_cmd)
        print("✅ 映像檔標籤完成")
    
    def push_image(self) -> None:
        """推送映像檔到 ACR"""
        print("📤 推送映像檔到 ACR...")
        acr_config = self.config['acr']
        domain = acr_config['domain']
        namespace = acr_config['namespace']
        image_name = acr_config['imageName']
        image_version = acr_config['imageVersion']
        
        push_cmd = f"docker push {domain}/{namespace}/{image_name}:{image_version}"
        self._run_command(push_cmd)
        print("✅ 映像檔推送成功")
    
    def update_function(self) -> None:
        """更新 Function Compute 服務"""
        print("🔄 更新 Function Compute 服務...")
        
        function_config = self.config['function']
        container_config = self.config['container']
        region = self.config['region']
        
        # 準備更新請求的 JSON 內容
        update_body = {
            "customContainerConfig": {
                "image": container_config['image'],
                "port": container_config['port']
            }
        }
        
        if container_config.get('command'):
            update_body['customContainerConfig']['command'] = container_config['command']
        if container_config.get('entrypoint'):
            update_body['customContainerConfig']['entrypoint'] = container_config['entrypoint']
        
        # 寫入臨時檔案
        temp_file = "temp_update_body.json"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(update_body, f, indent=2)
        
        try:
            # 讀取 JSON 內容
            with open(temp_file, 'r', encoding='utf-8') as f:
                body_content = f.read()
            # 用 subprocess 陣列方式執行，避免 shell 轉義問題
            cmd = [
                'aliyun', 'fc', 'UpdateFunction',
                '--region', region,
                '--functionName', function_config['name'],
                '--body', body_content
            ]
            print(f"🔄 執行命令: {' '.join(shlex.quote(x) for x in cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.stdout:
                print(f"📤 輸出: {result.stdout}")
            if result.stderr:
                print(f"⚠️  錯誤: {result.stderr}")
            if result.returncode != 0:
                print(f"❌ 命令執行失敗: {' '.join(cmd)}")
                sys.exit(1)
            print("✅ Function Compute 服務更新成功")
        finally:
            # 清理臨時檔案
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def deploy(self, skip_build: bool = False) -> None:
        """執行完整部署流程"""
        print("🚀 開始部署 Function Compute 服務...")
        print(f"📋 使用配置檔案: {self.config_path}")
        
        if not skip_build:
            self.login_acr()
            self.build_image()
            self.tag_image()
            self.push_image()
        
        self.update_function()
        print("🎉 部署完成！")
    
    def validate_config(self) -> None:
        """驗證配置檔案"""
        print("🔍 驗證配置檔案...")
        
        required_sections = ['function', 'container', 'vpc', 'log', 'acr']
        for section in required_sections:
            if section not in self.config:
                print(f"❌ 缺少必要配置區段: {section}")
                sys.exit(1)
        
        required_function_fields = ['name', 'runtime', 'handler', 'timeout', 'memorySize']
        for field in required_function_fields:
            if field not in self.config['function']:
                print(f"❌ 缺少必要函數配置: {field}")
                sys.exit(1)
        
        print("✅ 配置檔案驗證通過")
    
    def show_status(self) -> None:
        """顯示部署狀態"""
        print("📊 部署狀態資訊:")
        print(f"  函數名稱: {self.config['function']['name']}")
        print(f"  運行時: {self.config['function']['runtime']}")
        print(f"  記憶體: {self.config['function']['memorySize']} MB")
        print(f"  超時: {self.config['function']['timeout']} 秒")
        print(f"  映像檔: {self.config['container']['image']}")
        print(f"  區域: {self.config['region']}")
        
        # 檢查 ACR 認證
        username, password = self._get_acr_credentials()
        print(f"  ACR 認證: {'✅ 已設定' if username and password else '❌ 未設定'}")


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='Function Compute 部署工具')
    parser.add_argument('--config', '-c', default='config/fc-config.json', 
                       help='配置檔案路徑 (預設: config/fc-config.json)')
    parser.add_argument('--skip-build', action='store_true', 
                       help='跳過 Docker 建構步驟')
    parser.add_argument('--validate', action='store_true', 
                       help='僅驗證配置檔案')
    parser.add_argument('--status', action='store_true', 
                       help='顯示部署狀態')
    
    args = parser.parse_args()
    
    deployer = FunctionComputeDeployer(args.config)
    
    if args.validate:
        deployer.validate_config()
    elif args.status:
        deployer.show_status()
    else:
        deployer.deploy(skip_build=args.skip_build)


if __name__ == '__main__':
    main() 