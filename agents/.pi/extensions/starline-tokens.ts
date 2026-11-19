/**
 * starline-tokens — the context token count for the Starline pill bar.
 *
 * Starline (npm:pi-starline) has no tokens pill of its own: the old `tokens`
 * segment merged into `context`, which shows only the percentage. This
 * extension publishes the number of tokens currently filling the context
 * window as the `tokens` status; starline.base.json places it between
 * `context` and `cost` as `extensionStatus:tokens` and colours it from
 * `extensionStatuses.colors.tokens`, so it follows the same RGB palette.
 *
 * Pi auto-discovers this file from ~/.pi/agent/extensions/; install.sh copies
 * it there from the tracked base. Hot-reload with /reload.
 */
import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";

const STATUS_KEY = "tokens";

/** Same shape as Starline's own counts: 950, 1.2k, 45k, 1.2M. */
function formatCount(value: number): string {
	if (value < 1000) return value.toString();
	if (value < 10_000) return `${(value / 1000).toFixed(1)}k`;
	if (value < 1_000_000) return `${Math.round(value / 1000)}k`;
	if (value < 10_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
	return `${Math.round(value / 1_000_000)}M`;
}

export default function (pi: ExtensionAPI) {
	let last: string | undefined;

	const publish = (ctx: ExtensionContext) => {
		const usage = ctx.getContextUsage();
		// tokens is null right after compaction, before the next response is
		// measured: hide the pill rather than show a stale number.
		const text = usage && usage.tokens !== null ? formatCount(usage.tokens) : undefined;
		if (text === last) return;
		last = text;
		ctx.ui.setStatus(STATUS_KEY, text);
	};

	pi.on("session_start", async (_event, ctx) => publish(ctx));
	pi.on("turn_end", async (_event, ctx) => publish(ctx));
	pi.on("message_end", async (_event, ctx) => publish(ctx));
	pi.on("session_compact", async (_event, ctx) => publish(ctx));
	pi.on("model_select", async (_event, ctx) => publish(ctx));
	pi.on("session_shutdown", async (_event, ctx) => {
		last = undefined;
		ctx.ui.setStatus(STATUS_KEY, undefined);
	});
}
