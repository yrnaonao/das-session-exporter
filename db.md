# 实例相关表结构
```
CREATE TABLE `instance_list` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ins_id` varchar(255) COLLATE utf8mb4_general_ci NOT NULL COMMENT '实例ID',
  `ins_name` varchar(255) COLLATE utf8mb4_general_ci NOT NULL COMMENT '实例名',
  `ins_is_readonly` int(11) NOT NULL COMMENT '是否为只读 1只读 0读写',
  `ins_type` varchar(255) COLLATE utf8mb4_general_ci NOT NULL COMMENT '实例类型 PolarDB RDS Mongodb',
  `ins_status` int(11) NOT NULL COMMENT '实例状态 0 禁用 1 启用',
  `engine` varchar(255) COLLATE utf8mb4_general_ci NOT NULL COMMENT '数据库引擎 mysql mongodb',
  `engine_version` varchar(255) COLLATE utf8mb4_general_ci NOT NULL COMMENT '引擎版本 5.7 8.0',
  `master_id` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '主库ID，从库才有的属性， RDS才有',
  `aliyun_uid` varchar(255) COLLATE utf8mb4_general_ci NOT NULL COMMENT '阿里云账号ID',
  `inserttime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  `updatetime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `ix_instance_list_aliyun_uid` (`aliyun_uid`),
  KEY `ix_instance_list_ins_id` (`ins_id`)
) ENGINE=InnoDB AUTO_INCREMENT=64 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
```

```
CREATE TABLE `instance_node_id` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ins_id` varchar(255) COLLATE utf8mb4_general_ci NOT NULL COMMENT '实例ID',
  `node_id` varchar(255) COLLATE utf8mb4_general_ci NOT NULL COMMENT '节点ID',
  `node_type` int(11) NOT NULL COMMENT '节点类型 0 读写 1 只读',
  `inserttime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  `updatetime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=110 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci  
```

```
 CREATE TABLE `instance_conn` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ins_id` varchar(255) COLLATE utf8mb4_general_ci NOT NULL COMMENT '实例ID',
  `connection` varchar(255) COLLATE utf8mb4_general_ci NOT NULL COMMENT '连接串',
  `connection_port` varchar(255) COLLATE utf8mb4_general_ci NOT NULL COMMENT '连接端口',
  `conn_type` int(11) NOT NULL COMMENT '0 读写 1 只读',
  `inserttime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  `updatetime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `ix_instance_conn_ins_id` (`ins_id`)
) ENGINE=InnoDB AUTO_INCREMENT=176 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci 
```

```
CREATE TABLE `instance_users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ins_id` varchar(255) COLLATE utf8mb4_general_ci NOT NULL COMMENT '实例ID',
  `username` varchar(255) COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户名',
  `max_user_connections` int(11) NOT NULL COMMENT '最大连接数',
  `inserttime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  `updatetime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `ix_instance_users_ins_id` (`ins_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1173 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci  
```


## 测试数据
```
INSERT INTO instance_list(ins_id, ins_name, ins_is_readonly, ins_type, ins_status, engine, engine_version) values (
        'rm-d9jv538yq00q451nh',
        'idn_pro_user_master_mysql',
        0,
        'rds',
        1,
        'mysql',
        '5.7'
),
(
        'pc-d9jvgnk479vd24gb3',
        'idn_pro_listing_legal_polardb',
        0,
        'polardb',
        1,
        'mysql',
        '8.0.1'
);

insert into instance_node_id (ins_id, node_id, node_type) values ('pc-d9jvgnk479vd24gb3', 'pi-d9jqi2n0529jsmox2', 0), ('pc-d9jvgnk479vd24gb3', 'pi-d9j6209gyk0630yl0', 1);
```