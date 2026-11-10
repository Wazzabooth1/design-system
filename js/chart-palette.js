/* Chart colours for any charting library, read live from the design tokens so they follow
   light/dark. Usage: const c = dsChart(); c.series[0], c.grid, c.axis, c.text, c.surface.
   Assign series by entity in a fixed order; never re-sort colours when a filter hides a series.
   Light-mode amber/aqua/pink sit under 3:1 on white, so always pair charts with direct labels
   or a table view. */
(function () {
  window.dsChart = function () {
    var cs = getComputedStyle(document.documentElement);
    var v = function (n) { return cs.getPropertyValue(n).trim(); };
    return {
      series: [1, 2, 3, 4, 5, 6].map(function (i) { return v('--chart-' + i); }),
      grid: v('--chart-grid'), axis: v('--chart-axis'),
      text: v('--text'), muted: v('--muted'), surface: v('--surface'), accent: v('--accent'),
      ok: v('--ok'), warn: v('--warn'), bad: v('--bad'), info: v('--info')
    };
  };
})();
