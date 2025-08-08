<template>
  <div v-if="isOpen" class="modal-overlay">
    <div class="modal-container" :class="{ 'wide': wide }">
      <div class="modal-header">
        <h3>{{ title }}</h3>
        <button class="close-btn" @click="close">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      <div class="modal-content">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  wide: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['close']);

const close = () => {
  emit('close');
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background-color: #1e293b;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  width: 500px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  animation: modal-appear 0.3s ease-out;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-container.wide {
  width: 700px;
}

@keyframes modal-appear {
  0% {
    opacity: 0;
    transform: translateY(-30px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h3 {
  color: #e1e6f5;
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.close-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: #e1e6f5;
}

.modal-content {
  padding: 1.5rem;
}
</style>

<style>
/* 在全局范围内注册通用样式，以便在子组件中使用 */
.tabs {
  display: flex;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.tab {
  padding: 0.75rem 1rem;
  cursor: pointer;
  color: #94a3b8;
  font-weight: 500;
  transition: all 0.2s;
  position: relative;
}

.tab:hover {
  color: #e1e6f5;
}

.tab.active {
  color: #5e9bff;
}

.tab.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, #5e9bff 0%, #a569ff 100%);
  border-radius: 2px 2px 0 0;
}

.form-group {
  margin-bottom: 1.25rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #e1e6f5;
  font-weight: 500;
}

input {
  width: 100%;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background-color: rgba(255, 255, 255, 0.05);
  color: #e1e6f5;
  transition: border-color 0.2s;
  font-size: 1rem;
}

input:focus {
  outline: none;
  border-color: #5e9bff;
  box-shadow: 0 0 0 3px rgba(94, 155, 255, 0.2);
}

.error-message {
  color: #f87171;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.form-hint {
  color: #94a3b8;
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 1.5rem;
}

.primary-btn {
  background: linear-gradient(90deg, #5e9bff 0%, #a569ff 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.primary-btn:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
}

.primary-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.secondary-btn {
  background: rgba(255, 255, 255, 0.1);
  color: #e1e6f5;
  border: none;
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.secondary-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.15);
}

.secondary-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.cancel-btn {
  background: transparent;
  color: #94a3b8;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #e1e6f5;
}
</style> 