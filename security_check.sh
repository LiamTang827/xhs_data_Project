#!/bin/bash
# 安全检查脚本 - 上传 GitHub 前执行

echo "🔍 开始安全检查..."
echo ""

ERRORS=0
WARNINGS=0

# 1. 检查 .gitignore 是否存在
echo "1️⃣ 检查 .gitignore 文件..."
if [ ! -f .gitignore ]; then
    echo "   ❌ 错误: .gitignore 文件不存在"
    ERRORS=$((ERRORS + 1))
else
    echo "   ✅ .gitignore 已存在"
fi

# 2. 检查 .env 文件是否被追踪
echo ""
echo "2️⃣ 检查 .env 文件..."
if git ls-files 2>/dev/null | grep -q "\.env$"; then
    echo "   ❌ 错误: .env 文件在 git 追踪中！必须移除！"
    echo "      执行: git rm --cached .env"
    ERRORS=$((ERRORS + 1))
else
    echo "   ✅ .env 文件未被追踪"
fi

# 3. 检查 .env.example 是否存在
echo ""
echo "3️⃣ 检查配置模板..."
if [ ! -f .env.example ]; then
    echo "   ⚠️  警告: .env.example 不存在"
    WARNINGS=$((WARNINGS + 1))
else
    echo "   ✅ .env.example 已存在"
fi

# 4. 检查代码中的 API Keys
echo ""
echo "4️⃣ 扫描硬编码的 API Keys..."
if grep -r "sk-[a-zA-Z0-9]\{32,\}" --include="*.py" --exclude-dir=".venv" . 2>/dev/null | grep -v ".env.example" | grep -v "SECURITY_GUIDE.md"; then
    echo "   ❌ 错误: 发现可能的 DeepSeek API Key！"
    ERRORS=$((ERRORS + 1))
else
    echo "   ✅ 未发现 API Key"
fi

# 5. 检查 MongoDB 连接字符串
echo ""
echo "5️⃣ 扫描 MongoDB 凭据..."
if grep -r "mongodb+srv://[^:]*:[^@]*@" --include="*.py" --include="*.sh" --exclude-dir=".venv" . 2>/dev/null | grep -v ".env.example" | grep -v "SECURITY_GUIDE.md"; then
    echo "   ❌ 错误: 发现 MongoDB 凭据！"
    ERRORS=$((ERRORS + 1))
else
    echo "   ✅ 未发现 MongoDB 凭据"
fi

# 6. 检查 TikHub Token
echo ""
echo "6️⃣ 扫描 TikHub Token..."
if grep -r "Bearer [a-zA-Z0-9+/=]\{40,\}" --include="*.py" --exclude-dir=".venv" . 2>/dev/null | grep -v ".env.example" | grep -v "SECURITY_GUIDE.md"; then
    echo "   ❌ 错误: 发现 TikHub Token！"
    ERRORS=$((ERRORS + 1))
else
    echo "   ✅ 未发现 TikHub Token"
fi

# 7. 检查虚拟环境是否被追踪
echo ""
echo "7️⃣ 检查虚拟环境..."
if git ls-files 2>/dev/null | grep -q "\.venv/"; then
    echo "   ⚠️  警告: .venv/ 目录在 git 追踪中"
    WARNINGS=$((WARNINGS + 1))
else
    echo "   ✅ .venv/ 未被追踪"
fi

# 8. 检查 __pycache__ 是否被追踪
echo ""
echo "8️⃣ 检查 Python 缓存..."
if git ls-files 2>/dev/null | grep -q "__pycache__"; then
    echo "   ⚠️  警告: __pycache__ 在 git 追踪中"
    WARNINGS=$((WARNINGS + 1))
else
    echo "   ✅ __pycache__ 未被追踪"
fi

# 9. 检查 data 目录的敏感文件
echo ""
echo "9️⃣ 检查数据文件..."
if [ -d data-analysiter/data ]; then
    SENSITIVE_FILES=$(find data-analysiter/data -name "*.json" -type f 2>/dev/null | wc -l)
    if [ $SENSITIVE_FILES -gt 0 ]; then
        echo "   ⚠️  警告: 发现 $SENSITIVE_FILES 个 JSON 数据文件"
        echo "      请确认这些文件不包含敏感信息"
        WARNINGS=$((WARNINGS + 1))
    else
        echo "   ✅ 未发现数据文件"
    fi
else
    echo "   ℹ️  data 目录不存在"
fi

# 10. 检查是否有本地配置文件
echo ""
echo "🔟 检查本地配置..."
LOCAL_CONFIGS=(.env .env.local data-analysiter/.env tikhub-data-collector/.env)
LOCAL_EXISTS=false
for config in "${LOCAL_CONFIGS[@]}"; do
    if [ -f "$config" ]; then
        LOCAL_EXISTS=true
        if git ls-files 2>/dev/null | grep -q "^$config$"; then
            echo "   ❌ 错误: $config 在 git 追踪中！"
            ERRORS=$((ERRORS + 1))
        fi
    fi
done

if $LOCAL_EXISTS; then
    echo "   ✅ 本地配置文件存在且未被追踪"
else
    echo "   ℹ️  未发现本地配置文件（正常，用户需自行创建）"
fi

# 总结
echo ""
echo "================================================"
echo "📊 检查结果汇总"
echo "================================================"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ 完美！所有检查通过，可以安全上传到 GitHub"
    echo ""
    echo "下一步:"
    echo "  git add ."
    echo "  git commit -m \"Initial commit: XHS Data Analysis Platform\""
    echo "  git push origin main"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  发现 $WARNINGS 个警告，但可以上传"
    echo ""
    echo "建议先处理警告，或者确认无问题后继续"
    exit 0
else
    echo "❌ 发现 $ERRORS 个错误，$WARNINGS 个警告"
    echo ""
    echo "必须先修复所有错误才能上传！"
    echo "详细信息请参考: SECURITY_GUIDE.md"
    exit 1
fi
