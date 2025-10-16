<script setup lang="ts">
import { ref, onMounted } from 'vue';

// Telegram WebApp integration
const tgUser = ref<any | null>(null);
const tgReady = ref(false);

onMounted(() => {
  // @ts-ignore
  if (window.Telegram && window.Telegram.WebApp) {
    // @ts-ignore
    const webApp = window.Telegram.WebApp;
    tgUser.value = webApp.initDataUnsafe?.user || null;
    tgReady.value = true;
    webApp.ready();
  }
});
</script>

<template>
  <nav>
    <router-link to="/">Home</router-link> |
    <router-link to="/profile">Profile</router-link> |
    <router-link to="/subscriptions">Subscriptions</router-link> |
    <router-link to="/calendar">Calendar</router-link> |
    <router-link to="/macros">Macros</router-link> |
    <router-link to="/chatbot">Chatbot</router-link> |
    <router-link to="/trainer-dashboard">Trainer Dashboard</router-link>
  </nav>
  <div v-if="tgReady && tgUser">
    <p>Welcome, {{ tgUser.first_name }} {{ tgUser.last_name }} (ID: {{ tgUser.id }})</p>
  </div>
  <router-view />
</template>

<style scoped>
nav {
  margin-bottom: 1rem;
}
nav a {
  margin-right: 0.5rem;
  text-decoration: none;
  color: #42b983;
}
nav a.router-link-exact-active {
  font-weight: bold;
  color: #35495e;
}
</style>
