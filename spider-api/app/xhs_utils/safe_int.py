# 辅助函数：安全地将值转换为整数
def safe_int(value, default=0):
    """
    安全地将值转换为整数，支持中文数字格式（如 "2.7万"）
    :param value: 要转换的值（可能是 int, str, None 等）
    :param default: 转换失败时的默认值
    :return: 整数值
    """
    if value is None:
        return default
    
    try:
        # 如果已经是整数，直接返回
        if isinstance(value, int):
            return value
        
        # 如果是字符串，处理中文数字格式
        if isinstance(value, str):
            value = value.strip()
            
            # 处理空字符串
            if not value:
                return default
            
            # 处理包含"万"的情况（如 "2.7万" = 27000）
            if '万' in value:
                num_str = value.replace('万', '').strip()
                try:
                    # 转换为浮点数再乘以10000
                    return int(float(num_str) * 10000)
                except ValueError:
                    return default
            
            # 处理包含"千"的情况（如果有的话）
            if '千' in value:
                num_str = value.replace('千', '').strip()
                try:
                    return int(float(num_str) * 1000)
                except ValueError:
                    return default
            
            # 普通数字字符串
            return int(float(value))
        
        # 其他类型尝试直接转换
        return int(value)
        
    except (ValueError, TypeError):
        return defaul