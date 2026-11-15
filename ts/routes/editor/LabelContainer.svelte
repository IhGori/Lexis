<!--
Copyright: Anki Software, LLC and contributors
License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
-->
<script lang="ts">
    import * as tr from "@generated/ftl";

    import CollapseLabel from "./CollapseLabel.svelte";

    export let collapsed: boolean;

    $: tooltip = collapsed ? tr.editingExpandField() : tr.editingCollapseField();
</script>

<div class="label-container">
    <CollapseLabel {collapsed} {tooltip} on:toggle>
        <slot name="field-name" />
    </CollapseLabel>
    <slot />
</div>

<style lang="scss">
    .label-container {
        display: flex;
        justify-content: space-between;
        background: var(--canvas);
        border-top-right-radius: calc(var(--border-radius-medium) * 1.3);
        border-top-left-radius: calc(var(--border-radius-medium) * 1.3);
        padding: 2px 4px 3px;
        font-weight: 600;
        color: var(--fg-subtle);

        position: sticky;
        top: 0;
        z-index: 50;
    }
</style>
