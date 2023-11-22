import { defineConfig } from "vite";


import litestar from "litestar-vite-plugin";

export default defineConfig({
  plugins: [


    litestar({
      input: [
        "resources/styles.css"
      ],
      assetUrl: "/static/",
      assetDirectory: "resources/assets",
      bundleDirectory: "public",
      resourceDirectory: "resources"
    }),
  ],
  resolve: {
    alias: {
      "@": "resources",
    },
  },
});
