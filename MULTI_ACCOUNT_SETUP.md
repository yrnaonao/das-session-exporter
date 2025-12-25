# 多阿里云账号配置指南

本指南介绍如何配置多个阿里云账号以使用MySQL Session Prometheus Exporter。

## 配置方式

目前，多阿里云账号的配置主要通过数据库中的 `instance_list` 表来管理。每个实例记录都包含一个 `aliyun_uid` 字段，用于标识该实例所属的阿里云账号。

## 实现原理

1. **数据库表结构**：
   - `instance_list` 表的 `aliyun_uid` 字段存储阿里云账号ID
   - 每个实例记录都关联到一个特定的阿里云账号

2. **认证机制**：
   - DAS客户端支持按账号ID缓存客户端实例
   - 通过数据库中的 `aliyun_accounts` 表管理多个账号的认证信息
   - Access Key Secret经过加密存储在数据库中
   - 支持动态切换不同账号的认证信息

## 配置步骤

### 1. 数据库配置

在 `instance_list` 表中添加不同阿里云账号的实例：

```sql
INSERT INTO instance_list(ins_id, ins_name, ins_is_readonly, ins_type, ins_status, engine, engine_version, aliyun_uid) VALUES
(
    'rm-d9jv538yq00q451nh',
    'idn_pro_user_master_mysql',
    0,
    'rds',
    1,
    'mysql',
    '5.7',
    '1234567890123456'  -- 第一个阿里云账号ID
),
(
    'pc-d9jvgnk479vd24gb3',
    'idn_pro_listing_legal_polardb',
    0,
    'polardb',
    1,
    'mysql',
    '8.0.1',
    '9876543210987654'  -- 第二个阿里云账号ID
);
```

### 2. 认证信息管理

通过数据库表配置多账号的认证信息，使用提供的工具函数添加账号：

```python
from sqlalchemy.orm import sessionmaker
from models.database import engine
from utils.account_manager import add_aliyun_account

# 创建数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # 添加阿里云账号
    add_aliyun_account(
        db=db,
        aliyun_uid='1234567890123456',  # 阿里云账号ID
        access_key_id='your_access_key_id_for_account_1',
        access_key_secret='your_access_key_secret_for_account_1',
        region_id='cn-shanghai'
    )
    
    # 添加第二个阿里云账号
    add_aliyun_account(
        db=db,
        aliyun_uid='9876543210987654',  # 阿里云账号ID
        access_key_id='your_access_key_id_for_account_2',
        access_key_secret='your_access_key_secret_for_account_2',
        region_id='cn-shanghai'
    )
finally:
    db.close()
```

### 3. 环境变量配置

配置加密密码和其他通用设置：

```bash
export ENCRYPTION_PASSWORD=your_strong_encryption_password_here
export ALIBABA_CLOUD_REGION_ID=cn-shanghai
```

## 使用说明

1. **数据隔离**：不同阿里云账号的实例数据在数据库中是隔离的
2. **指标标签**：收集的指标会包含 `aliyun_uid` 标签，便于区分不同账号的实例
3. **API调用**：系统会根据实例所属的阿里云账号自动使用相应的认证信息进行API调用
4. **客户端缓存**：为每个阿里云账号缓存独立的DAS客户端实例，提高性能
5. **安全存储**：Access Key Secret经过加密后存储在数据库中

## 配置验证

启动应用后，查看日志确认多账号配置是否生效：

```bash
python run.py
```

在日志中应能看到类似以下信息：
```
处理实例: rm-xxx, 类型: rds, 阿里云账号: 1234567890123456
获取RDS实例 rm-xxx 的会话信息成功
```

## 扩展建议

为了实现更高级的多账号支持，可以考虑：

1. **数据库配置表**：创建专门的账号认证配置表存储认证信息
2. **API密钥轮换**：实现安全的API密钥管理机制
3. **权限管理**：为不同账号配置不同的权限级别

## 注意事项

- 在生产环境中，请确保加密密码的安全性
- 阿里云DAS API有流控限制（60次/秒），多账号调用也受此限制
- 不同账号的实例调用会共享API调用配额
- 数据库中存储的阿里云账号ID必须与 `instance_list` 表的 `aliyun_uid` 字段完全匹配