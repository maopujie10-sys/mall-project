import { ref, onMounted, onUnmounted } from 'vue'

// 响应式窗口宽度
export function useWindowSize() {
  const width = ref(window.innerWidth)
  const height = ref(window.innerHeight)
  const isMobile = ref(window.innerWidth < 768)

  function onResize() {
    width.value = window.innerWidth
    height.value = window.innerHeight
    isMobile.value = window.innerWidth < 768
  }

  onMounted(() => window.addEventListener('resize', onResize))
  onUnmounted(() => window.removeEventListener('resize', onResize))

  return { width, height, isMobile }
}

// 倒计时
export function useCountdown(seconds = 60) {
  const count = ref(seconds)
  const isRunning = ref(false)
  let timer = null

  function start() {
    if (isRunning.value) return
    isRunning.value = true
    count.value = seconds
    timer = setInterval(() => {
      count.value--
      if (count.value <= 0) {
        stop()
      }
    }, 1000)
  }

  function stop() {
    isRunning.value = false
    clearInterval(timer)
    timer = null
    count.value = seconds
  }

  onUnmounted(() => clearInterval(timer))

  return { count, isRunning, start, stop }
}

// 图片懒加载
export function useImageLazyLoad() {
  function loadImage(el) {
    const src = el.getAttribute('data-src')
    if (!src) return
    el.src = src
    el.removeAttribute('data-src')
  }

  onMounted(() => {
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            loadImage(entry.target)
            observer.unobserve(entry.target)
          }
        })
      })
      document.querySelectorAll('img[data-src]').forEach(img => observer.observe(img))
    }
  })
}

// 列表加载更多
export function useLoadMore(fetchFn, pageSize = 20) {
  const list = ref([])
  const page = ref(1)
  const loading = ref(false)
  const finished = ref(false)
  const refreshing = ref(false)

  async function loadMore() {
    if (loading.value || finished.value) return
    loading.value = true
    try {
      const res = await fetchFn({ page: page.value, size: pageSize })
      const data = res.data || res
      const items = data.list || data.rows || data || []
      if (items.length < pageSize) finished.value = true
      list.value.push(...items)
      page.value++
    } finally {
      loading.value = false
    }
  }

  async function refresh() {
    refreshing.value = true
    page.value = 1
    list.value = []
    finished.value = false
    try {
      const res = await fetchFn({ page: 1, size: pageSize })
      const data = res.data || res
      const items = data.list || data.rows || data || []
      if (items.length < pageSize) finished.value = true
      list.value = items
      page.value = 2
    } finally {
      refreshing.value = false
    }
  }

  return { list, loading, finished, refreshing, loadMore, refresh }
}
