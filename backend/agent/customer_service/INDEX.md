# 📖 智能客服系统 - 文档索引

欢迎使用智能客服系统！这里是所有文档的导航索引。

---

## 🚀 快速开始（推荐阅读顺序）

### 1️⃣ 新用户入门
- **[QUICKSTART.md](./QUICKSTART.md)** - 5分钟快速上手指南
  - 环境准备
  - 启动服务
  - 测试对话

### 2️⃣ 知识库功能
- **[QUICK_SETUP.md](./QUICK_SETUP.md)** - 知识库功能快速设置
  - 安装pgvector
  - 配置PostgreSQL
  - 测试向量检索

### 3️⃣ 详细使用
- **[USAGE_EXAMPLES.md](./USAGE_EXAMPLES.md)** - 实用代码示例
  - 创建知识库
  - 处理文档
  - 配置助手
  - API调用

---

## 📚 技术文档

### 完整技术文档
- **[README.md](./README.md)** - 完整技术文档（562行）
  - 功能特性
  - 系统架构
  - API文档
  - 工作流详解
  - 配置说明
  - 扩展开发

### 知识库技术详解
- **[KNOWLEDGE_BASE_IMPLEMENTATION.md](./KNOWLEDGE_BASE_IMPLEMENTATION.md)**
  - 功能概述
  - 数据库设计
  - 核心服务说明
  - API接口
  - 性能优化
  - 故障排查

---

## 📋 实施总结

### 基础功能总结
- **[项目根目录/CUSTOMER_SERVICE_IMPLEMENTATION.md](../../../CUSTOMER_SERVICE_IMPLEMENTATION.md)**
  - 已完成功能
  - 文件清单
  - 架构设计
  - 代码统计

### 知识库功能总结
- **[项目根目录/CUSTOMER_SERVICE_KNOWLEDGE_BASE_SUMMARY.md](../../../CUSTOMER_SERVICE_KNOWLEDGE_BASE_SUMMARY.md)**
  - 核心功能清单
  - 实施步骤
  - 待完成任务

### 完整总结
- **[项目根目录/CUSTOMER_SERVICE_COMPLETE_SUMMARY.md](../../../CUSTOMER_SERVICE_COMPLETE_SUMMARY.md)**
  - 完整功能清单
  - 安装部署
  - 使用指南
  - 7000行代码统计

---

## 🎯 快速参考

### 速查手册
- **[项目根目录/CUSTOMER_SERVICE_QUICK_REFERENCE.md](../../../CUSTOMER_SERVICE_QUICK_REFERENCE.md)**
  - 快速导航
  - 文件位置
  - 常用命令
  - 配置参数
  - FAQ

---

## 🗃️ 配置文件

### 依赖清单
- **[requirements_extended.txt](./requirements_extended.txt)**
  - pgvector
  - openai
  - PyPDF2
  - python-docx

---

## 📊 文档统计

### 文档类型
- 快速指南: 3个
- 技术文档: 2个
- 实施总结: 3个
- 使用示例: 1个
- 索引导航: 1个（本文档）

### 总文档量
- **~3000行** Markdown文档
- 覆盖安装、配置、使用、开发全流程

---

## 🎯 按需求查找

### 我想要...

**快速上手**
→ [QUICKSTART.md](./QUICKSTART.md)

**设置知识库**
→ [QUICK_SETUP.md](./QUICK_SETUP.md)

**查看代码示例**
→ [USAGE_EXAMPLES.md](./USAGE_EXAMPLES.md)

**了解技术细节**
→ [README.md](./README.md)

**查看实施进度**
→ [CUSTOMER_SERVICE_COMPLETE_SUMMARY.md](../../../CUSTOMER_SERVICE_COMPLETE_SUMMARY.md)

**快速查询配置**
→ [CUSTOMER_SERVICE_QUICK_REFERENCE.md](../../../CUSTOMER_SERVICE_QUICK_REFERENCE.md)

---

## 🔗 相关链接

### 外部资源
- [LangGraph文档](https://python.langchain.com/docs/langgraph)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [DashScope API](https://help.aliyun.com/zh/dashscope/)

### 项目文档
- [开发指导](../../../开发指导.md)
- [主题适配文档](../../../frontend/src/views/agent/customer-service/THEME_UPDATE.md)

---

## 🆘 获取帮助

### 问题排查顺序
1. 查看 [QUICKSTART.md](./QUICKSTART.md) FAQ部分
2. 查看 [README.md](./README.md) 故障排查章节
3. 查看Django日志
4. 提交Issue

### 常见问题快速链接
- [pgvector安装问题](./QUICK_SETUP.md#q1-pgvector扩展安装失败)
- [向量检索无结果](./QUICK_SETUP.md#q2-向量检索无结果)
- [API Key配置](./QUICK_SETUP.md#q3-api-key配置问题)
- [文档上传失败](./QUICK_SETUP.md#q4-文档上传失败)

---

## 📅 版本历史

### v2.0 (2025-10-22)
- ✅ 添加知识库管理功能
- ✅ 添加助手自定义功能
- ✅ 集成pgvector向量数据库
- ✅ 实现混合检索
- ✅ 创建管理中心界面

### v1.0 (2025-10-22)
- ✅ 基础对话功能
- ✅ LangGraph工作流
- ✅ 意图识别和路由
- ✅ 会话管理
- ✅ 主题适配

---

## 🎓 推荐学习路径

### 第1天：快速体验
- ⏱️ 30分钟 - 阅读QUICKSTART.md并启动系统
- ⏱️ 30分钟 - 创建知识库和助手
- ⏱️ 30分钟 - 测试对话功能

### 第2天：深入理解
- ⏱️ 1小时 - 阅读完整技术文档
- ⏱️ 1小时 - 学习LangGraph工作流
- ⏱️ 1小时 - 了解向量检索原理

### 第3天：高级应用
- ⏱️ 2小时 - 研究代码实现
- ⏱️ 2小时 - 自定义开发
- ⏱️ 1小时 - 性能优化

---

## ✅ 检查清单

### 安装完成
- [ ] pgvector扩展已安装
- [ ] Python依赖已安装
- [ ] 数据库迁移已执行
- [ ] 向量索引已创建

### 功能测试
- [ ] 创建知识库成功
- [ ] 上传文档成功
- [ ] 向量检索有结果
- [ ] 创建助手成功
- [ ] 对话功能正常

### 性能检查
- [ ] 响应时间 < 2秒
- [ ] 向量检索 < 100ms
- [ ] 文档处理无错误
- [ ] 内存占用正常

---

**🎉 欢迎使用智能客服系统！**

有任何问题，请查阅相关文档或联系支持。

---

*最后更新: 2025-10-22*  
*维护者: LLM ST FLY Team*

