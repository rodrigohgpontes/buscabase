<script lang="ts">
	import { OG_IMAGE_ALT, OG_IMAGE_HEIGHT, OG_IMAGE_WIDTH, socialPreview } from '$lib/social';

	let {
		title,
		description,
		url,
		image,
		noindex = false
	}: {
		title: string;
		description: string;
		url: string;
		image?: string;
		noindex?: boolean;
	} = $props();

	const preview = $derived(socialPreview({ title, description, url, image }));
</script>

<svelte:head>
	<meta property="og:title" content={preview.title} />
	<meta property="og:description" content={preview.description} />
	<meta property="og:url" content={preview.url} />
	<meta property="og:image" content={preview.image} />
	<meta property="og:image:width" content={String(OG_IMAGE_WIDTH)} />
	<meta property="og:image:height" content={String(OG_IMAGE_HEIGHT)} />
	<meta property="og:image:alt" content={OG_IMAGE_ALT} />
	<meta property="og:type" content={preview.type} />
	<meta property="og:locale" content={preview.locale} />
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:title" content={preview.title} />
	<meta name="twitter:description" content={preview.description} />
	<meta name="twitter:image" content={preview.image} />
	<meta name="twitter:image:alt" content={OG_IMAGE_ALT} />
	{#if noindex}
		<meta name="robots" content="noindex,nofollow" />
	{/if}
</svelte:head>
