<template>
  <div class="show-pdf">
    <div class="tools">
      <el-button type="submit" @click.stop="prePage" class="mr10">
        {{ $t('上一页') }}
      </el-button>
      <el-button type="submit" @click.stop="nextPage" class="mr10">
        {{ $t('下一页') }}
      </el-button>
      <div class="page">{{ pageNum }}/{{ pageTotalNum }}</div>
      <el-button type="submit" @click.stop="pdfPrintAll" class="mr10">
        {{ $t('打印') }}
      </el-button>
      <el-button type="submit" @click.stop="downloadPDF" class="mr10">
        {{ $t('下载') }}
      </el-button>
    </div>
    <div class="pdf" ref="pdfView">
      <pdf ref="pdf"
           :style="{width: width + 'px'}"
           :src="url"
           :page="pageNum"
           :rotate="pageRotate"
           @progress="loadedRatio = $event"
           @page-loaded="pageLoaded($event)"
           @num-pages="pageTotalNum=$event"
           @error="pdfError($event)"
           @link-clicked="page = $event">
      </pdf>
    </div>
    <div class="close" @click="closePdf">
      <i class="el-icon-close" style="font-size: 36px;"></i>
    </div>
  </div>
</template>

<script>
import pdf from 'vue-pdf'
import {mapGetters} from "vuex";

export default {
  name: 'Home',
  components: {
    pdf
  },
  data() {
    return {
      url: "",
      pageNum: 1,
      pageTotalNum: 1,
      pageRotate: 0,
      // 加载进度
      loadedRatio: 0,
      curPageNum: 0,
      width: 0,
    }
  },
  computed: {
    ...mapGetters(['userInfo']),
  },
  mounted() {
    this.url = this.userInfo.signPdfUrl
    this.$nextTick(() => {
      // const windowHeight = this.$refs.pdfView.clientHeight; // 获取窗口的可视区域高度
      // this.width = windowHeight * (210 / 297); // 根据 A4 比例计算宽度
      this.width = this.$refs.pdfView.clientWidth
    })
  },
  methods: {
    closePdf() {
      this.$emit('closePdf')
    },
    // 打印全部
    pdfPrintAll() {
      this.$refs.pdf.print()
    },
    // 上一页函数，
    prePage() {
      let page = this.pageNum
      page = page > 1 ? page - 1 : this.pageTotalNum
      this.pageNum = page
    },
    // 下一页函数
    nextPage() {
      let page = this.pageNum
      page = page < this.pageTotalNum ? page + 1 : 1
      this.pageNum = page
    },
    // 页面顺时针翻转90度。
    clock() {
      this.pageRotate += 90
    },
    // 页面逆时针翻转90度。
    counterClock() {
      this.pageRotate -= 90
    },
    // 页面加载回调函数，其中e为当前页数
    pageLoaded(e) {
      this.curPageNum = e
    },
    // 其他的一些回调函数。
    pdfError(error) {
      console.error(error)
    },
    downloadPDF() {
      fetch(this.url)
          .then(response => response.blob())
          .then(blob => {
            // 创建临时URL
            const blobUrl = URL.createObjectURL(blob);

            // 创建一个<a>标签并设置其属性
            const link = document.createElement('a');
            link.href = blobUrl;
            link.download = this.$t('电子合同') + '.pdf';

            // 模拟点击下载链接
            link.click();

            // 清理临时URL
            URL.revokeObjectURL(blobUrl);
          })
          .catch(error => {
            // 处理错误
          });
    }

  }
}
</script>
<style lang="scss">
//当前组件设置成全屏弹窗
.show-pdf {
  width: 100%;
  height: 100%;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000000;
  overflow: hidden;

  &::after {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
  }

  .tools {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 50px;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000001;
    color: #FFFFFF;

    .page {
      margin: 0 20px;
    }
  }

  .pdf {
    width: 100%;
    height: calc(100vh - 50px);
    position: relative;
    z-index: 1000001;
    top: 0;
    left: 0;
    overflow-y: auto;
    padding: 0;
    display: flex;
    justify-content: center;
  }

  .close {
    position: absolute;
    top: 12px;
    right: 12px;
    width: 50px;
    height: 50px;
    cursor: pointer;
    z-index: 1000002;
    background-color: rgba(0, 0, 0, 0.1);
    color: #FFFFFF;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 50%;

    &:hover {
      background-color: rgba(0, 0, 0, 0.3);
    }
  }
}

</style>
