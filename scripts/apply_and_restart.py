#!/usr/bin/env python3
"""
应用OpenClaw配置并重启Gateway
"""

import subprocess
import sys
import time
from pathlib import Path

def run_command(command, description):
    """运行命令行命令"""
    print(f"🔄 {description}...")
    print(f"   命令: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print(f"✅ {description}成功")
            if result.stdout.strip():
                print(f"   输出: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description}失败")
            print(f"   错误: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 执行命令时出错: {e}")
        return False

def apply_and_restart():
    """应用配置并重启Gateway"""
    print("🚀 OpenClaw配置应用和重启工具")
    print("=" * 50)
    
    # 检查配置文件
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        print("请先运行 setup_multi_bot.py 创建配置文件")
        return 1
    
    print(f"📁 配置文件: {config_path}")
    
    # 验证配置文件
    print("\n1. 验证配置文件...")
    validate_cmd = f"python {Path(__file__).parent / 'validate_config.py'} --config-path {config_path}"
    if not run_command(validate_cmd, "验证配置文件"):
        print("⚠️  配置文件验证失败，建议检查配置文件")
        proceed = input("是否继续重启？(y/N): ")
        if proceed.lower() != 'y':
            print("❌ 用户取消操作")
            return 1
    
    # 检查Gateway状态
    print("\n2. 检查Gateway状态...")
    if not run_command("openclaw gateway status", "检查Gateway状态"):
        print("⚠️  Gateway状态检查失败，可能未安装或未运行")
        proceed = input("是否继续重启？(y/N): ")
        if proceed.lower() != 'y':
            print("❌ 用户取消操作")
            return 1
    
    # 显示当前配置
    print("\n3. 显示当前配置...")
    run_command(f"python {Path(__file__).parent / 'list_feishu_accounts.py'}", "显示飞书账户配置")
    
    # 备份当前状态
    print("\n4. 备份当前状态...")
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_cmd = f"openclaw config get > {config_path.parent}/config-backup-{timestamp}.json"
    run_command(backup_cmd, "备份当前配置")
    
    # 重启Gateway
    print("\n5. 重启OpenClaw Gateway...")
    print("⚠️  这将暂时中断服务，请确认")
    confirm = input("确认重启Gateway？(y/N): ")
    
    if confirm.lower() != 'y':
        print("❌ 用户取消重启")
        return 0
    
    if run_command("openclaw gateway restart", "重启Gateway"):
        print("✅ Gateway重启命令已发送")
        print("ℹ️  重启可能需要几秒钟时间...")
        
        # 等待重启完成
        print("\n6. 等待Gateway重启...")
        for i in range(10):
            print(f"   等待Gateway启动 ({i+1}/10)...")
            time.sleep(3)
            
            # 检查Gateway状态
            result = subprocess.run(
                "openclaw gateway status",
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and "running" in result.stdout.lower():
                print("✅ Gateway已成功启动")
                break
        else:
            print("⚠️  Gateway启动可能较慢，请稍后检查状态")
    
    # 显示重启后的状态
    print("\n7. 检查重启后状态...")
    run_command("openclaw gateway status", "Gateway状态")
    
    # 验证功能
    print("\n8. 验证功能...")
    run_command("openclaw channels list", "通道列表")
    run_command("openclaw agents bindings", "Agent绑定")
    
    print("\n🎉 配置应用完成！")
    print("=" * 50)
    print("📋 后续步骤:")
    print("1. 检查飞书机器人是否能正常接收消息")
    print("2. 验证各Agent是否按预期响应")
    print("3. 检查数据隔离配置是否生效")
    print("4. 监控日志查看是否有错误")
    print("\n📊 监控命令:")
    print("  openclaw logs --follow    # 实时日志")
    print("  openclaw status --deep    # 详细状态")
    print("  openclaw doctor           # 健康检查")
    
    return 0

def main():
    return apply_and_restart()

if __name__ == "__main__":
    sys.exit(main())