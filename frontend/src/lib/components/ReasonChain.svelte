<script lang="ts">
  import type { ImpactedElement } from '$lib/types/contracts';

  export let impacted: ImpactedElement | null = null;
</script>

<div class="panel">
  <h3 class="text-sm font-semibold uppercase tracking-wide text-slate-600">Reason chain</h3>

  {#if !impacted}
    <p class="mt-3 text-sm text-slate-500">Select an impacted element to inspect why it was flagged.</p>
  {:else}
    <p class="mt-3 text-sm text-slate-700">
      <span class="font-mono text-xs">{impacted.id}</span>
      <span class="mx-1">•</span>
      <span>{impacted.discipline}</span>
      <span class="mx-1">•</span>
      <span>Severity {impacted.severity.toFixed(2)}</span>
    </p>

    <ul class="mt-4 space-y-3">
      {#each impacted.reasons as reason}
        <li class="rounded-lg border border-slate-200 p-3">
          <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">{reason.ruleId}</p>
          <p class="mt-1 text-sm text-slate-700">{reason.description}</p>
          <p class="mt-2 text-xs text-slate-500">
            Path:
            <span class="font-mono">{reason.pathElementIds.join(' -> ')}</span>
          </p>
        </li>
      {/each}
    </ul>
  {/if}
</div>
