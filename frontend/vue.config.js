module.exports = {
  publicPath: "/static/", // Should match Django STATIC_URL
  filenameHashing: false,
  configureWebpack: config => {
    return {
      "output": {
        // filename: "js/[name].js", // No filename hashing, Django takes care of this
        // chunkFilename: "js/[id].js",
      },
      "devServer": {
        // writeToDisk: true, // Write files to disk in dev mode, so Django can serve the assets
      },
    }
  }
}
