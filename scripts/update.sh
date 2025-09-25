#!/bin/bash
# SeleniumPelican 更新工具 - Shell 版本

echo ""
echo "🔄 SeleniumPelican 更新工具"
echo "=========================="
echo ""

echo "🔍 檢查更新環境..."

# 檢查 Git
GIT_AVAILABLE=false
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    echo "✅ Git: $GIT_VERSION"
    GIT_AVAILABLE=true
else
    echo "❌ Git 未安裝，無法執行自動更新"
fi

# 檢查是否為 Git 儲存庫
IS_GIT_REPO=false
if [ "$GIT_AVAILABLE" = true ] && [ -d ".git" ]; then
    echo "✅ Git 儲存庫: 偵測到"
    IS_GIT_REPO=true
else
    echo "❌ Git 儲存庫: 未偵測到"
fi

# 檢查 uv
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version)
    echo "✅ uv: $UV_VERSION"
else
    echo "❌ uv 未安裝，請先執行安裝程序"
    exit 1
fi

echo ""

if [ "$IS_GIT_REPO" = false ]; then
    echo "⚠️ 非 Git 儲存庫，僅執行依賴更新"
    echo ""
    
    # 步驟 1: 更新依賴
    echo "📋 步驟 1: 更新依賴套件"
    echo "⬇️ 正在執行: uv sync --upgrade"
    if uv sync --upgrade; then
        echo "✅ 依賴更新成功"
    else
        echo "❌ 依賴更新失敗"
        exit 1
    fi
else
    echo "🚀 開始執行更新程序..."
    echo ""
    
    # 步驟 1: 檢查遠端更新
    echo "📋 步驟 1: 檢查遠端更新"
    echo "🔍 正在檢查遠端更新..."
    
    if git fetch origin; then
        CURRENT_BRANCH=$(git branch --show-current)
        LOCAL_COMMIT=$(git rev-parse HEAD)
        REMOTE_COMMIT=$(git rev-parse "origin/$CURRENT_BRANCH" 2>/dev/null)
        
        if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
            echo "ℹ️ 程式碼已是最新版本"
            HAS_UPDATES=false
        else
            echo "🔄 發現遠端更新"
            HAS_UPDATES=true
        fi
    else
        echo "❌ 檢查遠端更新失敗"
        HAS_UPDATES=false
    fi
    
    # 步驟 2: 暫存本地變更
    if [ "$HAS_UPDATES" = true ]; then
        echo ""
        echo "📋 步驟 2: 處理本地變更"
        
        HAS_LOCAL_CHANGES=false
        if git status --porcelain | grep -q .; then
            echo "💾 發現本地變更，正在暫存..."
            STASH_MESSAGE="Auto-stash before update $(date '+%Y-%m-%d %H:%M:%S')"
            if git stash push -m "$STASH_MESSAGE"; then
                echo "✅ 本地變更已暫存"
                HAS_LOCAL_CHANGES=true
            else
                echo "❌ 暫存本地變更失敗"
            fi
        else
            echo "ℹ️ 無本地變更需要暫存"
        fi
        
        # 步驟 3: 執行更新
        echo ""
        echo "📋 步驟 3: 執行程式碼更新"
        echo "⬇️ 正在執行: git pull origin $CURRENT_BRANCH"
        if git pull origin "$CURRENT_BRANCH"; then
            echo "✅ 程式碼更新成功"
        else
            echo "❌ 程式碼更新失敗"
            if [ "$HAS_LOCAL_CHANGES" = true ]; then
                echo "🔄 正在還原暫存的變更..."
                git stash pop
            fi
            exit 1
        fi
        
        # 步驟 4: 還原本地變更
        if [ "$HAS_LOCAL_CHANGES" = true ]; then
            echo ""
            echo "📋 步驟 4: 還原本地變更"
            echo "🔄 正在還原暫存的變更..."
            if git stash pop; then
                echo "✅ 本地變更已還原"
            else
                echo "⚠️ 還原本地變更時發生衝突，請手動處理"
                echo "💡 使用 'git status' 查看衝突檔案"
            fi
        fi
    fi
    
    # 步驟 5: 檢查依賴更新
    echo ""
    if [ "$HAS_UPDATES" = true ]; then
        echo "📋 步驟 5: 檢查依賴更新"
    else
        echo "📋 步驟 2: 檢查依賴更新"
    fi
    
    NEEDS_DEPENDENCY_UPDATE=false
    if [ "$HAS_UPDATES" = true ]; then
        # 檢查 pyproject.toml 是否有變更
        if git diff HEAD~1 HEAD --name-only | grep -q "pyproject.toml"; then
            echo "🔄 偵測到 pyproject.toml 變更，需要更新依賴"
            NEEDS_DEPENDENCY_UPDATE=true
        else
            echo "ℹ️ pyproject.toml 無變更，跳過依賴更新"
        fi
    else
        # 無程式碼更新時，詢問是否強制更新依賴
        read -p "是否強制更新依賴套件？ (y/N): " choice
        if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
            NEEDS_DEPENDENCY_UPDATE=true
        fi
    fi
    
    if [ "$NEEDS_DEPENDENCY_UPDATE" = true ]; then
        echo "⬇️ 正在執行: uv sync --upgrade"
        if uv sync --upgrade; then
            echo "✅ 依賴更新成功"
        else
            echo "❌ 依賴更新失敗"
        fi
    fi
fi

# 最後步驟: 執行配置驗證
echo ""
echo "📋 最後步驟: 執行配置驗證"
export PYTHONPATH="$(pwd)"
export PYTHONUNBUFFERED=1
echo "🔍 正在執行配置驗證..."
if uv run python -m src.core.config_validator; then
    echo "✅ 配置驗證通過"
else
    echo "⚠️ 配置驗證發現問題，請檢查上方詳細資訊"
fi

echo ""
if [ "$HAS_UPDATES" = true ] || [ "$NEEDS_DEPENDENCY_UPDATE" = true ]; then
    echo "🎉 SeleniumPelican 更新完成！"
else
    echo "ℹ️ SeleniumPelican 已是最新狀態！"
fi

echo ""
echo "📝 建議執行的檢查："
echo "• ./Linux_配置驗證.sh - 驗證配置檔案"
echo "• 測試執行一個腳本確認功能正常"

echo ""
read -p "按 Enter 鍵繼續..."