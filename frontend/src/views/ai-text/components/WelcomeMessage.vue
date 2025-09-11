<template>
  <div class="welcome-message">
    <div class="welcome-card">
      <h2>{{ greeting }}，{{ userDisplayName }}，欢迎使用AI助手</h2>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  userDisplayName: string
  greeting: string
}

const props = defineProps<Props>()
</script>

<style scoped>
.welcome-message {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  animation: fade-in 0.5s ease-out;
}

.welcome-card {
  text-align: center;
  padding: 2rem;
  background-color: transparent;
  border-radius: 0.75rem;
  max-width: 80%;
}

.welcome-card h2 {
  margin: 0;
  color: var(--color-text, #334155);
  font-size: 2rem;
  font-weight: 600;
}

@keyframes fade-in {
  from { 
    opacity: 0; 
    transform: translateY(10px); 
  }
  to { 
    opacity: 1; 
    transform: translateY(0); 
  }
}

@media (max-width: 768px) {
  .welcome-card {
    max-width: 95%;
    padding: 1.5rem;
  }
  
  .welcome-card h2 {
    font-size: 1.5rem;
  }
}
</style>