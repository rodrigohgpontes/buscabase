const CORES = ['#0a6e38', '#1d4ed8', '#fffdf6', '#e85d04'] as const;

type Peca = {
	x: number;
	y: number;
	vx: number;
	vy: number;
	r: number;
	spin: number;
	vspin: number;
	age: number;
	ttl: number;
	delay: number;
	flutter: number;
	phase: number;
	color: string;
};

export function prefersReducedMotion(): boolean {
	return (
		typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
	);
}

export function lancarRajada(canvas: HTMLCanvasElement, onDone: () => void): () => void {
	if (prefersReducedMotion()) {
		onDone();
		return () => {};
	}

	const ctx = canvas.getContext('2d', { alpha: true });
	if (!ctx) {
		onDone();
		return () => {};
	}

	let cancelled = false;
	let frame = 0;

	const fit = () => {
		const dpr = Math.min(2, window.devicePixelRatio || 1);
		const w = window.innerWidth;
		const h = window.innerHeight;
		canvas.width = Math.floor(w * dpr);
		canvas.height = Math.floor(h * dpr);
		canvas.style.width = `${w}px`;
		canvas.style.height = `${h}px`;
		ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
		return { w, h };
	};

	let { w, h } = fit();
	const gravity = h * 1.55;
	const drag = 0.28;
	const total = 320;
	const pecas: Peca[] = new Array(total);

	for (let i = 0; i < total; i++) {
		const left = i < total / 2;
		const speed = (2.15 + Math.random() * 0.55) * h;
		const deg = (left ? -78 : -102) + (Math.random() - 0.5) * 14;
		const rad = (deg * Math.PI) / 180;
		pecas[i] = {
			x: left ? Math.random() * 36 : w - Math.random() * 36,
			y: h - 6 + Math.random() * 18,
			vx: Math.cos(rad) * speed,
			vy: Math.sin(rad) * speed,
			r: 3 + Math.random() * 5.5,
			spin: Math.random() * Math.PI * 2,
			vspin: (Math.random() - 0.5) * 16,
			age: 0,
			ttl: 3.2 + Math.random() * 1.4,
			delay: Math.random() * 0.12,
			flutter: 6 + Math.random() * 11,
			phase: Math.random() * Math.PI * 2,
			color: CORES[i & 3]
		};
	}

	let last = performance.now();

	const tick = (now: number) => {
		if (cancelled) return;
		const dt = Math.min(0.033, (now - last) / 1000);
		last = now;
		ctx.clearRect(0, 0, w, h);
		const damp = Math.exp(-drag * dt);
		let alive = 0;

		for (const p of pecas) {
			p.age += dt;
			if (p.age < p.delay) {
				alive += 1;
				continue;
			}
			if (p.age - p.delay > p.ttl || p.y > h + 40) continue;
			alive += 1;
			p.vy += gravity * dt;
			p.vx *= damp;
			p.vy *= damp * 0.985;
			const t = p.age - p.delay;
			p.x += p.vx * dt + Math.sin(t * p.flutter + p.phase) * 22 * dt;
			p.y += p.vy * dt;
			p.spin += p.vspin * dt;

			const fade = Math.min(1, (p.ttl - t) / 0.65);
			const floor = p.vy > 0 && p.y > h * 0.88 ? 1 - (p.y - h * 0.88) / (h * 0.12 + 40) : 1;
			const alpha = Math.max(0, fade * Math.min(1, floor) * 0.9);
			if (alpha <= 0.01) continue;

			const squash = 0.28 + 0.72 * Math.abs(Math.cos(p.spin));
			ctx.globalAlpha = alpha;
			ctx.fillStyle = p.color;
			ctx.beginPath();
			ctx.ellipse(p.x, p.y, p.r, p.r * squash, 0, 0, Math.PI * 2);
			ctx.fill();
		}

		ctx.globalAlpha = 1;
		if (alive === 0) {
			ctx.clearRect(0, 0, w, h);
			onDone();
			return;
		}
		frame = requestAnimationFrame(tick);
	};

	frame = requestAnimationFrame(tick);

	return () => {
		cancelled = true;
		cancelAnimationFrame(frame);
		ctx.clearRect(0, 0, w, h);
	};
}
