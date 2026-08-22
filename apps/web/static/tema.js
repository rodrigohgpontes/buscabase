(function () {
	try {
		if (localStorage.getItem('buscabase-tema') !== 'folia') return;
		document.documentElement.setAttribute('data-theme', 'folia');
		var meta = document.querySelector('meta[name="theme-color"]');
		if (meta) meta.setAttribute('content', '#0A6E38');
	} catch (e) {
		/* armazenamento indisponível */
	}
})();
