#!/usr/bin/env python3
"""
验证OpenClaw配置文件
"""

import json
import sys
import argparse
from pathlib import Path

def validate_config(config):
    """验证配置文件"""
    errors = []
    warnings = []
    
    # 检查必需字段
    required_fields = [
        ("agents", dict),
        ("agents.list", list),
        ("session", dict),
        ("channels", dict),
    ]
    
    for field_path, expected_type in required_fields:
        value = config
        path_parts = field_path.split('.')
        
        for part in path_parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                errors.append(f"缺少必需字段: {field_path}")
                break
        else:
            # 检查类型
            if not isinstance(value, expected_type):
                errors.append(f"字段 '{field_path}' 类型错误: 期望 {expected_type.__name__}, 实际 {type(value).__name__}")
    
    # 检查agents配置
    if "agents" in config and "list" in config["agents"]:
        agents = config["agents"]["list"]
        
        # 检查是否有Agent
        if not agents:
            warnings.append("agents.list 为空，没有配置任何Agent")
        else:
            # 检查Agent配置
            for i, agent in enumerate(agents):
                agent_id = agent.get("id")
                agent_name = agent.get("name", "未命名")
                
                if not agent_id:
                    errors.append(f"第{i+1}个Agent缺少 'id' 字段")
                
                # 检查workspace路径
                workspace = agent.get("workspace")
                if not workspace:
                    warnings.append(f"Agent '{agent_id}' 缺少 'workspace' 字段")
                
                # 检查model配置
                if "model" not in agent:
                    warnings.append(f"Agent '{agent_id}' 缺少 'model' 配置")
                elif "primary" not in agent["model"]:
                    warnings.append(f"Agent '{agent_id}' 的 'model' 配置缺少 'primary' 字段")
            
            # 检查默认Agent
            default_agents = [a for a in agents if a.get("default", False)]
            if len(default_agents) == 0:
                warnings.append("没有设置默认Agent")
            elif len(default_agents) > 1:
                warnings.append(f"设置了 {len(default_agents)} 个默认Agent，推荐只设置一个")
    
    # 检查channels配置
    if "channels" in config:
        channels = config["channels"]
        
        # 检查飞书配置
        if "feishu" in channels:
            feishu = channels["feishu"]
            
            if not feishu.get("enabled", False):
                warnings.append("飞书通道未启用 (feishu.enabled: false)")
            
            # 检查accounts配置
            accounts = feishu.get("accounts", {})
            if not accounts:
                warnings.append("飞书账户配置为空")
            else:
                for account_id, account in accounts.items():
                    # 检查必要字段
                    if not account.get("appId"):
                        warnings.append(f"飞书账户 '{account_id}' 缺少 'appId'")
                    if not account.get("appSecret"):
                        warnings.append(f"飞书账户 '{account_id}' 缺少 'appSecret'")
                    if not account.get("botName"):
                        warnings.append(f"飞书账户 '{account_id}' 缺少 'botName'")
                    
                    # 检查dmPolicy
                    dm_policy = account.get("dmPolicy")
                    if dm_policy not in ["pairing", "allowlist", "open", "disabled"]:
                        warnings.append(f"飞书账户 '{account_id}' 的 dmPolicy 值不标准: {dm_policy}")
    
    # 检查bindings配置
    if "bindings" in config:
        bindings = config["bindings"]
        
        if not bindings:
            warnings.append("bindings 为空，没有配置任何绑定规则")
        else:
            # 检查绑定规则
            for i, binding in enumerate(bindings):
                if "agentId" not in binding:
                    errors.append(f"第{i+1}个绑定规则缺少 'agentId'")
                
                if "match" not in binding:
                    errors.append(f"第{i+1}个绑定规则缺少 'match'")
                else:
                    match = binding["match"]
                    if "channel" not in match:
                        warnings.append(f"第{i+1}个绑定规则的 'match' 缺少 'channel'")
                    
                    # 检查绑定目标
                    has_account = "accountId" in match
                    has_peer = "peer" in match
                    
                    if not has_account and not has_peer:
                        warnings.append(f"第{i+1}个绑定规则没有指定 accountId 或 peer")
    
    # 检查session配置
    if "session" in config:
        session = config["session"]
        
        dm_scope = session.get("dmScope")
        valid_scopes = ["main", "per-peer", "per-channel-peer", "per-account-channel-peer"]
        
        if dm_scope not in valid_scopes:
            warnings.append(f"session.dmScope 值不标准: {dm_scope} (应为 {', '.join(valid_scopes)})")
    
    return errors, warnings

