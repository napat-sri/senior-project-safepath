module.exports = {
  devServer: {
    allowedHosts: 'all', // Allows the dev server to accept traffic from Caddy

    // Reached over the VPN by IP (http://172.28.0.20:8080), webpack's
    // hot-reload WebSocket can't negotiate the host and puts the page into a
    // constant-refresh loop. Pin the client WebSocket to the page's own
    // host/port so it connects back correctly.
    client: {
      webSocketURL: 'auto://0.0.0.0:0/ws',
    },
    proxy: {
    '/langflow': {
      target: 'http://langflow:7860', // reachable once frontend joins langflow-net (change 3)
      changeOrigin: true,
      pathRewrite: { '^/langflow': '' },
    },
  },

    // If the refresh loop persists, uncomment these to disable live reload
    // entirely (fine for a deployed/demo build; flip back on for local dev):
    // hot: false,
    // liveReload: false,
  }
}