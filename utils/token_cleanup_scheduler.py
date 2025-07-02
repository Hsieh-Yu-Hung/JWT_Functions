#!/usr/bin/env python3
"""
Token 清理排程器
定期清理已過期的 token 以節省記憶體
"""

import time
import threading
from datetime import datetime
from flask import current_app
from jwt_auth_middleware import JWTManager
import os

class TokenCleanupScheduler:
    def __init__(self, cleanup_interval_minutes=60):
        """
        初始化清理排程器
        
        Args:
            cleanup_interval_minutes (int): 清理間隔（分鐘）
        """
        self.cleanup_interval = cleanup_interval_minutes * 60  # 轉換為秒
        self.running = False
        self.thread = None
        
    def _get_jwt_manager(self):
        """獲取 JWT Manager 實例"""
        if hasattr(current_app, 'jwt_manager'):
            return current_app.jwt_manager
        else:
            # 如果沒有 Flask context，創建一個新的 JWT Manager
            jwt_manager = JWTManager(
                secret_key=os.environ['JWT_SECRET_KEY'],
                algorithm='HS256',
                token_expire_hours=24,
                blacklist_enabled=True
            )
            return jwt_manager
        
    def start(self):
        """啟動自動清理排程器"""
        if self.running:
            print("清理排程器已在運行中")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.thread.start()
        print(f"Token 清理排程器已啟動，清理間隔：{self.cleanup_interval // 60} 分鐘")
        
    def stop(self):
        """停止自動清理排程器"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("Token 清理排程器已停止")
        
    def _cleanup_loop(self):
        """清理循環"""
        while self.running:
            try:
                # 執行清理
                jwt_manager = self._get_jwt_manager()
                cleaned_count = jwt_manager.cleanup_expired_tokens()
                stats = jwt_manager.get_blacklist_stats()
                
                if cleaned_count > 0:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                          f"清理了 {cleaned_count} 個過期 token，"
                          f"剩餘 {stats.get('total_tokens', 0)} 個 token")
                
                # 等待下次清理
                time.sleep(self.cleanup_interval)
                
            except Exception as e:
                print(f"清理過程中發生錯誤: {e}")
                time.sleep(60)  # 發生錯誤時等待 1 分鐘後重試
                
    def manual_cleanup(self):
        """手動執行清理"""
        try:
            jwt_manager = self._get_jwt_manager()
            cleaned_count = jwt_manager.cleanup_expired_tokens()
            stats = jwt_manager.get_blacklist_stats()
            
            print(f"手動清理完成：")
            print(f"- 清理了 {cleaned_count} 個過期 token")
            print(f"- 剩餘 {stats.get('total_tokens', 0)} 個 token")
            print(f"- 預估記憶體使用量：{stats.get('estimated_memory_usage', 0)} bytes")
            
            return cleaned_count
        except Exception as e:
            print(f"手動清理失敗: {e}")
            return 0

# 全域清理排程器實例
cleanup_scheduler = TokenCleanupScheduler()

def start_cleanup_scheduler():
    """啟動清理排程器"""
    cleanup_scheduler.start()

def stop_cleanup_scheduler():
    """停止清理排程器"""
    cleanup_scheduler.stop()

def manual_cleanup():
    """手動執行清理"""
    return cleanup_scheduler.manual_cleanup()

if __name__ == "__main__":
    # 測試清理功能
    print("🧹 Token 清理排程器測試")
    print("=" * 50)
    
    # 手動清理測試
    print("執行手動清理...")
    cleaned = manual_cleanup()
    print(f"清理了 {cleaned} 個過期 token")
    
    # 啟動自動清理（每 120 分鐘清理一次）
    print("\n啟動自動清理排程器（每 120 分鐘清理一次）...")
    scheduler = TokenCleanupScheduler(cleanup_interval_minutes=120)
    scheduler.start()
    
    try:
        # 運行 30 秒後停止
        time.sleep(30)
    except KeyboardInterrupt:
        print("\n收到中斷信號，正在停止...")
    finally:
        scheduler.stop()
        print("測試完成") 