def validate_config_file(config_path):
    """验证配置文件"""
    print(f"[验证] 验证配置文件: {config_path}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON格式错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 无法读取文件: {e}")
        return False
    
    errors, warnings = validate_config(config)
    
    # 显示结果
    if errors:
        print("\n❌ 发现错误:")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print("\n⚠️  发现警告:")
        for warning in warnings:
            print(f"  - {warning}")
    
    if not errors and not warnings:
        print("\n✅ 配置文件验证通过！")
        return True
    elif errors:
        print(f"\n❌ 验证失败: {len(errors)} 个错误, {len(warnings)} 个警告")
        return False
    else:
        print(f"\n⚠️  验证通过但有警告: {len(warnings)} 个警告")
        return True

def check_agent_bindings(config):
    """检查Agent绑定完整性"""
    print("\n🔗 检查Agent绑定完整性...")
    
    agents = config.get("agents", {}).get("list", [])
    bindings = config.get("bindings", [])
    
    agent_ids = {agent.get("id") for agent in agents}
    bound_agent_ids = {binding.get("agentId") for binding in bindings}
    
    # 检查未绑定的Agent
    unbound_agents = agent_ids - bound_agent_ids
    if unbound_agents:
        print(f"⚠️  以下Agent没有绑定规则: {', '.join(unbound_agents)}")
    
    # 检查绑定到不存在的Agent
    invalid_bindings = bound_agent_ids - agent_ids
    if invalid_bindings:
        print(f"❌ 以下绑定规则指向不存在的Agent: {', '.join(invalid_bindings)}")
    
    # 检查飞书账户绑定
    feishu_accounts = config.get("channels", {}).get("feishu", {}).get("accounts", {})
    account_ids = set(feishu_accounts.keys())
    
    feishu_bindings = [b for b in bindings if b.get("match", {}).get("channel") == "feishu"]
    bound_account_ids = {b.get("match", {}).get("accountId") for b in feishu_bindings if b.get("match", {}).get("accountId")}
    
    # 检查未绑定的飞书账户
    unbound_accounts = account_ids - bound_account_ids
    if unbound_accounts:
        print(f"⚠️  以下飞书账户没有绑定规则: {', '.join(unbound_accounts)}")
    
    # 检查绑定到不存在的飞书账户
    invalid_account_bindings = bound_account_ids - account_ids
    if invalid_account_bindings:
        print(f"❌ 以下绑定规则指向不存在的飞书账户: {', '.join(invalid_account_bindings)}")

def main():
    parser = argparse.ArgumentParser(description="验证OpenClaw配置文件")
    parser.add_argument("--config-path", required=True, help="OpenClaw配置文件路径")
    parser.add_argument("--fix", action="store_true", help="尝试自动修复问题")
    
    args = parser.parse_args()
    
    config_path = Path(args.config_path)
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        return 1
    
    # 验证配置文件
    is_valid = validate_config_file(config_path)
    
    # 加载配置进行更详细的分析
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ 无法加载配置进行详细分析: {e}")
        return 1
    
    # 检查Agent绑定
    check_agent_bindings(config)
    
    # 显示配置摘要
    print("\n📊 配置摘要:")
    print(f"  Agent数量: {len(config.get('agents', {}).get('list', []))}")
    print(f"  飞书账户数量: {len(config.get('channels', {}).get('feishu', {}).get('accounts', {}))}")
    print(f"  绑定规则数量: {len(config.get('bindings', []))}")
    
    if "session" in config:
        print(f"  session.dmScope: {config['session'].get('dmScope')}")
    
    return 0 if is_valid else 1

if __name__ == "__main__":
    sys.exit(main())