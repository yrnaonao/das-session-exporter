from sqlalchemy.orm import Session
from models.instance import AliyunAccount
from utils.encryption import encrypt_string


def add_aliyun_account(
    db: Session,
    aliyun_uid: str,
    aliyun_name: str,
    access_key_id: str,
    access_key_secret: str,
    region_id: str = 'cn-shanghai',
    status: int = 1
) -> AliyunAccount:
    """
    添加阿里云账号到数据库
    """
    # 加密Access Key Secret
    encrypted_secret = encrypt_string(access_key_secret)
    
    # 创建账号记录
    account = AliyunAccount(
        aliyun_uid=aliyun_uid,
        aliyun_name=aliyun_name,
        access_key_id=access_key_id,
        encrypted_access_key_secret=encrypted_secret,
        region_id=region_id,
        status=status
    )
    
    # 检查是否已存在该账号
    existing_account = db.query(AliyunAccount).filter(
        AliyunAccount.aliyun_uid == aliyun_uid
    ).first()
    
    if existing_account:
        # 更新现有账号
        existing_account.access_key_id = access_key_id
        existing_account.encrypted_access_key_secret = encrypted_secret
        existing_account.region_id = region_id
        existing_account.aliyun_name = aliyun_name
        existing_account.status = status
        db.commit()
        db.refresh(existing_account)
        return existing_account
    else:
        # 添加新账号
        db.add(account)
        db.commit()
        db.refresh(account)
        return account


def get_aliyun_account(db: Session, aliyun_uid: str) -> AliyunAccount:
    """
    获取阿里云账号信息
    """
    return db.query(AliyunAccount).filter(
        AliyunAccount.aliyun_uid == aliyun_uid
    ).first()


def delete_aliyun_account(db: Session, aliyun_uid: str) -> bool:
    """
    删除阿里云账号
    """
    account = db.query(AliyunAccount).filter(
        AliyunAccount.aliyun_uid == aliyun_uid
    ).first()
    
    if account:
        db.delete(account)
        db.commit()
        return True
    
    return False


def list_aliyun_accounts(db: Session) -> list:
    """
    列出所有阿里云账号
    """
    return db.query(AliyunAccount).all()