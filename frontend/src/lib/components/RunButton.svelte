<script lang="ts">
  export let disabled = false;
  export let loading = false;
</script>

<button
  class="inline-flex items-center justify-center rounded-lg bg-ink px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
  disabled={disabled || loading}
  type="submit"
>
  {#if loading}
    Analyzing...
  {:else}
    Run Impact Analysis
  {/if}
</button>
