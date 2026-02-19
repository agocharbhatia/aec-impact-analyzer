<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';

  import Filters from '$lib/components/Filters.svelte';
  import MiniViewport from '$lib/components/MiniViewport.svelte';
  import ReasonChain from '$lib/components/ReasonChain.svelte';
  import ResultsTable from '$lib/components/ResultsTable.svelte';
  import { getJob } from '$lib/api/client';
  import type { Discipline, ImpactedElement, JobResponse } from '$lib/types/contracts';

  let loading = true;
  let errorMessage = '';
  let job: JobResponse | null = null;
  let jobId = '';
  let disciplineFilter: Discipline | 'ALL' = 'ALL';
  let selectedImpactedId = '';

  $: jobId = $page.params.jobId ?? '';
  $: impactedRows = job?.result?.impactedElements ?? [];
  $: filteredRows =
    disciplineFilter === 'ALL'
      ? impactedRows
      : impactedRows.filter((item) => item.discipline === disciplineFilter);
  $: if (filteredRows.length > 0 && !filteredRows.some((item) => item.id === selectedImpactedId)) {
    selectedImpactedId = filteredRows[0].id;
  }
  $: selectedImpacted = filteredRows.find((item) => item.id === selectedImpactedId) as ImpactedElement | undefined;

  async function loadJob(): Promise<void> {
    loading = true;
    errorMessage = '';

    try {
      if (!jobId) {
        throw new Error('Missing job id in route.');
      }
      for (let attempt = 0; attempt < 5; attempt += 1) {
        const response = await getJob(jobId);
        job = response;
        if (response.status !== 'pending') {
          break;
        }
        await new Promise((resolve) => setTimeout(resolve, 250));
      }

      if (!job || job.status === 'pending') {
        errorMessage = 'Job is still pending. Refresh in a moment.';
      }
      if (job?.status === 'failed') {
        errorMessage = 'Analysis failed. Please rerun the analysis.';
      }
    } catch (error) {
      errorMessage = error instanceof Error ? error.message : 'Failed to load job.';
    } finally {
      loading = false;
    }
  }

  onMount(async () => {
    await loadJob();
  });
</script>

<section class="space-y-6">
  <header class="panel">
    <div class="flex items-center justify-between gap-3">
      <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Analysis result</p>
      <a
        class="inline-flex items-center rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold uppercase tracking-wide text-slate-700 transition hover:bg-slate-100"
        href="/"
      >
        Back to main page
      </a>
    </div>
    <h1 class="mt-2 text-2xl font-semibold text-ink">Job <span class="font-mono text-xl">{jobId}</span></h1>

    {#if job?.result}
      <div class="mt-4 grid gap-3 sm:grid-cols-3">
        <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
          <p class="text-xs uppercase tracking-wide text-slate-500">Total impacted</p>
          <p class="mt-1 text-2xl font-semibold text-ink">{job.result.summary.totalImpacted}</p>
        </div>
        <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
          <p class="text-xs uppercase tracking-wide text-slate-500">Max severity</p>
          <p class="mt-1 text-2xl font-semibold text-ink">{job.result.summary.maxSeverity.toFixed(2)}</p>
        </div>
        <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
          <p class="text-xs uppercase tracking-wide text-slate-500">Changed elements</p>
          <p class="mt-1 text-sm font-mono text-slate-700">{job.request.changeEvent.elementIds.join(', ')}</p>
        </div>
      </div>
    {/if}
  </header>

  {#if loading}
    <div class="panel text-sm text-slate-600">Loading job results...</div>
  {:else if errorMessage}
    <div class="panel border border-red-200 bg-red-50 text-sm text-red-700">{errorMessage}</div>
  {:else if job && job.result}
    <section class="grid gap-6 xl:grid-cols-[1.2fr,0.8fr]">
      <div class="space-y-4">
        <div class="panel">
          <Filters bind:value={disciplineFilter} />
          <div class="mt-4">
            <ResultsTable rows={filteredRows} bind:selectedId={selectedImpactedId} on:select={(event) => (selectedImpactedId = event.detail)} />
          </div>
        </div>

        <MiniViewport
          elements={job.request.resolvedModel.elements}
          changedIds={job.request.changeEvent.elementIds}
          impactedIds={filteredRows.map((item) => item.id)}
          changeEvent={job.request.changeEvent}
          {selectedImpactedId}
        />
      </div>

      <ReasonChain impacted={selectedImpacted ?? null} />
    </section>
  {/if}
</section>
