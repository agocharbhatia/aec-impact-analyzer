<script lang="ts">
  import type { DatasetOption } from '$lib/types/contracts';

  export let datasets: DatasetOption[] = [];
  export let value = '';

  $: selectedDataset = datasets.find((item) => item.id === value);
</script>

<label class="field-label" for="dataset-select">Project dataset</label>
<select id="dataset-select" class="field-input" bind:value>
  {#each datasets as dataset}
    <option value={dataset.id}>{dataset.label}</option>
  {/each}
</select>
{#if selectedDataset}
  <p class="mt-2 text-xs text-slate-600">{selectedDataset.description}</p>
{/if}
