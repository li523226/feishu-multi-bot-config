#!/usr/bin/env python3
"""
查看OpenClaw绑定规则配置
"""

import json
import sys
from pathlib import Path

def get_config_path():
    """获取配置文件路径"""
    paths = [
        Path.home() / ".openclaw" / "openclaw.json",
        Path.home() / "AppData" / "Roaming" / "zhengfeiClaw" / "openclaw" / "state" / "openclaw.json",
    ]
    
    for path in paths:
        if path.exists():
            return path
    
    return None

def load_config(config_path):
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 无法读取配置文件: {e}")
        return None

def list_bindings():
    """列出绑定规则"""
    config_path = get_config_path()
    if not config_path:
        print("❌ 找不到OpenClaw配置文件")
        return 1
    
    config = load_config(config_path)
    if config is None:
        return 1
    
    bindings = config.get("bindings", [])
    if not bindings:
        print("📋 没有配置绑定规则")
        return 0
    
    print("📋 OpenClaw绑定规则")
    print("=" * 80)
    
    # 按通道分组
    channels = {}
    for binding in bindings:
        match = binding.get("match", {})
        channel = match.get("channel", "未知")
        
        if channel not in channels:
            channels[channel] = []
        channels[channel].append(binding)
    
    # 显示每个通道的绑定规则
    for channel, channel_bindings in channels.items():
        print(f"\n📡 通道: {channel}")
        print("-" * 40)
        
        for i, binding in enumerate(channel_bindings, 1):
            agent_id = binding.get("agentId", "未知")
            match = binding.get("match", {})
            
            print(f"{i}. Agent: {agent_id}")
            print(f"   匹配规则:")
            
            # 显示匹配条件
            conditions = []
            
            # 账户ID匹配
            account_id = match.get("accountId")
            if account_id:
                conditions.append(f"账户ID: {account_id}")
            
            # 对等方匹配
            peer = match.get("peer")
            if peer:
                peer_kind = peer.get("kind", "未知")
                peer_id = peer.get("id", "未知")
                conditions.append(f"{peer_kind}: {peer_id}")
            
            # 其他匹配条件
            for key, value in match.items():
                if key not in ["channel", "accountId", "peer"]:
                    conditions.append(f"{key}: {value}")
            
            if conditions:
                for condition in conditions:
                    print(f"      - {condition}")
            else:
                print("      - 无具体匹配条件")
    
    # 显示绑定统计
    print("\n📊 绑定统计")
    print("-" * 40)
    
    total_bindings = len(bindings)
    feishu_bindings = len([b for b in bindings if b.get("match", {}).get("channel") == "feishu"])
    other_bindings = total_bindings - feishu_bindings
    
    print(f"总绑定规则: {total_bindings}")
    print(f"飞书绑定规则: {feishu_bindings}")
    print(f"其他通道绑定规则: {other_bindings}")
    
    # 检查绑定完整性
    print("\n🔍 绑定完整性检查")
    print("-" * 40)
    
    # 获取所有Agent ID
    agents = config.get("agents", {}).get("list", [])
    agent_ids = {agent.get("id") for agent in agents}
    
    # 获取所有绑定的Agent ID
    bound_agent_ids = {binding.get("agentId") for binding in bindings}
    
    # 未绑定的Agent
    unbound_agents = agent_ids - bound_agent_ids
    if unbound_agents:
        print(f"⚠️  未绑定的Agent: {', '.join(unbound_agents)}")
    else:
        print("✅ 所有Agent都有绑定规则")
    
    # 绑定到不存在的Agent
    invalid_bindings = bound_agent_ids - agent_ids
    if invalid_bindings:
        print(f"❌ 绑定到不存在的Agent: {', '.join(invalid_bindings)}")
    else:
        print("✅ 所有绑定规则都指向有效的Agent")
    
    # 检查飞书账户绑定
    if "feishu" in channels:
        feishu_accounts = config.get("channels", {}).get("feishu", {}).get("accounts", {})
        account_ids = set(feishu_accounts.keys())
        
        feishu_account_bindings = [b for b in channels["feishu"] if b.get("match", {}).get("accountId")]
        bound_account_ids = {b.get("match", {}).get("accountId") for b in feishu_account_bindings}
        
        # 未绑定的账户
        unbound_accounts = account_ids - bound_account_ids
        if unbound_accounts:
            print(f"⚠️  未绑定的飞书账户: {', '.join(unbound_accounts)}")
        
        # 绑定到不存在的账户
        invalid_account_bindings = bound_account_ids - account_ids
        if invalid_account_bindings:
            print(f"❌ 绑定到不存在的飞书账户: {', '.join(invalid_account_bindings)}")
    
    print("\n" + "=" * 80)
    print(f"配置文件: {config_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(list_bindings())