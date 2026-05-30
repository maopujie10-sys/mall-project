#!/bin/bash
# RAG知识库依赖安装脚本
# 运行: bash install_rag.sh

echo "=== Friday AI RAG 知识库依赖安装 ==="

# 安装chromadb (向量数据库)
echo "[1/2] 安装 chromadb..."
pip install chromadb

# 安装sentence-transformers (语义嵌入模型)
echo "[2/2] 安装 sentence-transformers..."
pip install sentence-transformers

echo ""
echo "=== 安装完成 ==="
echo "RAG知识库现在支持:"
echo "  - ChromaDB 向量存储"
echo "  - Sentence-Transformers 语义嵌入"
echo "  - 混合检索 (向量+关键词)"
echo ""
echo "如安装失败，RAG会自动降级为hash嵌入+关键词检索模式"