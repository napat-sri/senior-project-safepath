import { reactive } from 'vue';

export const errorState = reactive({
  show: false,
  status: null,   // e.g. 404
  title: '',      // e.g. "Not Found"
  message: '',    // human-readable detail
});

export function showError({ status, title, message }) {
  errorState.status = status ?? null;
  errorState.title = title || 'Something went wrong';
  errorState.message = message || 'Please try again.';
  errorState.show = true;
}

export function clearError() {
  errorState.show = false;
}