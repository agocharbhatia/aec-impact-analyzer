<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  import ChangeEventSelector from '$lib/components/ChangeEventSelector.svelte';
  import DatasetSelector from '$lib/components/DatasetSelector.svelte';
  import RunButton from '$lib/components/RunButton.svelte';
  import { getDatasets, getPresets, submitAnalyze } from '$lib/api/client';
  import type { ChangePreset, DatasetOption } from '$lib/types/contracts';

  let datasets: DatasetOption[] = [];
  let presets: ChangePreset[] = [];
  let selectedDatasetId = '';
  let selectedPresetId = '';
  let loading = false;
  let catalogLoading = true;
  let errorMessage = '';

  $: if (!selectedDatasetId && datasets.length > 0) {
    selectedDatasetId = datasets[0].id;
  }
  $: filteredPresets = presets.filter((preset) => preset.datasetId === selectedDatasetId);
  $: if (!filteredPresets.some((preset) => preset.id === selectedPresetId)) {
    selectedPresetId = filteredPresets[0]?.id ?? '';
  }
  $: selectedPreset = filteredPresets.find((preset) => preset.id === selectedPresetId) as ChangePreset | undefined;

  async function loadCatalog(): Promise<void> {
    catalogLoading = true;
    errorMessage = '';
    try {
      const [datasetOptions, presetOptions] = await Promise.all([getDatasets(), getPresets()]);
      datasets = datasetOptions;
      presets = presetOptions;
      if (datasetOptions.length === 0) {
        throw new Error('No datasets available from API.');
      }
      selectedDatasetId = datasetOptions[0].id;
    } catch (error) {
      errorMessage = error instanceof Error ? error.message : 'Failed to load datasets and presets.';
    } finally {
      catalogLoading = false;
    }
  }

  async function onSubmit(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    if (!selectedPreset || !selectedDatasetId || loading || catalogLoading) {
      return;
    }

    loading = true;
    errorMessage = '';

    try {
      const response = await submitAnalyze({
        datasetId: selectedDatasetId,
        changeEvent: selectedPreset.changeEvent
      });
      await goto(`/results/${response.jobId}`);
    } catch (error) {
      errorMessage = error instanceof Error ? error.message : 'Unexpected analysis error.';
    } finally {
      loading = false;
    }
  }

  onMount(async () => {
    await loadCatalog();
  });
</script>

<section class="grid gap-6 lg:grid-cols-[1.1fr,0.9fr]">
  <div class="panel">
    <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Structured QA/QC Demo</p>
    <h1 class="mt-2 text-3xl font-semibold text-ink">Cross Discipline Impact Analyzer</h1>
    <p class="mt-3 max-w-2xl text-sm text-slate-600">
      Simulate how one discipline change propagates across ARCH/MECH/ELEC/PLUMB using graph traversal,
      geometric tolerances, and connector dependencies.
    </p>

    <form class="mt-6 grid gap-5" on:submit={onSubmit}>
      {#if catalogLoading}
        <p class="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600">
          Loading datasets and change presets...
        </p>
      {:else}
        <DatasetSelector {datasets} bind:value={selectedDatasetId} />
        <ChangeEventSelector presets={filteredPresets} bind:value={selectedPresetId} />
      {/if}

      {#if selectedPreset}
        <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
          <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Selected change payload</p>
          <pre class="mt-2 overflow-x-auto text-xs text-slate-700">{JSON.stringify(selectedPreset.changeEvent, null, 2)}</pre>
        </div>
      {/if}

      <div class="flex items-center gap-3">
        <RunButton loading={loading} disabled={!selectedPreset || catalogLoading} />
        <span class="text-xs text-slate-500">Expected runtime: &lt; 1 second (local)</span>
      </div>

      {#if errorMessage}
        <p class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{errorMessage}</p>
      {/if}
    </form>
  </div>

  <aside class="panel">
    <h2 class="text-lg font-semibold text-ink">Demo checklist</h2>
    <ol class="mt-3 list-decimal space-y-2 pl-4 text-sm text-slate-600">
      <li>Select dataset and preset.</li>
      <li>Run analysis and open results page.</li>
      <li>Show ranked impacts + discipline filter.</li>
      <li>Open a row to inspect rule reason chains.</li>
      <li>Use viewport to compare changed vs impacted geometry.</li>
    </ol>
  </aside>
</section>
