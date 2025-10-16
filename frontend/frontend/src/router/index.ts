import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import Profile from '../views/Profile.vue';
import Subscriptions from '../views/Subscriptions.vue';
import Calendar from '../views/Calendar.vue';
import Macros from '../views/Macros.vue';
import Chatbot from '../views/Chatbot.vue';
import TrainerDashboard from '../views/TrainerDashboard.vue';

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/profile', name: 'Profile', component: Profile },
  { path: '/subscriptions', name: 'Subscriptions', component: Subscriptions },
  { path: '/calendar', name: 'Calendar', component: Calendar },
  { path: '/macros', name: 'Macros', component: Macros },
  { path: '/chatbot', name: 'Chatbot', component: Chatbot },
  { path: '/trainer-dashboard', name: 'TrainerDashboard', component: TrainerDashboard },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
