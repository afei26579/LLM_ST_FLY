<template>
  <div class="empty-assistant-view">
    <div class="empty-content">
      <div class="empty-icon">🤖</div>
      <h2>还没有智能助手</h2>
      <p class="empty-subtitle">创建您的第一个智能客服助手，开始提供优质服务</p>
      
      <div class="setup-guide">
        <div class="guide-step">
          <div class="step-number">1</div>
          <div class="step-info">
            <h3>准备知识库</h3>
            <p>上传文档构建知识库，让助手拥有专业知识</p>
          </div>
          <div class="step-status" :class="{ completed: hasKnowledgeBase }">
            <span v-if="hasKnowledgeBase">✅ 已完成</span>
            <span v-else>待完成</span>
          </div>
        </div>
        
        <div class="guide-arrow">↓</div>
        
        <div class="guide-step">
          <div class="step-number">2</div>
          <div class="step-info">
            <h3>创建助手</h3>
            <p>配置助手参数，设置专属对话风格</p>
          </div>
          <div class="step-status">
            待完成
          </div>
        </div>
        
        <div class="guide-arrow">↓</div>
        
        <div class="guide-step">
          <div class="step-number">3</div>
          <div class="step-info">
            <h3>开始对话</h3>
            <p>测试和使用您的智能助手</p>
          </div>
          <div class="step-status">
            待完成
          </div>
        </div>
      </div>

      <div class="action-buttons">
        <button
          v-if="!hasKnowledgeBase"
          @click="$emit('create-kb')"
          class="btn-action-primary"
        >
          <span class="btn-icon">📚</span>
          <div class="btn-text">
            <strong>创建知识库</strong>
            <small>第一步：上传文档构建知识库</small>
          </div>
        </button>
        <button
          v-else
          @click="$emit('create-assistant')"
          class="btn-action-primary"
        >
          <span class="btn-icon">🤖</span>
          <div class="btn-text">
            <strong>创建助手</strong>
            <small>第二步：配置您的智能助手</small>
          </div>
        </button>
      </div>

      <div class="tips-box">
        <div class="tip-icon">💡</div>
        <div class="tip-content">
          <strong>提示：</strong>您可以创建多个助手，每个助手可以关联多个知识库，满足不同场景需求
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  hasKnowledgeBase: boolean
}>()

defineEmits<{
  'create-kb': []
  'create-assistant': []
}>()
</script>

<style scoped>
.empty-assistant-view {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  background: var(--color-surface);
  padding: 40px;
  margin: 16px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  box-shadow: var(--card-shadow);
}

.empty-content {
  max-width: 600px;
  width: 100%;
  text-align: center;
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 24px;
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.empty-content h2 {
  margin: 0 0 12px;
  font-size: 28px;
  font-weight: 600;
  color: var(--color-text);
}

.empty-subtitle {
  margin: 0 0 48px;
  font-size: 16px;
  color: var(--color-text-secondary);
}

.setup-guide {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 48px;
}

.guide-step {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--color-background);
  border: 2px solid var(--color-border);
  border-radius: 12px;
  text-align: left;
  transition: all 0.3s;
}

.guide-step:hover {
  border-color: var(--button-primary);
  transform: translateX(4px);
}

.step-number {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--color-primary-alpha);
  color: var(--button-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
  flex-shrink: 0;
}

.step-info {
  flex: 1;
}

.step-info h3 {
  margin: 0 0 4px;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
}

.step-info p {
  margin: 0;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.step-status {
  padding: 6px 16px;
  background: var(--color-background);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.step-status.completed {
  background: var(--color-success, #10b981);
  color: white;
}

.guide-arrow {
  font-size: 32px;
  color: var(--color-text-secondary);
  opacity: 0.5;
  margin: -8px 0;
}

.action-buttons {
  margin-bottom: 32px;
}

.btn-action-primary {
  display: inline-flex;
  align-items: center;
  gap: 16px;
  padding: 20px 40px;
  background: var(--button-primary);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(94, 155, 255, 0.3);
}

.btn-action-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(94, 155, 255, 0.4);
}

.btn-icon {
  font-size: 40px;
}

.btn-text {
  text-align: left;
}

.btn-text strong {
  display: block;
  font-size: 18px;
  margin-bottom: 4px;
}

.btn-text small {
  display: block;
  font-size: 13px;
  opacity: 0.9;
  font-weight: normal;
}

.tips-box {
  display: inline-flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 24px;
  background: var(--color-primary-alpha);
  border-radius: 12px;
  border-left: 3px solid var(--button-primary);
  max-width: 100%;
}

.tip-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.tip-content {
  text-align: left;
  font-size: 14px;
  color: var(--color-text);
  line-height: 1.6;
}

.tip-content strong {
  color: var(--button-primary);
}
</style>

