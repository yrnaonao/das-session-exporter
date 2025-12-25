# MySQL Session Prometheus Exporter
基于 FastAPI 的 Prometheus 自定义 Exporter,用于导出阿里云 RDS/PolarDB MySQL 实例的用户会话数指标。

## 功能特性
- 支持 RDS MySQL 和 PolarDB MySQL 实例
- 异步调用阿里云 DAS API 获取会话信息
- 调用阿里云DAS API要支持限流，阿里云DAS API自身有流控（60次/s）尽量避免触发次流控
- 按用户维度统计会话数
- 支持 PolarDB 多节点监控
- 自动定期更新指标
- 支持手动触发更新
- 不同指标支持不同的缓存时间控制
- 支持多阿里云账号

## 项目结构要求
- 按模块划分目录
- 程序入口放在./下
- 代码要简洁易读

## 其他说明
* apis.md： das api示例
* db.md： 表结构

## Prometheus 指标
### db_user_session_count
**类型**: Gauge  
**描述**: 数据库用户会话数  
**Labels**:
- `ins_id`: 实例ID
- `ins_name`: 实例名称
- `ins_type`: 实例类型 (RDS/PolarDB)
- `aliyun_uid`: 阿里云账号ID
- `db_user`: 数据库用户名
- `node_id`: 节点ID (PolarDB有值,RDS为空)
- `node_type`: 节点类型 (read/write)

**示例**:
```
db_user_session_count{ins_id="rm-xxx",ins_name="test_mysql",ins_type="rds",aliyun_uid="123456",db_user="app_user",node_id="",node_type="write"} 10
db_user_session_count{ins_id="pc-xxx",ins_name="test_polardb",ins_type="polardb",aliyun_uid="123456",db_user="app_user",node_id="pi-xxx1",node_type="write"} 5
db_user_session_count{ins_id="pc-xxx",ins_name="test_polardb",ins_type="polardb",aliyun_uid="123456",db_user="app_user",node_id="pi-xxx2",node_type="read"} 3
```

### db_max_user_connections
**类型**: Gauge
**描述**: 用户最大连接数
**Labels**:
- `ins_id`: 实例ID
- `username`: 用户名

**示例**:
```
db_max_user_connections{ins_id="rm-xxx",username="app_user"} 100
db_max_user_connections{ins_id="pc-xxx",username="app_user"} 200
```

## 数据库表结构

服务需要以下数据库表(详见 db.md):
- `instance_list`: 实例列表
- `instance_node_id`: 节点信息 (PolarDB)
- `instance_conn`: 连接信息
- `instance_users`: 数据库用户max_user_connections表

## 工作原理

### db_user_session_count 指标
1. 从 `instance_list` 表查询所有启用的实例 (`ins_status=1`)
2. 对于 RDS 实例:
   - 直接调用 DAS API 获取会话信息
   - 根据 `ins_is_readonly` 判断节点类型
     * 0: 读写(write)
     * 1: 只读(read)
3. 对于 PolarDB 实例:
   - 从 `instance_node_id` 表查询所有节点
   - 并发调用 DAS API 获取每个节点的会话信息
4. 解析返回的 `UserStats` 数据,按用户统计会话数
5. 生成 Prometheus 指标并导出

### db_max_user_connections 指标
1. 从 `instance_users` 查询所有数据导出即可

## 注意事项
1. DAS API 采用异步调用方式,需要轮询获取结果
2. 建议更新间隔不要太短,避免频繁调用 API
3. Prometheus 客户端已自动移除默认收集器(GC_COLLECTOR, PLATFORM_COLLECTOR, PROCESS_COLLECTOR)
4. 不同指标有不同的缓存时间控制

## 故障排查

### 日志级别
服务使用 Python logging,默认日志级别为 INFO。主要日志包括:
- 实例查询和会话收集
- DAS API 调用和结果轮询
- 指标更新和缓存状态
- 错误和异常信息
