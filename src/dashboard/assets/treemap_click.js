// A treemap tile zooms in when clicked, which would hide the other tiles and leave
// nothing to click. Returning false keeps the tiles in place, but it also stops
// plotly_click, so the clicked tile is handed to the dashboard here instead.
(function () {
  function keepTreemapStill() {
    var graph = document.querySelector("#ai-treemap .js-plotly-plot");
    if (graph && graph.on && !graph.dataset.noDrill) {
      graph.on("plotly_treemapclick", function (event) {
        var id = event.points[0].id;
        window.dash_clientside.set_props("ai-treemap", { clickData: { points: [{ id: id }] } });
        return false;
      });
      graph.dataset.noDrill = "true";
    }
  }
  new MutationObserver(keepTreemapStill).observe(document.documentElement, { childList: true, subtree: true });
})();
