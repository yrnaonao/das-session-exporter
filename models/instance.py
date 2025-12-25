from sqlalchemy import Column, Integer, String, DateTime, text
from models.database import Base


class InstanceList(Base):
    """
    实例列表表
    """
    __tablename__ = "instance_list"

    id = Column(Integer, primary_key=True, index=True)
    ins_id = Column(String(255), nullable=False, index=True, comment='实例ID')
    ins_name = Column(String(255), nullable=False, comment='实例名')
    ins_is_readonly = Column(Integer, nullable=False, comment='是否为只读 1只读 0读写')
    ins_type = Column(String(255), nullable=False, comment='实例类型 PolarDB RDS Mongodb')
    ins_status = Column(Integer, nullable=False, comment='实例状态 0 禁用 1 启用')
    engine = Column(String(255), nullable=False, comment='数据库引擎 mysql mongodb')
    engine_version = Column(String(255), nullable=False, comment='引擎版本 5.7 8.0')
    master_id = Column(String(255), comment='主库ID，从库才有的属性， RDS才有')
    aliyun_uid = Column(String(255), nullable=False, index=True, comment='阿里云账号ID')
    inserttime = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), comment='插入时间')
    updatetime = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), 
                       onupdate=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')


class InstanceNodeId(Base):
    """
    实例节点ID表 (PolarDB)
    """
    __tablename__ = "instance_node_id"

    id = Column(Integer, primary_key=True, index=True)
    ins_id = Column(String(255), nullable=False, comment='实例ID')
    node_id = Column(String(255), nullable=False, comment='节点ID')
    node_type = Column(Integer, nullable=False, comment='节点类型 0 读写 1 只读')
    inserttime = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), comment='插入时间')
    updatetime = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), 
                       onupdate=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')


class InstanceConn(Base):
    """
    实例连接信息表
    """
    __tablename__ = "instance_conn"

    id = Column(Integer, primary_key=True, index=True)
    ins_id = Column(String(255), nullable=False, index=True, comment='实例ID')
    connection = Column(String(255), nullable=False, comment='连接串')
    connection_port = Column(String(255), nullable=False, comment='连接端口')
    conn_type = Column(Integer, nullable=False, comment='0 读写 1 只读')
    inserttime = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), comment='插入时间')
    updatetime = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), 
                       onupdate=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')


class InstanceUsers(Base):
    """
    实例用户最大连接数表
    """
    __tablename__ = "instance_users"

    id = Column(Integer, primary_key=True, index=True)
    ins_id = Column(String(255), nullable=False, index=True, comment='实例ID')
    username = Column(String(255), nullable=False, comment='用户名')
    max_user_connections = Column(Integer, nullable=False, comment='最大连接数')
    inserttime = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), comment='插入时间')
    updatetime = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), 
                       onupdate=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')


class AliyunAccount(Base):
    """
    阿里云账号配置表
    """
    __tablename__ = "aliyun_uids"

    id = Column(Integer, primary_key=True, index=True)
    aliyun_uid = Column(String(255), nullable=False, unique=True, comment='阿里云账号ID')
    aliyun_name = Column(String(255), nullable=False, comment='阿里云账号名称')
    access_key_id = Column(String(255), nullable=False, comment='Access Key ID')
    encrypted_access_key_secret = Column(String(255), nullable=False, comment='加密的Access Key Secret')
    region_id = Column(String(255), default='cn-shanghai', comment='区域ID')
    status = Column(Integer, default=1, comment='状态 0禁用 1启用')
    inserttime = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), comment='插入时间')
    updatetime = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), 
                       onupdate=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')