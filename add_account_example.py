"""
添加阿里云账号示例
"""
import os
import sys
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import engine, Base
from utils.account_manager import add_aliyun_account
from models.instance import AliyunAccount
from utils.encryption import encrypt_string, decrypt_string


def create_tables():
    """创建数据库表"""
    Base.metadata.create_all(bind=engine)


def add_sample_account():
    """添加示例账号"""
    # 创建数据库会话
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 示例：添加阿里云账号
        aliyun_uid = "1234567890123456"
        access_key_id = "your_access_key_id_here"
        access_key_secret = "your_access_key_secret_here"
        region_id = "cn-shanghai"
        
        print(f"正在添加阿里云账号: {aliyun_uid}")
        
        # 添加账号到数据库
        account = add_aliyun_account(
            db=db,
            aliyun_uid=aliyun_uid,
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            region_id=region_id
        )
        
        print(f"账号添加成功！ID: {account.id}, UID: {account.aliyun_uid}")
        print(f"Access Key ID: {account.access_key_id}")
        print(f"加密的Secret: {account.encrypted_access_key_secret[:50]}...")  # 只显示前50个字符
        print(f"区域: {account.region_id}")
        
        # 验证解密功能
        decrypted_secret = decrypt_string(account.encrypted_access_key_secret)
        print(f"解密验证成功: {decrypted_secret == access_key_secret}")
        
    finally:
        db.close()


if __name__ == "__main__":
    create_tables()
    add_sample_account()