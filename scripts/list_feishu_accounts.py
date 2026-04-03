#!/usr/bin/env python3
"""
查看当前OpenClaw配置中的飞书账户配置
"""

import json
import os
import sys
from pathlib import Path

def get_openclaw_config_path():
    """获取OpenClaw配置文件路径"""
    # 尝试多个可能的路径
    paths = [
        Path.home() / ".openclaw" / "openclaw.json",
        Path.home() / "AppData" / "Roaming" / "zhengfeiClaw" / "openclaw" / "state" / "openclaw.json",
        Path.home() / ".config" / "openclaw" / "openclaw.json",
        Path.home() / "zhengfeiClaw" / "project" / "openclaw.json",
    ]
    
    for path in paths:
        if path.exists():
            return path
    
    # 如果文件不存在，提示用户
    print("错误：找不到OpenClaw配置文件。")
    print("请确认OpenClaw已安装且配置文件存在。")
    print("可能的位置：")
    for path in paths:
        print(f"  {path}")
    return None

def list_feishu_accounts():
    """列出飞书账户配置"""
    config_path = get_openclaw_config_path()
    if not config_path:
        return 1
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"错误：无法读取配置文件 {config_path}: {e}")
        return 1
    
    # 检查飞书配置
    channels = config.get('channels', {})
    feishu_config = channels.get('feishu', {})
    
    if not feishu_config:
        print("未找到飞书通道配置。")
        return 0
    
    accounts = feishu_config.get('accounts', {})
    
    if not accounts:
        print("未找到飞书账户配置。")
        return 0
    
    print("飞书账户配置：")
    print("=" * 80)
    
    for account_id, account_config in accounts.items():
        print(f"\n账户ID: {account_id}")
        print(f"  应用名称: {account_config.get('botName', '未设置')}")
        print(f"  App ID: {account_config.get('appId', '未设置')}")
        print(f"  DM策略: {account_config.get('dmPolicy', '未设置')}")
        
        allow_from = account_config.get('allowFrom', [])
        if allow_from:
            print(f"  允许来源: {', '.join(allow_from)}")
        else:
            print("  允许来源: 无限制")
    
    # 检查绑定规则
    bindings = config.get('bindings', [])
    feishu_bindings = [b for b in bindings if b.get('match', {}).get('channel') == 'feishu']
    
    if feishu_bindings:
        print("\n飞书绑定规则：")
        print("-" * 80)
        for binding in feishu_bindings:
            agent_id = binding.get('agentId', '未知')
            match = binding.get('match', {})
            account_id = match.get('accountId', '未知')
            peer = match.get('peer', {})
            
            print(f"  Agent: {agent_id} -> 飞书账户: {account_id}")
            if peer:
                print(f"    特殊规则: {peer.get('kind', '未知')} ID={peer.get('id', '未知')}")
    
    # 检查Agent配置
    agents = config.get('agents', {}).get('list', [])
    if agents:
        print("\nAgent配置：")
        print("-" * 80)
        for agent in agents:
            agent_id = agent.get('id', '未知')
            name = agent.get('name', '未命名')
            default = agent.get('default', False)
            shared_skills = agent.get('sharedSkills', '未设置')
            data_isolation = agent.get('dataIsolation', {})
            
            print(f"  ID: {agent_id}")
            print(f"    名称: {name}")
            print(f"    默认: {'是' if default else '否'}")
            print(f"    共享Skill: {shared_skills}")
            if data_isolation:
                enabled = data_isolation.get('enabled', False)
                shared_types = data_isolation.get('sharedTypes', [])
                print(f"    数据隔离: {'启用' if enabled else '禁用'}")
                if enabled and shared_types:
                    print(f"    共享类型: {', '.join(shared_types)}")
    
    print("\n" + "=" * 80)
    print(f"配置文件路径: {config_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(list_feishu_accounts())