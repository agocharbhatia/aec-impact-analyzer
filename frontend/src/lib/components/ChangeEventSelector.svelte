<script lang="ts">
  import type { ChangePreset } from '$lib/types/contracts';

  export let presets: ChangePreset[] = [];
  export let value = '';

  $: activePreset = presets.find((item) => item.id === value);
</script>

<label class="field-label" for="change-select">Change event preset</label>
<select id="change-select" class="field-input" bind:value>
  {#each presets as preset}
    <option value={preset.id}>{preset.label}</option>
  {/each}
</select>
{#if activePreset}
  <p class="mt-2 text-xs text-slate-600">{activePreset.description}</p>
{/if}
