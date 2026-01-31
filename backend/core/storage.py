"""
Storage Service 抽象层
支持本地存储和S3兼容存储
"""

from abc import ABC, abstractmethod
from typing import BinaryIO, Optional
from pathlib import Path
import os

from core.config import settings


class StorageBackend(ABC):
    """存储后端抽象基类"""
    
    @abstractmethod
    async def upload(self, key: str, data: BinaryIO, content_type: str = "application/octet-stream") -> str:
        """
        上传文件
        
        Args:
            key: 文件唯一标识（路径）
            data: 文件数据流
            content_type: MIME类型
            
        Returns:
            访问URL
        """
        pass
    
    @abstractmethod
    async def download(self, key: str) -> bytes:
        """
        下载文件
        
        Args:
            key: 文件唯一标识
            
        Returns:
            文件字节数据
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        删除文件
        
        Args:
            key: 文件唯一标识
            
        Returns:
            是否删除成功
        """
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """检查文件是否存在"""
        pass


class LocalStorage(StorageBackend):
    """本地文件系统存储（开发环境）"""
    
    def __init__(self, base_dir: str = "/tmp/xhs_storage"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    async def upload(self, key: str, data: BinaryIO, content_type: str = "application/octet-stream") -> str:
        file_path = self.base_dir / key
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(data.read())
        
        return f"file://{file_path}"
    
    async def download(self, key: str) -> bytes:
        file_path = self.base_dir / key
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {key}")
        
        with open(file_path, 'rb') as f:
            return f.read()
    
    async def delete(self, key: str) -> bool:
        file_path = self.base_dir / key
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    async def exists(self, key: str) -> bool:
        return (self.base_dir / key).exists()


class S3Storage(StorageBackend):
    """S3兼容存储（生产环境）"""
    
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket: str):
        try:
            import boto3
            self.client = boto3.client(
                's3',
                endpoint_url=endpoint,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key
            )
            self.bucket = bucket
        except ImportError:
            raise ImportError("请安装 boto3: pip install boto3")
    
    async def upload(self, key: str, data: BinaryIO, content_type: str = "application/octet-stream") -> str:
        self.client.upload_fileobj(
            data,
            self.bucket,
            key,
            ExtraArgs={'ContentType': content_type}
        )
        return f"https://{self.bucket}.s3.amazonaws.com/{key}"
    
    async def download(self, key: str) -> bytes:
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return response['Body'].read()
    
    async def delete(self, key: str) -> bool:
        self.client.delete_object(Bucket=self.bucket, Key=key)
        return True
    
    async def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except:
            return False


# 工厂函数
def get_storage() -> StorageBackend:
    """获取存储后端实例（根据环境变量）"""
    storage_type = getattr(settings, 'STORAGE_TYPE', 'local')
    
    if storage_type == 's3':
        return S3Storage(
            endpoint=settings.S3_ENDPOINT,
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            bucket=settings.S3_BUCKET
        )
    
    # 默认使用本地存储
    storage_dir = getattr(settings, 'STORAGE_DIR', '/tmp/xhs_storage')
    return LocalStorage(storage_dir)


# 全局存储实例
storage = get_storage()
