import { fileURLToPath, URL } from 'node:url'

import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      resolvers: [ElementPlusResolver()],
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },

  // 配置代理，对接后端接口
  server: {
    port: 8173,
    host: 'localhost',
    proxy: {
      // 匹配所有以 /api 开头的请求
      '/api': {
        target: 'http://127.0.0.1:8000/api',  // 后端接口地址
        changeOrigin: true,  // 允许跨域
        rewrite: (path) => path.replace(/^\/api/, ''),  //重写路径
      }
    }
  }
})
