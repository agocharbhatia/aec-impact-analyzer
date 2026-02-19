<script lang="ts">
  import type { Discipline } from '$lib/types/contracts';

  export let value: Discipline | 'ALL' = 'ALL';
</script>

<label class="field-label" for="discipline-filter">Discipline filter</label>
<select id="discipline-filter" class="field-input max-w-xs" bind:value>
  <option value="ALL">All disciplines</option>
  <option value="ARCH">ARCH</option>
  <option value="MECH">MECH</option>
  <option value="ELEC">ELEC</option>
  <option value="PLUMB">PLUMB</option>
</select>
