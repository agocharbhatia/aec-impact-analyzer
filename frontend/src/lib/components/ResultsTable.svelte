<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  import type { ImpactedElement } from '$lib/types/contracts';

  export let rows: ImpactedElement[] = [];
  export let selectedId = '';

  const dispatch = createEventDispatcher<{ select: string }>();

  function pick(id: string): void {
    dispatch('select', id);
  }
</script>

<div class="overflow-hidden rounded-xl border border-slate-200">
  <table class="min-w-full divide-y divide-slate-200 text-sm">
    <thead class="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">
      <tr>
        <th class="px-3 py-3">Element</th>
        <th class="px-3 py-3">Discipline</th>
        <th class="px-3 py-3">Category</th>
        <th class="px-3 py-3">Severity</th>
        <th class="px-3 py-3">Reasons</th>
      </tr>
    </thead>
    <tbody class="divide-y divide-slate-100 bg-white">
      {#if rows.length === 0}
        <tr>
          <td class="px-3 py-4 text-slate-500" colspan="5">No impacted elements for this filter.</td>
        </tr>
      {:else}
        {#each rows as row}
          <tr
            class={`cursor-pointer transition hover:bg-slate-50 ${selectedId === row.id ? 'bg-orange-50' : ''}`}
            on:click={() => pick(row.id)}
          >
            <td class="px-3 py-3 font-mono text-xs">{row.id}</td>
            <td class="px-3 py-3">{row.discipline}</td>
            <td class="px-3 py-3">{row.category}</td>
            <td class="px-3 py-3 font-semibold">{row.severity.toFixed(2)}</td>
            <td class="px-3 py-3">{row.reasons.length}</td>
          </tr>
        {/each}
      {/if}
    </tbody>
  </table>
</div>
