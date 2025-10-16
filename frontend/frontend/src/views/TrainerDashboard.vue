<template>
  <div>
    <h2>Trainer Dashboard</h2>
    <div v-if="loading">Loading...</div>
    <div v-else>
      <div>
        <strong>Clients:</strong> {{ summary.client_count }}<br />
        <strong>Visits:</strong> {{ summary.visit_count }}<br />
        <strong>Food Logs:</strong> {{ summary.foodlog_count }}
      </div>
      <h3>Client List</h3>
      <ul>
        <li v-for="client in clients" :key="client.id">
          {{ client.goal }} (ID: {{ client.id }})
          <button @click="viewProgress(client.id)">View Progress</button>
        </li>
      </ul>
      <div v-if="progress">
        <h4>Progress for Client {{ progressClientId }}</h4>
        <div>Calories: {{ progress.total_calories }}</div>
        <div>Protein: {{ progress.total_protein }}</div>
        <div>Fat: {{ progress.total_fat }}</div>
        <div>Carbs: {{ progress.total_carbs }}</div>
        <div>Days Logged: {{ progress.days_logged }}</div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue';

const trainerId = 1; // TODO: Replace with actual trainer ID from auth/session
const clients = ref<any[]>([]);
const summary = ref({ client_count: 0, visit_count: 0, foodlog_count: 0 });
const loading = ref(true);
const progress = ref<any | null>(null);
const progressClientId = ref<number | null>(null);

async function fetchClients() {
  const res = await fetch(`/api/v1/clients?trainer_id=${trainerId}`);
  clients.value = await res.json();
}

async function fetchSummary() {
  const res = await fetch(`/api/v1/reports/summary?trainer_id=${trainerId}`);
  summary.value = await res.json();
}

async function viewProgress(clientId: number) {
  const res = await fetch(`/api/v1/clients/${clientId}/progress`);
  progress.value = await res.json();
  progressClientId.value = clientId;
}

onMounted(async () => {
  await Promise.all([fetchClients(), fetchSummary()]);
  loading.value = false;
});
</script>
