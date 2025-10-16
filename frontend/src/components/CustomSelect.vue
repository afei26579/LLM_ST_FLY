<template>
  <div class="custom-select" ref="selectRef">
    <button 
      class="select-trigger" 
      @click="toggleDropdown"
      :class="{ 'is-open': isOpen }"
      type="button"
    >
      <span class="selected-text">{{ displayText }}</span>
      <svg 
        class="dropdown-icon" 
        :class="{ 'rotated': isOpen }"
        xmlns="http://www.w3.org/2000/svg" 
        width="16" 
        height="16" 
        viewBox="0 0 24 24" 
        fill="none" 
        stroke="currentColor" 
        stroke-width="2" 
        stroke-linecap="round" 
        stroke-linejoin="round"
      >
        <polyline points="6,9 12,15 18,9"></polyline>
      </svg>
    </button>
    
    <transition name="dropdown">
      <div v-if="isOpen" class="select-dropdown">
        <div class="dropdown-content">
          <div 
            v-for="option in options" 
            :key="option.value"
            class="dropdown-item"
            :class="{ 'active': modelValue === option.value }"
            @click="selectOption(option.value)"
          >
            {{ option.label }}
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface SelectOption {
  value: string
  label: string
}

interface Props {
  modelValue: string
  options: SelectOption[]
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '请选择'
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const isOpen = ref(false)
const selectRef = ref<HTMLElement>()

const displayText = computed(() => {
  const selectedOption = props.options.find(opt => opt.value === props.modelValue)
  return selectedOption ? selectedOption.label : props.placeholder
})

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

const selectOption = (value: string) => {
  emit('update:modelValue', value)
  isOpen.value = false
}

// 点击外部关闭下拉
const handleClickOutside = (event: MouseEvent) => {
  if (selectRef.value && !selectRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.custom-select {
  position: relative;
  width: 100%;
}

.select-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--card-background);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: var(--card-shadow);
  text-align: left;
}

.select-trigger:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-alpha);
}

.select-trigger.is-open {
  border-color: var(--color-primary);
  box-shadow: var(--card-shadow), 0 0 0 2px rgba(94, 155, 255, 0.1);
}

.selected-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-icon {
  flex-shrink: 0;
  transition: transform 0.3s ease;
}

.dropdown-icon.rotated {
  transform: rotate(180deg);
}

.select-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  left: 0;
  right: 0;
  z-index: 1000;
  background: var(--card-background);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  box-shadow: var(--card-shadow);
  max-height: 300px;
  overflow-y: auto;
}

.dropdown-content {
  padding: 0.5rem;
}

.dropdown-item {
  padding: 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
  color: var(--color-text);
  font-size: 1rem;
  margin-bottom: 0.25rem;
}

.dropdown-item:hover {
  background: var(--color-primary-alpha);
}

.dropdown-item.active {
  background: var(--color-primary-alpha);
  color: var(--color-primary);
  font-weight: 500;
}

/* 下拉动画 */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 自定义滚动条 */
.select-dropdown::-webkit-scrollbar {
  width: 8px;
}

.select-dropdown::-webkit-scrollbar-track {
  background: var(--input-background);
  border-radius: 4px;
}

.select-dropdown::-webkit-scrollbar-thumb {
  background: var(--color-primary-alpha);
  border-radius: 4px;
  transition: background 0.3s ease;
}

.select-dropdown::-webkit-scrollbar-thumb:hover {
  background: var(--color-primary);
}

/* Firefox 滚动条 */
.select-dropdown {
  scrollbar-width: thin;
  scrollbar-color: var(--color-primary-alpha) var(--input-background);
}
</style>

